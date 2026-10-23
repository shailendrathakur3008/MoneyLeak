"""
Multi-Bank Statement Parser.
Supports standard CSV formats from Indian banks (HDFC, SBI, ICICI, Axis)
and Generic CSVs with automatic dialect detection, header alignment,
date normalization, and amount extraction in integer minor units.
"""
import io
import re
import csv
import hashlib
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from app.services.money import to_minor_units


class StatementParser:
    """Parses bank statements into standardized transaction records with validation."""

    DATE_FORMATS = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d/%m/%y',
        '%d-%m-%y',
        '%d-%b-%Y',
        '%d %b %Y',
        '%d-%B-%Y',
        '%b %d, %Y',
        '%d/%m/%Y %H:%M:%S',
        '%Y-%m-%d %H:%M:%S'
    ]

    @staticmethod
    def parse_statement(
        file_content: str,
        bank_hint: str = 'AUTO',
        currency: str = 'INR'
    ) -> Dict[str, Any]:
        """
        Parse CSV content into a list of normalized transaction dictionaries.
        Returns:
          {
             'success': bool,
             'bank_detected': str,
             'valid_count': int,
             'error_count': int,
             'transactions': [...],
             'errors': [...]
          }
        """
        if not file_content or not file_content.strip():
            return {
                'success': False,
                'error': 'Statement file is empty.',
                'transactions': [],
                'errors': []
            }

        lines = file_content.strip().splitlines()
        
        # 1. Detect header row
        header_idx, headers, bank_detected = StatementParser._find_header_row(lines, bank_hint)
        if header_idx is None:
            return {
                'success': False,
                'error': 'Could not identify statement headers. Ensure your CSV contains columns for Date, Description, and Amount.',
                'transactions': [],
                'errors': []
            }

        reader = csv.reader(lines[header_idx + 1:])
        parsed_records: List[Dict[str, Any]] = []
        errors: List[str] = []

        line_num = header_idx + 1
        for row in reader:
            line_num += 1
            if not row or not any(field.strip() for field in row):
                continue

            try:
                record = StatementParser._parse_row(row, headers, bank_detected, currency, line_num)
                if record:
                    parsed_records.append(record)
            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")

        return {
            'success': True,
            'bank_detected': bank_detected,
            'valid_count': len(parsed_records),
            'error_count': len(errors),
            'transactions': parsed_records,
            'errors': errors[:10]  # First 10 errors for brevity
        }

    @staticmethod
    def _find_header_row(lines: List[str], bank_hint: str) -> Tuple[Optional[int], Optional[List[str]], str]:
        """Locate the row index that contains column headers."""
        bank = bank_hint.upper() if bank_hint and bank_hint != 'AUTO' else 'GENERIC'

        for idx, line in enumerate(lines[:30]):  # Search first 30 lines
            row = [f.strip().lower() for f in csv.reader([line]).__next__()]
            row_text = " ".join(row)

            # Check for HDFC signature
            if 'narration' in row_text and ('withdrawal' in row_text or 'deposit' in row_text):
                return idx, [f.strip() for f in csv.reader([line]).__next__()], 'HDFC'

            # Check for SBI signature
            if 'txn date' in row_text or ('description' in row_text and 'ref no' in row_text):
                return idx, [f.strip() for f in csv.reader([line]).__next__()], 'SBI'

            # Check for ICICI signature
            if 'transaction remarks' in row_text or ('withdrawal amount' in row_text and 'deposit amount' in row_text):
                return idx, [f.strip() for f in csv.reader([line]).__next__()], 'ICICI'

            # Check for Axis signature
            if 'particulars' in row_text and ('dr' in row or 'cr' in row):
                return idx, [f.strip() for f in csv.reader([line]).__next__()], 'AXIS'

            # Check for Union Bank signature
            if 'union' in row_text or ('remarks' in row_text and ('debit' in row_text or 'withdrawal' in row_text)):
                return idx, [f.strip() for f in csv.reader([line]).__next__()], 'UNION_BANK'

            # Check Generic signature
            if 'date' in row_text and ('amount' in row_text or 'debit' in row_text or 'description' in row_text):
                return idx, [f.strip() for f in csv.reader([line]).__next__()], bank

        return None, None, 'UNKNOWN'

    @staticmethod
    def _parse_row(
        row: List[str],
        headers: List[str],
        bank: str,
        currency: str,
        line_num: int
    ) -> Optional[Dict[str, Any]]:
        """Map CSV row to normalized transaction dictionary."""
        # Create lower-case key-value map
        row_dict = {}
        for idx, val in enumerate(row):
            if idx < len(headers):
                row_dict[headers[idx].strip().lower()] = val.strip()

        # 1. Extract Date
        date_val = StatementParser._extract_date(row_dict)
        if not date_val:
            return None

        # 2. Extract Narration / Description
        narration = StatementParser._extract_narration(row_dict)
        if not narration:
            narration = 'Bank Transaction'

        # 3. Extract Amount & Direction (Debit vs Credit)
        amount_minor, direction = StatementParser._extract_amount(row_dict, currency)
        if amount_minor <= 0:
            return None

        # 4. Extract Reference ID if present
        ref_id = StatementParser._extract_ref_id(row_dict, narration)

        # 5. Generate unique external ID
        hash_input = f"{date_val.isoformat()}|{amount_minor}|{direction}|{narration}|{ref_id or ''}"
        external_id = ref_id if ref_id and len(ref_id) >= 6 else f"CSV_{hashlib.md5(hash_input.encode()).hexdigest()[:14]}"

        return {
            'external_id': external_id,
            'date': date_val,
            'narration': narration,
            'amount_minor_units': amount_minor,
            'currency': currency,
            'direction': direction,
            'ref_id': ref_id,
            'source': f"STATEMENT_{bank}"
        }

    @staticmethod
    def _extract_date(row_dict: Dict[str, str]) -> Optional[date]:
        """Locate and parse date from row dictionary."""
        date_candidates = ['date', 'txn date', 'transaction date', 'value date', 'tran date']
        raw_val = None
        for key in date_candidates:
            if key in row_dict and row_dict[key]:
                raw_val = row_dict[key]
                break

        if not raw_val:
            # Fallback: check any key with 'date'
            for k, v in row_dict.items():
                if 'date' in k and v:
                    raw_val = v
                    break

        if not raw_val:
            return None

        # Clean string
        raw_clean = re.sub(r'[\'"]', '', raw_val.strip())
        for fmt in StatementParser.DATE_FORMATS:
            try:
                return datetime.strptime(raw_clean, fmt).date()
            except ValueError:
                continue

        return None

    @staticmethod
    def _extract_narration(row_dict: Dict[str, str]) -> str:
        """Find description/narration field."""
        keys = ['narration', 'description', 'transaction remarks', 'particulars', 'remarks', 'details', 'payee']
        for k in keys:
            if k in row_dict and row_dict[k]:
                return row_dict[k]
        return ''

    @staticmethod
    def _extract_amount(row_dict: Dict[str, str], currency: str) -> Tuple[int, str]:
        """
        Extract minor units amount and determine DEBIT vs CREDIT.
        Handles both 2-column (Debit/Credit) and 1-column (Amount + type) structures.
        """
        # Case A: Separate Debit and Credit columns
        debit_keys = ['withdrawal amount', 'withdrawal', 'debit', 'dr', 'withdrawal amt', 'withdrawal amount (inr)']
        credit_keys = ['deposit amount', 'deposit', 'credit', 'cr', 'deposit amt', 'deposit amount (inr)']

        debit_val = None
        for k in debit_keys:
            if k in row_dict and row_dict[k]:
                debit_val = StatementParser._clean_num_str(row_dict[k])
                break

        credit_val = None
        for k in credit_keys:
            if k in row_dict and row_dict[k]:
                credit_val = StatementParser._clean_num_str(row_dict[k])
                break

        if debit_val and debit_val > 0:
            return to_minor_units(debit_val, currency), 'DEBIT'
        if credit_val and credit_val > 0:
            return to_minor_units(credit_val, currency), 'CREDIT'

        # Case B: Single Amount column
        amount_keys = ['amount', 'txn amount', 'total', 'transaction amount']
        for k in amount_keys:
            if k in row_dict and row_dict[k]:
                val_str = row_dict[k]
                num_val = StatementParser._clean_num_str(val_str)
                if num_val and num_val > 0:
                    # Check direction indicator
                    dir_keys = ['type', 'cr/dr', 'dr/cr', 'direction']
                    direction = 'DEBIT'
                    for dk in dir_keys:
                        if dk in row_dict and 'cr' in row_dict[dk].lower():
                            direction = 'CREDIT'
                            break
                    if '-' in val_str:
                        direction = 'DEBIT'
                    elif '+' in val_str:
                        direction = 'CREDIT'
                    return to_minor_units(num_val, currency), direction

        return 0, 'DEBIT'

    @staticmethod
    def _clean_num_str(val: str) -> Optional[float]:
        """Convert currency string like '1,499.50' or '₹ 350.00' to float."""
        if not val:
            return None
        # Remove currency symbols and non-numeric chars except '.' and '-'
        clean = re.sub(r'[^\d.-]', '', val.replace(',', '').strip())
        try:
            return abs(float(clean))
        except ValueError:
            return None

    @staticmethod
    def _extract_ref_id(row_dict: Dict[str, str], narration: str) -> Optional[str]:
        """Extract UTR or Cheque/Reference number."""
        ref_keys = ['chq/ref no', 'ref no.', 'ref no', 'cheque no', 'chqno', 'reference id', 'utr']
        for k in ref_keys:
            if k in row_dict and row_dict[k] and row_dict[k] != '-':
                clean = re.sub(r'[\'"]', '', row_dict[k].strip())
                if len(clean) >= 4:
                    return clean

        # Check narration for 12-digit UTR
        utr_match = re.search(r'\b([0-9]{12})\b', narration)
        if utr_match:
            return utr_match.group(1)

        return None
