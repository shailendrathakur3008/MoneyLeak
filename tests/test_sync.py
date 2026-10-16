"""
Comprehensive Acceptance Tests for Universal Expense Sync:
1. Account Aggregator connection lifecycle and consent verification
2. Multi-app UPI transaction capture (Google Pay, PhonePe, Paytm, BHIM)
3. Card purchases and merchant normalization (Amazon, Swiggy, Blinkit, Uber)
4. Idempotent deduplication via external UTR/RRN and fuzzy match detection
5. Accounting correctness: Refunds, Transfers, CC bill payments, and SIPs
6. Core ledger integration (50/30/20 budget calculations update automatically)
7. Category preference memory and manual review queue workflows
8. Multi-bank statement CSV parsing (HDFC, SBI, ICICI, Axis, Generic)
9. Receipt parsing and bank debit matching
10. Multi-tenant security isolation and revocation
"""
import io
import json
from datetime import date, timedelta
from app.extensions import db
from app.models.sync import (
    FinancialConnection,
    SyncedTransaction,
    MerchantCategoryPreference,
    SyncAuditLog,
    ReceiptRecord
)
from app.models.transaction import Transaction
from app.models.income import IncomeRecord
from app.models.category import Category
from app.services.sync.categorizer import MerchantCategorizer
from app.services.sync.reconciler import TransactionReconciler
from app.services.sync.statement_parser import StatementParser
from app.services.sync.receipt_parser import ReceiptParser
from app.services.sync.sync_engine import SyncEngine
from app.services.budget_engine import calculate_budget_summary


def test_merchant_categorizer_indian_merchants(app, test_user):
    """1. Test merchant normalization, method detection, and category matching for Indian apps."""
    with app.app_context():
        # A. Swiggy Food Delivery via UPI
        res_swiggy = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "UPI/412988129034/SWIGGY/PAYTM/swiggy@icici",
            direction="DEBIT",
            amount_minor_units=42000
        )
        assert res_swiggy['normalized_merchant'] == 'Swiggy'
        assert res_swiggy['payment_method'] == 'UPI'
        assert res_swiggy['transaction_type'] == 'EXPENSE'
        assert res_swiggy['confidence_level'] == 'HIGH'

        # B. Blinkit Quick Groceries via UPI
        res_blinkit = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "UPI/412877123999/BLINKIT/KOTAK/groceries@kotak",
            direction="DEBIT",
            amount_minor_units=78500
        )
        assert res_blinkit['normalized_merchant'] == 'Blinkit'
        assert res_blinkit['payment_method'] == 'UPI'
        assert res_blinkit['budget_group'] == 'NEEDS'

        # C. Uber Ride via Card POS
        res_uber = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "POS 4012XXXXXXXX1234 UBER INDIA TECH P BANGALORE",
            direction="DEBIT",
            amount_minor_units=28900
        )
        assert res_uber['normalized_merchant'] == 'Uber'
        assert res_uber['payment_method'] == 'CARD'

        # D. Zerodha SIP Investment (Savings Contribution, NOT consumption!)
        res_zerodha = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "ACH DR/ZERODHA BROKING LTD/SIP MUTUAL FUND",
            direction="DEBIT",
            amount_minor_units=500000
        )
        assert res_zerodha['transaction_type'] == 'SAVINGS_CONTRIBUTION'
        assert res_zerodha['budget_group'] == 'SAVINGS'

        # E. CRED Credit Card Bill Payment (Transfer / Debt Repayment, NOT consumption!)
        res_cred = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "UPI/412099881234/CRED/AXIS/CC PAYMENT HDFC REGALIA",
            direction="DEBIT",
            amount_minor_units=1200000
        )
        assert res_cred['transaction_type'] == 'TRANSFER'

        # F. Amazon Refund (Refund offset)
        res_refund = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "REFUND CR/AMAZON SELLER SERVICES/ORDER 403-1290382",
            direction="CREDIT",
            amount_minor_units=49900
        )
        assert res_refund['transaction_type'] == 'REFUND'


def test_merchant_user_preference_priority(app, test_user):
    """2. User-approved category preference overrides default heuristics."""
    with app.app_context():
        # Get a specific category, e.g. Books or Personal
        custom_cat = Category.query.filter_by(user_id=test_user.id, budget_group='NEEDS').first()
        assert custom_cat is not None

        # Add explicit user preference for 'Zepto'
        pref = MerchantCategoryPreference(
            user_id=test_user.id,
            merchant_normalized='zepto',
            category_id=custom_cat.id,
            transaction_type='EXPENSE'
        )
        db.session.add(pref)
        db.session.commit()

        # Categorizing Zepto now must match user's custom preference
        res = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "UPI/209876543210/ZEPTO/YESB/zepto@yesbank",
            direction="DEBIT",
            amount_minor_units=35000
        )
        assert res['category_id'] == custom_cat.id
        assert res['confidence_score'] == 0.99
        assert "User-defined rule" in res['reason']


def test_transaction_deduplication_and_idempotence(app, test_user):
    """3. Deduplication engine detects exact UTR duplicates, ledger matches, and fuzzy windows."""
    with app.app_context():
        today = date.today()

        # 1. External ID deduplication check
        st = SyncedTransaction(
            user_id=test_user.id,
            external_id="UTR123456789012",
            raw_narration="UPI/123456789012/ZOMATO",
            normalized_merchant="Zomato",
            amount_minor_units=45000,
            direction="DEBIT",
            raw_date=today
        )
        db.session.add(st)
        db.session.commit()

        status, _, reason = TransactionReconciler.check_duplicate(
            user_id=test_user.id,
            external_id="UTR123456789012",
            amount_minor_units=45000,
            transaction_date=today,
            direction="DEBIT",
            normalized_merchant="Zomato"
        )
        assert status == 'DUPLICATE_EXTERNAL_ID'

        # 2. Existing manual transaction exact coordinate match
        cat = Category.query.filter_by(user_id=test_user.id).first()
        manual_txn = Transaction(
            user_id=test_user.id,
            category_id=cat.id,
            amount_minor_units=30000,
            transaction_type='EXPENSE',
            transaction_date=today,
            description='Lunch at Subway',
            merchant='Subway'
        )
        db.session.add(manual_txn)
        db.session.commit()

        status_exact, matched_id, _ = TransactionReconciler.check_duplicate(
            user_id=test_user.id,
            external_id="NEW_UTR_999",
            amount_minor_units=30000,
            transaction_date=today,
            direction="DEBIT",
            normalized_merchant="Subway"
        )
        assert status_exact == 'EXACT_MATCH'
        assert matched_id == manual_txn.id

        # 3. Fuzzy match: Same amount within ±2 days with similar narration
        status_fuzzy, fuzzy_id, _ = TransactionReconciler.check_duplicate(
            user_id=test_user.id,
            external_id="NEW_UTR_888",
            amount_minor_units=30000,
            transaction_date=today + timedelta(days=1),
            direction="DEBIT",
            normalized_merchant="Subway Restaurant"
        )
        assert status_fuzzy == 'POTENTIAL_DUPLICATE'
        assert fuzzy_id == manual_txn.id


def test_account_aggregator_connect_and_sync_flow(client, test_user):
    """4. Connect bank institution via Account Aggregator and sync transactions."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # A. Connect HDFC Bank
    res = client.post('/api/sync/connections', json={
        'fip_code': 'HDFC',
        'phone': '9876543210',
        'account_types': ['SAVINGS']
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    conn_id = data['connection']['id']

    # B. Verify connection registered in DB
    conn = FinancialConnection.query.get(conn_id)
    assert conn is not None
    assert conn.user_id == test_user.id
    assert conn.institution_code == 'HDFC'
    assert conn.status == 'CONNECTED'

    # C. Verify initial sync executed and populated SyncedTransaction staging table
    synced_items = SyncedTransaction.query.filter_by(connection_id=conn.id).all()
    assert len(synced_items) > 0

    # D. Trigger Sync Now
    res_sync = client.post(f'/api/sync/connections/{conn.id}/sync')
    assert res_sync.status_code == 200
    sync_data = res_sync.get_json()
    assert sync_data['success'] is True
    # Repeated sync should be idempotent and count duplicates rather than re-creating them
    assert sync_data['duplicate_count'] > 0


def test_synced_transactions_integrate_with_budget_summary(app, test_user):
    """5. Approved synced transactions immediately reflect in 50/30/20 budget calculations."""
    with app.app_context():
        today = date.today()

        # Seed Needs Category
        needs_cat = Category.query.filter_by(user_id=test_user.id, budget_group='NEEDS').first()
        # Seed Wants Category
        wants_cat = Category.query.filter_by(user_id=test_user.id, budget_group='WANTS').first()

        # Process a raw grocery purchase (₹800 -> 80,000 paise)
        raw_items = [
            {
                'external_id': 'TEST_BLINKIT_001',
                'date': today,
                'narration': 'UPI/412877123999/BLINKIT/KOTAK/groceries@kotak',
                'amount_minor_units': 80000,
                'direction': 'DEBIT'
            },
            {
                'external_id': 'TEST_SWIGGY_002',
                'date': today,
                'narration': 'UPI/412988129034/SWIGGY/PAYTM/swiggy@icici',
                'amount_minor_units': 45000,
                'direction': 'DEBIT'
            }
        ]

        res = SyncEngine.process_raw_transactions(
            user_id=test_user.id,
            connection_id=None,
            raw_records=raw_items,
            source="AA_TEST"
        )
        assert res['imported_count'] == 2

        # Verify budget engine summary reflects the spending
        summary = calculate_budget_summary(test_user.id, today.year, today.month)
        assert summary['expenses']['minor'] >= 125000  # ₹800 + ₹450 = ₹1,250
        assert summary['needs']['actual_minor'] >= 80000
        assert summary['wants']['actual_minor'] >= 45000


def test_refunds_and_transfers_do_not_inflate_consumption(app, test_user):
    """6. Refunds reduce outflow and transfers/debt payments do not count as consumption."""
    with app.app_context():
        today = date.today()
        wants_cat = Category.query.filter_by(user_id=test_user.id, budget_group='WANTS').first()

        # 1. Base expense: ₹1,000
        txn_expense = Transaction(
            user_id=test_user.id,
            category_id=wants_cat.id,
            amount_minor_units=100000,
            transaction_type='EXPENSE',
            transaction_date=today,
            description='Amazon Online Order'
        )
        # 2. Refund: ₹400
        txn_refund = Transaction(
            user_id=test_user.id,
            category_id=wants_cat.id,
            amount_minor_units=40000,
            transaction_type='REFUND',
            transaction_date=today,
            description='Amazon Return Refund'
        )
        # 3. Credit Card Payment / Self Transfer: ₹15,000
        txn_transfer = Transaction(
            user_id=test_user.id,
            category_id=wants_cat.id,
            amount_minor_units=1500000,
            transaction_type='TRANSFER',
            transaction_date=today,
            description='CRED HDFC Card Bill Payment'
        )
        db.session.add_all([txn_expense, txn_refund, txn_transfer])
        db.session.commit()

        summary = calculate_budget_summary(test_user.id, today.year, today.month)
        # Net consumption should be 1000 - 400 = 600, NOT 1000 + 15000!
        assert summary['expenses']['minor'] == 60000
        assert summary['wants']['actual_minor'] == 60000


def test_statement_csv_parser_multi_bank(app):
    """7. StatementParser parses HDFC, SBI, ICICI, and generic statement CSV formats."""
    with app.app_context():
        # HDFC Format Sample
        hdfc_csv = """Date,Narration,Chq/Ref No,Value Dt,Withdrawal Amt,Deposit Amt,Closing Balance
14/10/2026,UPI-SWIGGY-swiggy@icici-PAYTM,412988129034,14/10/2026,420.00,,45210.00
15/10/2026,ACH CR-INFOSYS LTD-SALARY,SAL992182,15/10/2026,,65000.00,110210.00
"""
        parsed_hdfc = StatementParser.parse_statement(hdfc_csv, bank_hint='HDFC')
        assert parsed_hdfc['success'] is True
        assert parsed_hdfc['valid_count'] == 2
        assert parsed_hdfc['transactions'][0]['amount_minor_units'] == 42000
        assert parsed_hdfc['transactions'][0]['direction'] == 'DEBIT'
        assert parsed_hdfc['transactions'][1]['amount_minor_units'] == 6500000
        assert parsed_hdfc['transactions'][1]['direction'] == 'CREDIT'

        # Generic CSV with single Amount column and Cr/Dr
        generic_csv = """Date,Description,Amount,Type
2026-10-12,Zomato Online Delivery,350.00,DR
2026-10-13,Friend UPI Reimbursement,500.00,CR
"""
        parsed_gen = StatementParser.parse_statement(generic_csv, bank_hint='GENERIC')
        assert parsed_gen['success'] is True
        assert parsed_gen['valid_count'] == 2
        assert parsed_gen['transactions'][0]['direction'] == 'DEBIT'
        assert parsed_gen['transactions'][1]['direction'] == 'CREDIT'


def test_receipt_parser_and_matching(app, test_user):
    """8. ReceiptParser parses digital order confirmation and matches with bank debit."""
    with app.app_context():
        today = date.today()

        # Seed an existing synced transaction
        st = SyncedTransaction(
            user_id=test_user.id,
            external_id="UPI41290001",
            raw_narration="UPI/41290001/SWIGGY",
            normalized_merchant="Swiggy",
            amount_minor_units=42000,
            direction="DEBIT",
            raw_date=today
        )
        db.session.add(st)
        db.session.commit()

        receipt_text = f"""
        Swiggy Order Receipt
        Order ID: 19283742910
        Date: {today.strftime('%d/%m/%Y')}
        Items: 1x Paneer Butter Masala, 2x Butter Naan
        Total Paid: ₹420.00 via UPI
        """

        parsed = ReceiptParser.parse_receipt_text(receipt_text, currency='INR')
        assert parsed['success'] is True
        assert parsed['merchant'] == 'Swiggy'
        assert parsed['total_minor_units'] == 42000
        assert parsed['order_id'] == '19283742910'

        matches = ReceiptParser.match_receipt_with_transactions(test_user.id, parsed)
        assert len(matches) >= 1
        assert matches[0]['id'] == st.id


def test_multi_user_data_isolation(client, test_user, second_user):
    """9. Financial connections and synced transactions are strictly isolated per user."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Alice connects HDFC
    res_a = client.post('/api/sync/connections', json={'fip_code': 'HDFC'})
    assert res_a.status_code == 201
    alice_conn_id = res_a.get_json()['connection']['id']

    # Switch session to Bob
    with client.session_transaction() as sess:
        sess['user_id'] = second_user.id

    # Bob's connections list should NOT include Alice's connection
    res_b_list = client.get('/api/sync/connections')
    assert res_b_list.status_code == 200
    b_conns = res_b_list.get_json()['connections']
    assert all(c['id'] != alice_conn_id for c in b_conns)

    # Bob cannot disconnect Alice's connection
    res_hack = client.delete(f'/api/sync/connections/{alice_conn_id}')
    assert res_hack.status_code == 400
    assert 'not found' in res_hack.get_json()['error'].lower()


def test_revoke_consent_and_disconnect(client, test_user):
    """10. Disconnecting an institution revokes consent and stops synchronization."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Connect ICICI Bank
    res = client.post('/api/sync/connections', json={'fip_code': 'ICIC'})
    conn_id = res.get_json()['connection']['id']

    # Disconnect
    res_disc = client.delete(f'/api/sync/connections/{conn_id}')
    assert res_disc.status_code == 200

    conn = FinancialConnection.query.get(conn_id)
    assert conn.status == 'DISCONNECTED'
    assert conn.consent_status == 'REVOKED'

    # Sync attempt on disconnected institution should be blocked
    res_sync = client.post(f'/api/sync/connections/{conn_id}/sync')
    assert res_sync.status_code == 400
    assert 'disconnected' in res_sync.get_json()['error'].lower()
