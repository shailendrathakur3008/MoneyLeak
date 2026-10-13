"""
Money & Currency Utilities for MoneyLeak.

Authoritative representation of money is strictly integer minor units
(e.g., paise for INR, cents for USD, yen for JPY).
Floating-point values are never used for storage or authoritative balances.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any

# Currency configuration map: symbol, decimals, name, formatting pattern
CURRENCY_CONFIG: Dict[str, Dict[str, Any]] = {
    'INR': {'symbol': '₹', 'decimals': 2, 'name': 'Indian Rupee', 'minor_name': 'paise'},
    'USD': {'symbol': '$', 'decimals': 2, 'name': 'US Dollar', 'minor_name': 'cents'},
    'EUR': {'symbol': '€', 'decimals': 2, 'name': 'Euro', 'minor_name': 'cents'},
    'GBP': {'symbol': '£', 'decimals': 2, 'name': 'British Pound', 'minor_name': 'pence'},
    'AED': {'symbol': 'د.إ', 'decimals': 2, 'name': 'UAE Dirham', 'minor_name': 'fils'},
    'JPY': {'symbol': '¥', 'decimals': 0, 'name': 'Japanese Yen', 'minor_name': 'yen'},
    'CAD': {'symbol': 'CA$', 'decimals': 2, 'name': 'Canadian Dollar', 'minor_name': 'cents'},
    'AUD': {'symbol': 'AU$', 'decimals': 2, 'name': 'Australian Dollar', 'minor_name': 'cents'},
    'SGD': {'symbol': 'SG$', 'decimals': 2, 'name': 'Singapore Dollar', 'minor_name': 'cents'},
}

DEFAULT_CURRENCY = 'INR'


def get_currency_decimals(currency_code: str = DEFAULT_CURRENCY) -> int:
    """Return number of decimal places for the given currency code."""
    config = CURRENCY_CONFIG.get(currency_code.upper(), CURRENCY_CONFIG[DEFAULT_CURRENCY])
    return config['decimals']


def get_currency_symbol(currency_code: str = DEFAULT_CURRENCY) -> str:
    """Return currency display symbol."""
    config = CURRENCY_CONFIG.get(currency_code.upper(), CURRENCY_CONFIG[DEFAULT_CURRENCY])
    return config['symbol']


def to_minor_units(amount: float | str | Decimal | int, currency_code: str = DEFAULT_CURRENCY) -> int:
    """
    Convert an input amount (major units, e.g. 1500.50) into exact integer minor units (e.g. 150050).
    Uses Decimal with ROUND_HALF_UP to avoid floating-point binary inaccuracies.
    """
    if amount is None or amount == '':
        return 0
    decimals = get_currency_decimals(currency_code)
    multiplier = Decimal(10 ** decimals)
    dec_val = Decimal(str(amount).strip().replace(',', ''))
    minor = (dec_val * multiplier).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return int(minor)


def from_minor_units(minor_units: int | None, currency_code: str = DEFAULT_CURRENCY) -> Decimal:
    """
    Convert integer minor units into high-precision Decimal major units.
    """
    if minor_units is None:
        return Decimal('0')
    decimals = get_currency_decimals(currency_code)
    divisor = Decimal(10 ** decimals)
    return Decimal(minor_units) / divisor


def format_money(minor_units: int | None, currency_code: str = DEFAULT_CURRENCY, include_symbol: bool = True) -> str:
    """
    Format minor units into user-facing human-readable string with proper commas and symbol.
    Supports Indian numbering grouping (Lakhs/Crores) for INR, and standard thousands grouping for others.
    """
    if minor_units is None:
        minor_units = 0

    decimals = get_currency_decimals(currency_code)
    symbol = get_currency_symbol(currency_code) if include_symbol else ''

    is_negative = minor_units < 0
    abs_minor = abs(minor_units)

    if decimals > 0:
        divisor = 10 ** decimals
        major_part = abs_minor // divisor
        minor_part = abs_minor % divisor
        minor_str = f"{minor_part:0{decimals}d}"
    else:
        major_part = abs_minor
        minor_str = ""

    # Indian number formatting for INR: 1,00,000 instead of 100,000
    if currency_code.upper() == 'INR':
        s = str(major_part)
        if len(s) > 3:
            last3 = s[-3:]
            rest = s[:-3]
            # split rest in groups of 2
            groups = []
            while len(rest) > 2:
                groups.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                groups.insert(0, rest)
            groups.append(last3)
            formatted_major = ",".join(groups)
        else:
            formatted_major = s
    else:
        # Standard formatting with thousands separator
        formatted_major = f"{major_part:,}"

    sign_str = "-" if is_negative else ""
    if decimals > 0:
        result = f"{sign_str}{symbol}{formatted_major}.{minor_str}".strip()
    else:
        result = f"{sign_str}{symbol}{formatted_major}".strip()

    return result
