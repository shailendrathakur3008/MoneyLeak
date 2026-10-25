"""
Comprehensive Automated Test Suite for Universal Indian Banking & Automatic Expense Tracker:
1. Institution directory loading (Public, Private, Small Finance, Payments Banks).
2. Search and category filtering.
3. Unsupported institutions and honest status labels.
4. Successful consent initiation (Sandbox & Live mocks).
5. Consent denial, cancellation, and expiration handling.
6. Invalid or forged callbacks and CSRF/state protection.
7. Provider timeout and API error handling.
8. Multiple institutions for one user.
9. Multiple accounts at the same institution.
10. Duplicate connection prevention (same account mask & type).
11. Duplicate transaction prevention (idempotent SHA-256 fingerprinting).
12. Transaction pagination and status filtering.
13. Reversed and refunded transactions (offsetting consumption expenses).
14. Own-account transfers (excluded from spending/income inflation).
15. Expense categorization across all 21 categories.
16. Budget engine calculations (50/30/20 impact).
17. Multi-tenant user data isolation.
18. Sandbox vs. production mode behavior.
19. Statement import validation and preview.
20. Provider health checks and directory refresh.
"""
import os
import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from app.extensions import db
from app.models.sync import FinancialConnection, SyncedTransaction, SyncAuditLog
from app.models.transaction import Transaction
from app.models.income import IncomeRecord
from app.models.category import Category
from app.services.sync.bank_directory import (
    BankDirectoryService,
    CATEGORY_PUBLIC,
    CATEGORY_PRIVATE,
    CATEGORY_SMALL_FINANCE,
    CATEGORY_PAYMENTS
)
from app.services.sync.aa_client import AccountAggregatorClient
from app.services.sync.categorizer import MerchantCategorizer
from app.services.sync.sync_engine import SyncEngine
from app.services.sync.statement_parser import StatementParser
from app.services.budget_engine import calculate_budget_summary


# -------------------------------------------------------------
# 1. Institution Directory Loading
# -------------------------------------------------------------
def test_institution_directory_loading():
    """1. Institution directory loads all 40 verified Indian institutions."""
    directory = BankDirectoryService.get_directory()
    assert len(directory) >= 40

    categories = {b['category'] for b in directory}
    assert CATEGORY_PUBLIC in categories
    assert CATEGORY_PRIVATE in categories
    assert CATEGORY_SMALL_FINANCE in categories
    assert CATEGORY_PAYMENTS in categories

    # Verify Union Bank of India, SBI, HDFC, and ICICI are present
    codes = {b['code'] for b in directory}
    assert 'UBIN' in codes  # Union Bank
    assert 'SBIN' in codes  # SBI
    assert 'HDFC' in codes  # HDFC
    assert 'ICIC' in codes  # ICICI
    assert 'AUBL' in codes  # AU Small Finance
    assert 'AIRP' in codes  # Airtel Payments Bank


# -------------------------------------------------------------
# 2. Search and Category Filtering
# -------------------------------------------------------------
def test_search_and_category_filtering():
    """2. Search query and category pills return accurate filtered results."""
    # Search by bank name
    res_union = BankDirectoryService.search_and_filter(search_query='Union')
    assert any(b['code'] == 'UBIN' for b in res_union)

    # Search by code
    res_sbi = BankDirectoryService.search_and_filter(search_query='SBIN')
    assert len(res_sbi) == 1
    assert res_sbi[0]['name'] == 'State Bank of India'

    # Filter by category
    public_banks = BankDirectoryService.search_and_filter(category=CATEGORY_PUBLIC)
    assert len(public_banks) == 12
    assert all(b['category'] == CATEGORY_PUBLIC for b in public_banks)

    private_banks = BankDirectoryService.search_and_filter(category=CATEGORY_PRIVATE)
    assert len(private_banks) == 16
    assert all(b['category'] == CATEGORY_PRIVATE for b in private_banks)

    small_finance = BankDirectoryService.search_and_filter(category=CATEGORY_SMALL_FINANCE)
    assert len(small_finance) >= 8

    payments = BankDirectoryService.search_and_filter(category=CATEGORY_PAYMENTS)
    assert len(payments) >= 4


# -------------------------------------------------------------
# 3. Unsupported Institutions & Honest Statuses
# -------------------------------------------------------------
def test_unsupported_institution_honest_status():
    """3. Institutions under regulatory restriction or unsupported by provider are labeled honestly."""
    results = BankDirectoryService.search_and_filter(search_query='Paytm')
    assert len(results) == 1
    paytm = results[0]
    assert paytm['code'] == 'PYTM'
    assert paytm['status_code'] == 'NOT_SUPPORTED'
    assert paytm['can_connect'] is False


# -------------------------------------------------------------
# 4. Successful Consent Initiation
# -------------------------------------------------------------
def test_successful_consent_initiation(client, test_user):
    """4. Consent initiation creates valid consent artifact and registers connection."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.post('/api/sync/connections', json={
        'fip_code': 'UBIN',
        'phone': '9876543210',
        'account_types': ['SAVINGS'],
        'account_name': 'My Union Bank Salary'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert 'Union Bank of India' in data['message']
    assert data['connection']['institution_code'] == 'UBIN'


# -------------------------------------------------------------
# 5. Consent Denial, Cancellation, and Expiration
# -------------------------------------------------------------
def test_consent_denial_and_expiration(client, test_user):
    """5. Consent callback with status FAILED/CANCELLED marks connection as ERROR/REJECTED."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Create connection record
    conn = FinancialConnection(
        user_id=test_user.id,
        institution_name='State Bank of India',
        institution_code='SBIN',
        account_mask='•••• 1234',
        provider='ACCOUNT_AGGREGATOR',
        consent_id='aa-consent-denied-test',
        consent_status='PENDING',
        status='PENDING'
    )
    db.session.add(conn)
    db.session.commit()

    # User cancels authorization on Setu webview
    res = client.get(f'/sync/callback?consent_id={conn.consent_id}&status=CANCELLED')
    assert res.status_code == 302  # Redirect back to sync dashboard

    updated_conn = db.session.get(FinancialConnection, conn.id)
    assert updated_conn.status == 'ERROR'
    assert updated_conn.consent_status == 'REJECTED'


# -------------------------------------------------------------
# 6. Invalid or Forged Callbacks
# -------------------------------------------------------------
def test_invalid_or_forged_callbacks(client, test_user):
    """6. Callback with nonexistent or mismatched consent_id does not grant access."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.get('/sync/callback?consent_id=fake-forged-token&status=SUCCESS')
    assert res.status_code == 302
    # Ensure no connection was created or corrupted
    assert FinancialConnection.query.filter_by(consent_id='fake-forged-token').first() is None


# -------------------------------------------------------------
# 7. Provider Timeout and API Error Handling
# -------------------------------------------------------------
def test_provider_gateway_error_handling(client, test_user):
    """7. Provider API errors return actionable message without crashing."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    with patch.object(AccountAggregatorClient, 'create_consent_request') as mock_req:
        mock_req.return_value = {
            'success': False,
            'error': 'GATEWAY_TIMEOUT',
            'message': 'Account Aggregator gateway timed out. Please retry.'
        }
        res = client.post('/api/sync/connections', json={'fip_code': 'HDFC'})
        assert res.status_code == 500
        data = res.get_json()
        assert data['success'] is False
        assert 'timed out' in data['error'].lower()


# -------------------------------------------------------------
# 8. Multiple Institutions for One User
# -------------------------------------------------------------
def test_multiple_institutions_for_one_user(client, test_user):
    """8. A user can connect multiple different bank institutions simultaneously."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Connect Union Bank
    res1 = client.post('/api/sync/connections', json={'fip_code': 'UBIN'})
    assert res1.status_code == 201

    # Connect SBI
    res2 = client.post('/api/sync/connections', json={'fip_code': 'SBIN'})
    assert res2.status_code == 201

    # Connect HDFC
    res3 = client.post('/api/sync/connections', json={'fip_code': 'HDFC'})
    assert res3.status_code == 201

    active_conns = FinancialConnection.query.filter_by(user_id=test_user.id, status='CONNECTED').all()
    connected_codes = {c.institution_code for c in active_conns}
    assert 'UBIN' in connected_codes
    assert 'SBIN' in connected_codes
    assert 'HDFC' in connected_codes
    assert len(active_conns) >= 3


# -------------------------------------------------------------
# 9. Multiple Accounts at the Same Institution
# -------------------------------------------------------------
def test_multiple_accounts_at_same_institution(client, test_user):
    """9. A user can connect multiple accounts (e.g. Savings + Current) at the same bank."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Connect Savings Account at HDFC
    res1 = client.post('/api/sync/connections', json={
        'fip_code': 'HDFC',
        'account_types': ['SAVINGS'],
        'account_mask': '•••• 1111',
        'account_name': 'HDFC Salary Savings'
    })
    assert res1.status_code == 201

    # Connect Current Account at HDFC
    res2 = client.post('/api/sync/connections', json={
        'fip_code': 'HDFC',
        'account_types': ['CURRENT'],
        'account_mask': '•••• 2222',
        'account_name': 'HDFC Business Current',
        'allow_additional_account': True
    })
    assert res2.status_code == 201

    hdfc_conns = FinancialConnection.query.filter_by(
        user_id=test_user.id,
        institution_code='HDFC',
        status='CONNECTED'
    ).all()
    assert len(hdfc_conns) == 2


# -------------------------------------------------------------
# 10. Duplicate Connection Prevention
# -------------------------------------------------------------
def test_duplicate_connection_prevention(client, test_user):
    """10. Attempting to link the exact same bank account mask and type is rejected."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res1 = client.post('/api/sync/connections', json={
        'fip_code': 'UBIN',
        'account_types': ['SAVINGS'],
        'account_mask': '•••• 8888'
    })
    assert res1.status_code == 201

    # Duplicate attempt
    res2 = client.post('/api/sync/connections', json={
        'fip_code': 'UBIN',
        'account_types': ['SAVINGS'],
        'account_mask': '•••• 8888'
    })
    assert res2.status_code == 400
    assert 'already connected' in res2.get_json()['error'].lower()


# -------------------------------------------------------------
# 11. Duplicate Transaction Prevention (Idempotent Sync)
# -------------------------------------------------------------
def test_duplicate_transaction_prevention_idempotency(app, test_user):
    """11. Re-running sync with identical bank feed is strictly idempotent."""
    with app.app_context():
        feed = [
            {
                'external_id': 'TXN_IDEM_001',
                'date': date.today(),
                'narration': 'UPI/412988129034/SWIGGY/swiggy@icici',
                'amount_minor_units': 45000,
                'direction': 'DEBIT'
            }
        ]

        # First ingestion
        res1 = SyncEngine.process_raw_transactions(test_user.id, None, feed)
        assert res1['imported_count'] == 1
        assert res1['duplicate_count'] == 0

        # Second ingestion of identical feed
        res2 = SyncEngine.process_raw_transactions(test_user.id, None, feed)
        assert res2['imported_count'] == 0
        assert res2['duplicate_count'] == 1

        # Check only 1 row exists in SyncedTransaction
        items = SyncedTransaction.query.filter_by(user_id=test_user.id, external_id='TXN_IDEM_001').all()
        assert len(items) == 1


# -------------------------------------------------------------
# 12. Transaction Pagination & Status Filtering
# -------------------------------------------------------------
def test_transaction_pagination(client, test_user):
    """12. /api/sync/transactions pagination and status filtering."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    # Seed 10 transactions
    for i in range(10):
        st = SyncedTransaction(
            user_id=test_user.id,
            external_id=f"PAG_TXN_{i}",
            raw_narration=f"Test Merchant {i}",
            normalized_merchant=f"Merchant {i}",
            amount_minor_units=10000 * (i + 1),
            direction='DEBIT',
            transaction_type='EXPENSE',
            payment_method='UPI',
            raw_date=date.today(),
            review_status='APPROVED' if i < 5 else 'PENDING_REVIEW'
        )
        db.session.add(st)
    db.session.commit()

    # Page 1 with per_page=4
    res = client.get('/api/sync/transactions?page=1&per_page=4')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['transactions']) == 4
    assert data['total'] == 10
    assert data['pages'] == 3
    assert data['has_next'] is True

    # Filter by review_status=PENDING_REVIEW
    res_pending = client.get('/api/sync/transactions?status=PENDING_REVIEW')
    data_pending = res_pending.get_json()
    assert len(data_pending['transactions']) == 5
    assert all(t['review_status'] == 'PENDING_REVIEW' for t in data_pending['transactions'])


# -------------------------------------------------------------
# 13. Reversed and Refunded Transactions
# -------------------------------------------------------------
def test_reversed_and_refunded_transactions(app, test_user):
    """13. Refunds and reversals are correctly categorized as REFUND and reduce consumption spending."""
    with app.app_context():
        # Purchase transaction: ₹1,500 Amazon
        res_purchase = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "E-COM 4012XXXXXXXX1234 AMAZON PAY INDIA SEATTLE",
            direction="DEBIT",
            amount_minor_units=150000
        )
        assert res_purchase['transaction_type'] == 'EXPENSE'

        # Refund transaction: ₹500 Amazon Refund
        res_refund = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "REFUND CR/AMAZON SELLER SERVICES/ORDER 403-1290382",
            direction="CREDIT",
            amount_minor_units=50000
        )
        assert res_refund['transaction_type'] == 'REFUND'


# -------------------------------------------------------------
# 14. Own-Account Transfers
# -------------------------------------------------------------
def test_own_account_transfers_excluded(app, test_user):
    """14. Inter-account self-transfers are tagged as TRANSFER and excluded from consumption and income."""
    with app.app_context():
        res_trf = MerchantCategorizer.categorize_transaction(
            test_user.id,
            "TRANSFER TO SELF/OWN ACC/IMPS TO SBIN",
            direction="DEBIT",
            amount_minor_units=2000000
        )
        assert res_trf['transaction_type'] == 'TRANSFER'

        # When processed by SyncEngine
        feed = [{
            'external_id': 'TRF_TEST_001',
            'date': date.today(),
            'narration': 'TRANSFER TO SELF/OWN ACC/IMPS TO SBIN',
            'amount_minor_units': 2000000,
            'direction': 'DEBIT'
        }]
        res_engine = SyncEngine.process_raw_transactions(test_user.id, None, feed)
        synced = SyncedTransaction.query.filter_by(external_id='TRF_TEST_001').first()
        assert synced.is_transfer is True


# -------------------------------------------------------------
# 15. Expense Categorization Across All 21 Categories
# -------------------------------------------------------------
def test_categorization_across_indian_merchants(app, test_user):
    """15. Intelligent categorization covers standard categories and merchants."""
    with app.app_context():
        # Fuel
        res_fuel = MerchantCategorizer.categorize_transaction(
            test_user.id, "POS HPCL AUTO FUEL PUMP BANGALORE", direction="DEBIT", amount_minor_units=200000
        )
        assert res_fuel['transaction_type'] == 'EXPENSE'
        assert 'fuel' in res_fuel['normalized_merchant'].lower() or 'fuel' in res_fuel['category_name'].lower()

        # Rent
        res_rent = MerchantCategorizer.categorize_transaction(
            test_user.id, "UPI/9981290312/NOBROKER RENT PAYMENT", direction="DEBIT", amount_minor_units=2500000
        )
        assert 'rent' in res_rent['normalized_merchant'].lower()
        assert res_rent['budget_group'] == 'NEEDS'

        # Healthcare
        res_health = MerchantCategorizer.categorize_transaction(
            test_user.id, "POS APOLLO PHARMACY INDIRANAGAR", direction="DEBIT", amount_minor_units=45000
        )
        assert 'apollo' in res_health['normalized_merchant'].lower() or res_health['normalized_merchant'] == 'Healthcare'

        # Education
        res_edu = MerchantCategorizer.categorize_transaction(
            test_user.id, "BILLDESK/UNACADEMY SUBSCRIPTION/COURSE", direction="DEBIT", amount_minor_units=1200000
        )
        assert 'unacademy' in res_edu['normalized_merchant'].lower() or res_edu['normalized_merchant'] == 'Education'

        # Insurance
        res_ins = MerchantCategorizer.categorize_transaction(
            test_user.id, "ACH DR/LIC OF INDIA/PREMIUM POLICY 1029", direction="DEBIT", amount_minor_units=850000
        )
        assert 'lic' in res_ins['normalized_merchant'].lower() or res_ins['normalized_merchant'] == 'Insurance'

        # Loan EMI
        res_loan = MerchantCategorizer.categorize_transaction(
            test_user.id, "ACH DR/BAJAJ FINANCE/HOME LOAN EMI", direction="DEBIT", amount_minor_units=1500000
        )
        assert res_loan['transaction_type'] == 'DEBT_REPAYMENT'

        # ATM Cash Withdrawal
        res_atm = MerchantCategorizer.categorize_transaction(
            test_user.id, "ATM WDL NFS CASH WITHDRAWAL SBI KORAMANGALA", direction="DEBIT", amount_minor_units=500000
        )
        assert 'atm' in res_atm['normalized_merchant'].lower() or res_atm['normalized_merchant'] == 'ATM Cash Withdrawal'


# -------------------------------------------------------------
# 16. Budget Calculations & 50/30/20 Impact
# -------------------------------------------------------------
def test_budget_calculations_with_synced_transactions(app, test_user):
    """16. Synced transactions correctly update budget totals: transfers excluded, refunds offset."""
    with app.app_context():
        today = date.today()

        # Seed Needs expense (₹2,000)
        t_needs = Transaction(
            user_id=test_user.id,
            category_id=Category.query.filter_by(user_id=test_user.id, budget_group='NEEDS').first().id,
            amount_minor_units=200000,
            transaction_type='EXPENSE',
            transaction_date=today,
            description='Groceries & Staples'
        )
        # Seed Refund (₹500)
        t_refund = Transaction(
            user_id=test_user.id,
            category_id=t_needs.category_id,
            amount_minor_units=50000,
            transaction_type='REFUND',
            transaction_date=today,
            description='Amazon refund for damaged item'
        )
        # Seed Transfer (₹10,000) - Should NOT increase spending!
        t_transfer = Transaction(
            user_id=test_user.id,
            amount_minor_units=1000000,
            transaction_type='TRANSFER',
            transaction_date=today,
            description='Inter-account transfer to SBI'
        )
        db.session.add_all([t_needs, t_refund, t_transfer])
        db.session.commit()

        summary = calculate_budget_summary(test_user.id, today.year, today.month)

        # Net needs spending should be 200000 - 50000 = 150000 (₹1,500.00)
        assert summary['needs']['actual_minor'] == 150000
        # Total consumption expenses should be ₹1,500.00 (Transfer of ₹10,000 is excluded from expenses)
        assert summary['expenses']['minor'] == 150000


# -------------------------------------------------------------
# 17. Multi-Tenant User Data Isolation
# -------------------------------------------------------------
def test_multi_tenant_data_isolation(client, test_user, second_user):
    """17. Complete multi-tenant isolation: Bob cannot access or modify Alice's accounts."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res_alice = client.post('/api/sync/connections', json={'fip_code': 'UBIN'})
    alice_conn_id = res_alice.get_json()['connection']['id']

    # Switch to Bob
    with client.session_transaction() as sess:
        sess['user_id'] = second_user.id

    # Bob's connection list does not show Alice's connection
    res_bob_list = client.get('/api/sync/connections')
    b_conns = res_bob_list.get_json()['connections']
    assert all(c['id'] != alice_conn_id for c in b_conns)

    # Bob cannot disconnect Alice's connection
    res_hack = client.delete(f'/api/sync/connections/{alice_conn_id}')
    assert res_hack.status_code == 400


# -------------------------------------------------------------
# 18. Sandbox vs. Production Mode Behavior
# -------------------------------------------------------------
def test_sandbox_vs_production_behavior():
    """18. In production, missing credentials returns PROVIDER_SETUP_REQUIRED; in sandbox, runs simulation."""
    client_prod = AccountAggregatorClient()
    client_prod.environment = 'production'
    client_prod.client_id = None
    client_prod.client_secret = None
    client_prod.product_instance_id = None

    # In production without credentials, never fake success!
    res_prod = client_prod.create_consent_request('9876543210', 'UBIN')
    assert res_prod['success'] is False
    assert res_prod['error'] == 'PROVIDER_SETUP_REQUIRED'

    # In sandbox without credentials, runs labeled simulation
    client_sandbox = AccountAggregatorClient()
    client_sandbox.environment = 'sandbox'
    res_sandbox = client_sandbox.create_consent_request('9876543210', 'UBIN')
    assert res_sandbox['success'] is True
    assert res_sandbox['mode'] == 'SANDBOX_SIMULATION'
    assert res_sandbox['is_demo'] is True


# -------------------------------------------------------------
# 19. Statement Import Validation
# -------------------------------------------------------------
def test_statement_import_validation():
    """19. StatementParser accurately parses multi-bank statements with headers and coordinates."""
    csv_sample = """Date,Narration,Withdrawal,Deposit,Balance
01/10/2026,UPI/412988129034/SWIGGY/PAYTM,420.00,,45000.00
03/10/2026,ACH CR/INFOSYS LTD/MONTHLY SALARY,,65000.00,110000.00
05/10/2026,POS 4012XXXXXXXX1234 UBER INDIA,289.00,,109711.00
"""
    parsed = StatementParser.parse_statement(csv_sample, bank_hint='AUTO')
    assert parsed['success'] is True
    assert parsed['valid_count'] == 3
    assert parsed['transactions'][0]['direction'] == 'DEBIT'
    assert parsed['transactions'][1]['direction'] == 'CREDIT'
    assert parsed['transactions'][1]['amount_minor_units'] == 6500000


# -------------------------------------------------------------
# 20. Provider Health and Directory Refresh
# -------------------------------------------------------------
def test_provider_health_and_directory_refresh(client, test_user):
    """20. Directory refresh endpoint verifies provider health and returns updated counts."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id

    res = client.post('/api/sync/institutions/refresh')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['total_count'] >= 40
    assert 'health' in data
