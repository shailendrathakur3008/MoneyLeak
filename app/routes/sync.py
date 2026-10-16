"""
Universal Expense Sync routes and REST API.
Handles bank connections, Account Aggregator consent, manual statement imports,
receipt matching, transaction review queue, and synchronization audits.
"""
import json
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
from app.services.sync.statement_parser import StatementParser
from app.services.sync.receipt_parser import ReceiptParser
from app.services.money import format_money

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

    return render_template(
        'sync.html',
        user=user,
        overview=overview,
        connections=connections,
        categories=categories,
        supported_fips=SUPPORTED_FIPS
    )


@sync_bp.route('/api/sync/overview', methods=['GET'])
@login_required
def api_get_overview():
    """Get high-level synchronization metrics."""
    user = g.current_user
    overview = SyncEngine.get_sync_overview(user.id)
    return jsonify({'success': True, 'overview': overview})


@sync_bp.route('/api/sync/connections', methods=['GET'])
@login_required
def api_get_connections():
    """List all financial connections for current user."""
    user = g.current_user
    connections = FinancialConnection.query.filter_by(user_id=user.id).order_by(FinancialConnection.created_at.desc()).all()
    return jsonify({
        'success': True,
        'connections': [c.to_dict() for c in connections],
        'supported_fips': SUPPORTED_FIPS
    })


@sync_bp.route('/api/sync/connections', methods=['POST'])
@login_required
def api_connect_institution():
    """
    Initiate Account Aggregator connection with chosen bank / FIP.
    """
    user = g.current_user
    data = request.get_json() or {}

    fip_code = data.get('fip_code', 'HDFC').upper()
    phone = data.get('phone') or user.phone_number or '9876543210'
    account_types = data.get('account_types') or ['SAVINGS']

    selected_fip = next((f for f in SUPPORTED_FIPS if f['code'] == fip_code), SUPPORTED_FIPS[0])

    # Check if this institution is already connected
    existing = FinancialConnection.query.filter_by(
        user_id=user.id,
        institution_code=fip_code,
        status='CONNECTED'
    ).first()

    if existing:
        return jsonify({'success': False, 'error': f"{selected_fip['name']} is already connected."}), 400

    aa_client = AccountAggregatorClient()
    consent_res = aa_client.create_consent_request(
        user_phone=phone,
        fip_code=fip_code,
        account_types=account_types
    )

    if not consent_res.get('success'):
        return jsonify({'success': False, 'error': consent_res.get('message', 'Failed to initiate consent.')}), 500

    # Create connection record
    new_conn = FinancialConnection(
        user_id=user.id,
        institution_name=selected_fip['name'],
        institution_code=fip_code,
        account_mask=consent_res.get('account_mask', '•••• 4821'),
        account_type=account_types[0] if account_types else 'SAVINGS',
        provider='ACCOUNT_AGGREGATOR',
        consent_id=consent_res.get('consent_id'),
        consent_status='ACTIVE',
        status='CONNECTED'
    )
    db.session.add(new_conn)
    db.session.commit()

    # Automatically perform initial sync for instant data visibility
    sync_res = SyncEngine.sync_connection(user.id, new_conn.id, sync_type='INITIAL_SYNC')

    return jsonify({
        'success': True,
        'message': f"Successfully linked {selected_fip['name']} via Account Aggregator.",
        'connection': new_conn.to_dict(),
        'sync_result': sync_res
    }), 201


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
