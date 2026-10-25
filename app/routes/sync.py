"""
Universal Expense Sync routes and REST API.
Handles bank connections, Account Aggregator consent, manual statement imports,
receipt matching, transaction review queue, and synchronization audits.
"""
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, g, flash, redirect, url_for
from app.extensions import db, csrf
from app.routes.auth import login_required
from app.models.category import Category
from app.models.sync import (
    FinancialConnection,
    SyncedTransaction,
    MerchantCategoryPreference,
    SyncAuditLog,
    ReceiptRecord
)
from app.services.sync.sync_engine import SyncEngine
from app.services.sync.aa_client import AccountAggregatorClient, SUPPORTED_FIPS
from app.services.sync.bank_directory import BankDirectoryService
from app.services.sync.statement_parser import StatementParser
from app.services.sync.receipt_parser import ReceiptParser
from app.services.money import format_money

logger = logging.getLogger(__name__)
sync_bp = Blueprint('sync', __name__)


@sync_bp.route('/sync')
@login_required
def view_sync():
    """Render Universal Expense Sync main dashboard."""
    user = g.current_user
    overview = SyncEngine.get_sync_overview(user.id)
    connections = FinancialConnection.query.filter_by(user_id=user.id).all()
    categories = Category.query.filter(
        (Category.user_id == user.id) | (Category.user_id.is_(None)),
        Category.is_active.is_(True)
    ).order_by(Category.name.asc()).all()

    aa_client = AccountAggregatorClient()
    provider_status = aa_client.get_provider_status()
    all_institutions = BankDirectoryService.get_directory()
    last_refreshed_at = BankDirectoryService.get_last_refreshed_at()

    return render_template(
        'sync.html',
        user=user,
        overview=overview,
        connections=connections,
        categories=categories,
        supported_fips=all_institutions,
        provider_status=provider_status,
        last_refreshed_at=last_refreshed_at.isoformat() if last_refreshed_at else None
    )


@sync_bp.route('/api/sync/overview', methods=['GET'])
@login_required
def api_get_overview():
    """Get high-level synchronization metrics."""
    user = g.current_user
    overview = SyncEngine.get_sync_overview(user.id)
    return jsonify({'success': True, 'overview': overview})


@sync_bp.route('/api/sync/institutions', methods=['GET'])
@login_required
def api_get_institutions():
    """
    Dynamic discovery endpoint: Returns verified Indian institutions with honest availability statuses.
    Supports query search and category filtering.
    """
    user = g.current_user
    query = request.args.get('q', '').strip()
    category = request.args.get('category', 'ALL').strip().upper()

    aa_client = AccountAggregatorClient()
    is_configured = aa_client.is_configured()
    is_sandbox = not aa_client.is_production()

    # Get codes of already connected accounts for this user
    active_conns = FinancialConnection.query.filter_by(
        user_id=user.id,
        status='CONNECTED'
    ).all()
    connected_codes = [c.institution_code for c in active_conns]

    institutions = BankDirectoryService.search_and_filter(
        search_query=query,
        category=category,
        user_connected_codes=connected_codes,
        is_provider_ready=is_configured,
        is_sandbox_simulation=is_sandbox and not is_configured
    )

    last_refreshed = BankDirectoryService.get_last_refreshed_at()
    return jsonify({
        'success': True,
        'institutions': institutions,
        'total_count': len(institutions),
        'last_refreshed_at': last_refreshed.isoformat() if last_refreshed else None,
        'provider_status': aa_client.get_provider_status()
    })


@sync_bp.route('/api/sync/institutions/refresh', methods=['POST'])
@login_required
def api_refresh_institutions():
    """Force directory cache refresh and health probe."""
    directory = BankDirectoryService.get_directory(force_refresh=True)
    aa_client = AccountAggregatorClient()
    health = aa_client.check_provider_health()
    last_refreshed = BankDirectoryService.get_last_refreshed_at()

    return jsonify({
        'success': True,
        'message': f"Successfully refreshed directory: {len(directory)} institutions available.",
        'total_count': len(directory),
        'last_refreshed_at': last_refreshed.isoformat() if last_refreshed else None,
        'health': health
    })


@sync_bp.route('/api/sync/connections', methods=['GET'])
@login_required
def api_get_connections():
    """List all financial connections for current user."""
    user = g.current_user
    connections = FinancialConnection.query.filter_by(user_id=user.id).order_by(FinancialConnection.created_at.desc()).all()
    return jsonify({
        'success': True,
        'connections': [c.to_dict() for c in connections],
        'supported_fips': BankDirectoryService.get_directory()
    })


@sync_bp.route('/api/sync/connections', methods=['POST'])
@login_required
def api_connect_institution():
    """
    Initiate Account Aggregator connection. Supports multiple accounts and institutions.
    In live mode: redirects user to Setu consent portal with OTP.
    In sandbox mode: activates simulated Indian banking feed.
    """
    user = g.current_user
    data = request.get_json() or {}

    fip_code = data.get('fip_code', 'SBIN').upper()
    phone = data.get('phone') or user.phone_number or '9876543210'
    account_types = data.get('account_types') or ['SAVINGS']
    account_name = data.get('account_name')
    target_mask = data.get('account_mask')

    selected_fip = BankDirectoryService.find_institution_by_code(fip_code)
    if not selected_fip:
        return jsonify({'success': False, 'error': f"Unknown institution code '{fip_code}'."}), 400

    # Prevent connecting duplicate exact account
    existing_query = FinancialConnection.query.filter_by(
        user_id=user.id,
        institution_code=fip_code,
        status='CONNECTED'
    )
    if target_mask:
        existing_query = existing_query.filter_by(account_mask=target_mask)

    # If the user already has this specific account connected:
    existing = existing_query.first()
    if existing and not data.get('allow_additional_account', False):
        return jsonify({
            'success': False,
            'error': f"{selected_fip['name']} ({existing.account_mask}) is already connected. You can sync or manage it in Connected Accounts."
        }), 400

    aa_client = AccountAggregatorClient()
    callback_url = url_for('sync.consent_callback', _external=True)

    consent_res = aa_client.create_consent_request(
        user_phone=phone,
        fip_code=fip_code,
        account_types=account_types,
        redirect_url=callback_url
    )

    if not consent_res.get('success'):
        error_msg = consent_res.get('message') or consent_res.get('error') or 'Failed to initiate consent.'
        status_code = 400 if consent_res.get('error') == 'PROVIDER_SETUP_REQUIRED' else 500
        return jsonify({
            'success': False,
            'error': error_msg,
            'setup_required': consent_res.get('error') == 'PROVIDER_SETUP_REQUIRED',
            'mode': consent_res.get('mode')
        }), status_code

    mode = consent_res.get('mode', 'SANDBOX_SIMULATION')
    is_live = mode == 'LIVE_API'

    # Register Financial Connection record (prefer target_mask if provided)
    account_mask = target_mask or consent_res.get('account_mask') or '•••• 4821'
    new_conn = FinancialConnection(
        user_id=user.id,
        institution_name=selected_fip['name'],
        institution_code=fip_code,
        account_mask=account_mask,
        account_reference=consent_res.get('account_reference'),
        account_name=account_name or f"{selected_fip['name']} {account_types[0].capitalize()}",
        account_type=account_types[0] if account_types else 'SAVINGS',
        provider='ACCOUNT_AGGREGATOR',
        consent_id=consent_res.get('consent_id'),
        consent_status='PENDING' if is_live else 'ACTIVE',
        status='PENDING' if is_live else 'CONNECTED',
        is_demo=bool(consent_res.get('is_demo', False))
    )
    db.session.add(new_conn)
    db.session.commit()

    # If Live API: Return redirect URL to frontend for user to authenticate via Setu webview OTP
    if is_live:
        return jsonify({
            'success': True,
            'mode': 'LIVE_API',
            'redirect_url': consent_res.get('url'),
            'consent_id': consent_res.get('consent_id'),
            'connection_id': new_conn.id,
            'message': f"Consent request created for {selected_fip['name']}. Redirecting to authorization webview..."
        }), 201

    # In Sandbox Simulation Mode: Perform instant initial sync
    sync_res = SyncEngine.sync_connection(user.id, new_conn.id, sync_type='INITIAL_SYNC')

    return jsonify({
        'success': True,
        'mode': 'SANDBOX_SIMULATION',
        'message': f"Successfully linked {selected_fip['name']} via Account Aggregator.",
        'connection': new_conn.to_dict(),
        'sync_result': sync_res
    }), 201


@sync_bp.route('/sync/callback')
@login_required
def consent_callback():
    """
    Handle return redirect from Setu Account Aggregator webview.
    Query parameters: consent_id, status (SUCCESS, FAILED, CANCELLED)
    """
    user = g.current_user
    consent_id = request.args.get('consent_id')
    status_param = request.args.get('status', '').upper()

    if not consent_id:
        flash("Consent authorization failed: Missing consent token.", "error")
        return redirect(url_for('sync.view_sync'))

    conn = FinancialConnection.query.filter_by(user_id=user.id, consent_id=consent_id).first()
    if not conn:
        flash("Financial connection record not found for this authorization.", "error")
        return redirect(url_for('sync.view_sync'))

    # If status explicitly indicates cancellation, denial, or failure
    if status_param in ('CANCELLED', 'FAILED', 'REJECTED', 'DENIED'):
        conn.status = 'ERROR'
        conn.consent_status = 'REJECTED'
        conn.error_message = f'Consent authorization was {status_param.lower()} by user.'
        db.session.commit()
        flash(f"Consent authorization for {conn.institution_name} was {status_param.lower()}.", "error")
        return redirect(url_for('sync.view_sync'))

    aa_client = AccountAggregatorClient()
    auth_check = aa_client.complete_authorization(consent_id)

    if auth_check.get('success') or status_param == 'SUCCESS':
        conn.status = 'CONNECTED'
        conn.consent_status = 'ACTIVE'
        conn.error_message = ''
        db.session.commit()

        # Trigger immediate initial transaction sync
        SyncEngine.sync_connection(user.id, conn.id, sync_type='INITIAL_SYNC')
        flash(f"Successfully authorized and connected {conn.institution_name}!", "success")
    else:
        conn.status = 'ERROR'
        conn.consent_status = 'REJECTED'
        conn.error_message = 'Consent authorization was cancelled or rejected by user.'
        db.session.commit()
        flash(f"Consent authorization for {conn.institution_name} was denied or expired.", "error")

    return redirect(url_for('sync.view_sync'))


@sync_bp.route('/api/sync/consents/<consent_id>/check', methods=['POST'])
@login_required
def api_check_consent_status(consent_id):
    """Poll consent status from provider for active webviews."""
    user = g.current_user
    conn = FinancialConnection.query.filter_by(user_id=user.id, consent_id=consent_id).first()
    if not conn:
        return jsonify({'success': False, 'error': 'Connection not found.'}), 404

    aa_client = AccountAggregatorClient()
    status_res = aa_client.get_consent_status(consent_id)
    is_active = status_res.get('is_active', False)

    if is_active and conn.status != 'CONNECTED':
        conn.status = 'CONNECTED'
        conn.consent_status = 'ACTIVE'
        conn.error_message = ''
        db.session.commit()
        SyncEngine.sync_connection(user.id, conn.id, sync_type='INITIAL_SYNC')

    return jsonify({
        'success': True,
        'consent_id': consent_id,
        'status': status_res.get('status'),
        'is_active': is_active,
        'connection': conn.to_dict()
    })


@sync_bp.route('/api/sync/webhook', methods=['POST'])
@csrf.exempt
def api_provider_webhook():
    """
    Setu Account Aggregator Webhook handler for async notifications.
    Supports CONSENT_STATUS_UPDATE and FI_NOTIFICATION.
    """
    payload = request.get_json(silent=True) or {}
    event_type = payload.get('type') or payload.get('event')
    consent_id = payload.get('consentId') or payload.get('consent_id')

    logger.info(f"Received Setu AA Webhook event: {event_type} for consent {consent_id}")

    if consent_id:
        conn = FinancialConnection.query.filter_by(consent_id=consent_id).first()
        if conn:
            new_status = payload.get('status', '').upper()
            if new_status == 'ACTIVE':
                conn.status = 'CONNECTED'
                conn.consent_status = 'ACTIVE'
                db.session.commit()
                SyncEngine.sync_connection(conn.user_id, conn.id, sync_type='AUTOMATIC_WEBHOOK')
            elif new_status in ('REVOKED', 'EXPIRED'):
                conn.status = 'DISCONNECTED'
                conn.consent_status = new_status
                db.session.commit()

    return jsonify({'success': True, 'acknowledged': True}), 200



@sync_bp.route('/api/sync/connections/<int:conn_id>/sync', methods=['POST'])
@login_required
def api_sync_connection(conn_id):
    """Trigger Sync Now for a single institution."""
    user = g.current_user
    res = SyncEngine.sync_connection(user.id, conn_id, sync_type='MANUAL_SYNC_NOW')
    if not res.get('success'):
        return jsonify(res), 400
    return jsonify(res)


@sync_bp.route('/api/sync/all/sync', methods=['POST'])
@login_required
def api_sync_all():
    """Trigger Sync Now across all connected institutions."""
    user = g.current_user
    res = SyncEngine.sync_all_connections(user.id)
    if not res.get('success'):
        return jsonify(res), 400
    return jsonify(res)


@sync_bp.route('/api/sync/connections/<int:conn_id>', methods=['DELETE'])
@login_required
def api_disconnect_connection(conn_id):
    """Disconnect institution and revoke consent."""
    user = g.current_user
    delete_data = request.args.get('delete_data', 'false').lower() == 'true'
    res = SyncEngine.disconnect_connection(user.id, conn_id, delete_data=delete_data)
    if not res.get('success'):
        return jsonify(res), 400
    return jsonify(res)


@sync_bp.route('/api/sync/transactions', methods=['GET'])
@login_required
def api_get_synced_transactions():
    """List synced transactions with search, pagination, and review status filtering."""
    user = g.current_user
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status = request.args.get('status')  # PENDING_REVIEW, APPROVED, POTENTIAL_DUPLICATE, REJECTED
    search = request.args.get('search', '').strip()

    query = SyncedTransaction.query.filter_by(user_id=user.id)

    if status and status.upper() != 'ALL':
        query = query.filter_by(review_status=status.upper())

    if search:
        term = f"%{search}%"
        query = query.filter(
            (SyncedTransaction.normalized_merchant.ilike(term)) |
            (SyncedTransaction.raw_narration.ilike(term)) |
            (SyncedTransaction.external_id.ilike(term))
        )

    query = query.order_by(SyncedTransaction.raw_date.desc(), SyncedTransaction.id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    records = []
    for t in pagination.items:
        data = t.to_dict()
        data['formatted_amount'] = format_money(t.amount_minor_units, user.currency)
        records.append(data)

    return jsonify({
        'success': True,
        'transactions': records,
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@sync_bp.route('/api/sync/transactions/<int:txn_id>/approve', methods=['POST'])
@login_required
def api_approve_transaction(txn_id):
    """Approve a synced transaction, saving optional category and user preference."""
    user = g.current_user
    data = request.get_json() or {}

    category_id = data.get('category_id')
    save_preference = bool(data.get('save_preference', False))

    res = SyncEngine.approve_transaction(
        user_id=user.id,
        synced_txn_id=txn_id,
        category_id=category_id,
        save_preference=save_preference
    )
    if not res.get('success'):
        return jsonify(res), 400
    return jsonify(res)


@sync_bp.route('/api/sync/transactions/<int:txn_id>/link', methods=['POST'])
@login_required
def api_link_transaction(txn_id):
    """Link a potential duplicate synced transaction to an existing ledger entry."""
    user = g.current_user
    data = request.get_json() or {}
    existing_txn_id = data.get('existing_txn_id')

    if not existing_txn_id:
        return jsonify({'success': False, 'error': 'Target existing_txn_id is required.'}), 400

    res = SyncEngine.link_transaction_to_existing(user.id, txn_id, existing_txn_id)
    if not res.get('success'):
        return jsonify(res), 400
    return jsonify(res)


@sync_bp.route('/api/sync/transactions/<int:txn_id>/reject', methods=['POST'])
@login_required
def api_reject_transaction(txn_id):
    """Dismiss / exclude a synced transaction."""
    user = g.current_user
    res = SyncEngine.reject_transaction(user.id, txn_id)
    if not res.get('success'):
        return jsonify(res), 400
    return jsonify(res)


@sync_bp.route('/api/sync/transactions/bulk-approve', methods=['POST'])
@login_required
def api_bulk_approve():
    """Bulk approve all high-confidence pending transactions."""
    user = g.current_user
    res = SyncEngine.bulk_approve_high_confidence(user.id)
    return jsonify(res)


@sync_bp.route('/api/sync/import-statement', methods=['POST'])
@login_required
def api_import_statement():
    """
    Parse uploaded bank statement CSV file.
    Supports mode='preview' (for user verification) and mode='commit' (for ingestion).
    """
    user = g.current_user
    mode = request.form.get('mode', 'preview').lower()
    bank_hint = request.form.get('bank_hint', 'AUTO')

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No statement file uploaded.'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'success': False, 'error': 'Empty file selected.'}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return jsonify({'success': False, 'error': f"Failed to read statement file: {str(e)}"}), 400

    parsed = StatementParser.parse_statement(content, bank_hint=bank_hint, currency=user.currency)
    if not parsed.get('success'):
        return jsonify(parsed), 400

    # If mode == preview, return parsed records for user review before writing
    if mode == 'preview':
        preview_rows = []
        for t in parsed['transactions'][:15]:  # Show first 15 preview items
            preview_rows.append({
                'date': t['date'].isoformat(),
                'narration': t['narration'],
                'amount_minor_units': t['amount_minor_units'],
                'formatted_amount': format_money(t['amount_minor_units'], user.currency),
                'direction': t['direction'],
                'external_id': t['external_id']
            })
        return jsonify({
            'success': True,
            'mode': 'preview',
            'bank_detected': parsed['bank_detected'],
            'total_detected': parsed['valid_count'],
            'error_count': parsed['error_count'],
            'preview_transactions': preview_rows
        })

    # Mode == commit: Ingest transactions into SyncedTransaction staging/ledger
    source_tag = f"STATEMENT_{parsed['bank_detected']}"
    res = SyncEngine.process_raw_transactions(
        user_id=user.id,
        connection_id=None,
        raw_records=parsed['transactions'],
        source=source_tag
    )

    # Record Audit Log
    audit = SyncAuditLog(
        user_id=user.id,
        connection_id=None,
        sync_type='STATEMENT_IMPORT',
        status='SUCCESS',
        records_fetched=parsed['valid_count'],
        records_imported=res['imported_count'],
        records_duplicates=res['duplicate_count'],
        records_review_required=res['review_count'],
        error_details=''
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Statement successfully imported ({res['imported_count']} auto-imported, {res['review_count']} queued for review).",
        'bank_detected': parsed['bank_detected'],
        'imported_count': res['imported_count'],
        'duplicate_count': res['duplicate_count'],
        'review_count': res['review_count']
    })


@sync_bp.route('/api/sync/upload-receipt', methods=['POST'])
@login_required
def api_upload_receipt():
    """
    Parse digital receipt or order confirmation text/file and find matching bank debits.
    """
    user = g.current_user
    text_content = request.form.get('receipt_text', '').strip()
    file_name = ''

    if 'receipt_file' in request.files:
        f = request.files['receipt_file']
        if f.filename:
            file_name = f.filename
            try:
                text_content = f.read().decode('utf-8', errors='ignore')
            except Exception:
                pass

    if not text_content:
        return jsonify({'success': False, 'error': 'Receipt text or file content is required.'}), 400

    parsed = ReceiptParser.parse_receipt_text(text_content, currency=user.currency, file_name=file_name)
    if not parsed.get('success'):
        return jsonify(parsed), 400

    # Find matching transactions in ledger
    matches = ReceiptParser.match_receipt_with_transactions(user.id, parsed)

    # Save Receipt Record
    receipt_record = ReceiptRecord(
        user_id=user.id,
        merchant_name=parsed['merchant'],
        order_id=parsed.get('order_id'),
        total_minor_units=parsed['total_minor_units'],
        receipt_date=parsed['receipt_date'],
        file_name=file_name,
        raw_text=parsed.get('raw_text', '')
    )
    db.session.add(receipt_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'receipt': receipt_record.to_dict(),
        'formatted_total': format_money(parsed['total_minor_units'], user.currency),
        'matches_found': len(matches),
        'matching_transactions': matches
    })


@sync_bp.route('/api/sync/audit-logs', methods=['GET'])
@login_required
def api_get_audit_logs():
    """Retrieve historical synchronization audit logs."""
    user = g.current_user
    logs = SyncAuditLog.query.filter_by(user_id=user.id).order_by(SyncAuditLog.created_at.desc()).limit(30).all()
    return jsonify({
        'success': True,
        'logs': [l.to_dict() for l in logs]
    })


# -----------------------------------------------------------------------------
# ACCOUNT AGGREGATOR WEBHOOK CALLBACK (CSRF EXEMPT)
# -----------------------------------------------------------------------------

@sync_bp.route('/api/sync/webhook/aa', methods=['POST'])
@csrf.exempt
def api_aa_webhook():
    """
    Asynchronous Webhook for RBI Account Aggregator notifications.
    Triggered when user approves consent or when new periodic FI data arrives.
    """
    payload = request.get_json() or {}
    logger.info(f"Received AA Webhook: {json.dumps(payload)[:300]}")

    consent_id = payload.get('consentId')
    status = payload.get('status', '').upper()

    if consent_id:
        conn = FinancialConnection.query.filter_by(consent_id=consent_id).first()
        if conn:
            if status in ('ACTIVE', 'APPROVED'):
                conn.consent_status = 'ACTIVE'
                conn.status = 'CONNECTED'
                # Trigger automatic data pull
                SyncEngine.sync_connection(conn.user_id, conn.id, sync_type='WEBHOOK')
            elif status in ('REVOKED', 'EXPIRED'):
                conn.consent_status = status
                conn.status = 'DISCONNECTED'
            db.session.commit()

    return jsonify({'success': True, 'status': 'RECEIVED'}), 200
