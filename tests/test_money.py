from decimal import Decimal
from app.services.money import to_minor_units, from_minor_units, format_money, get_currency_decimals


def test_minor_unit_conversions():
    # INR: 2 decimals
    assert to_minor_units(40000, 'INR') == 4000000
    assert to_minor_units('1500.50', 'INR') == 150050
    assert from_minor_units(150050, 'INR') == Decimal('1500.50')

    # USD: 2 decimals
    assert to_minor_units('12.99', 'USD') == 1299
    assert from_minor_units(1299, 'USD') == Decimal('12.99')

    # JPY: 0 decimals
    assert to_minor_units('5000', 'JPY') == 5000
    assert from_minor_units(5000, 'JPY') == Decimal('5000')


def test_money_formatting():
    # INR Indian numbering commas
    assert format_money(10000000, 'INR') == '₹1,00,000.00'
    assert format_money(4000000, 'INR') == '₹40,000.00'
    assert format_money(1250, 'INR') == '₹12.50'

    # USD standard commas
    assert format_money(10000000, 'USD') == '$100,000.00'

    # JPY zero decimals
    assert format_money(5000, 'JPY') == '¥5,000'

    # Negative amount
    assert format_money(-150000, 'INR') == '-₹1,500.00'
