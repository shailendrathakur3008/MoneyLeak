"""
Report Generation Service for MoneyLeak.

Generates CSV exports and downloadable PDF summaries using ReportLab.
Uses the unified budget calculation engine to guarantee data consistency.
"""
import io
import csv
from datetime import date
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.extensions import db
from app.models.user import User
from app.models.transaction import Transaction
from app.services.budget_engine import calculate_budget_summary, get_month_date_range
from app.services.money import format_money


def generate_transactions_csv(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> io.StringIO:
    """Generate CSV string buffer containing user transactions."""
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("User not found")

    query = Transaction.query.filter_by(user_id=user_id)
    if year and month:
        start_date, end_date = get_month_date_range(year, month)
        query = query.filter(Transaction.transaction_date >= start_date, Transaction.transaction_date <= end_date)

    txns = query.order_by(Transaction.transaction_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Transaction ID', 'Date', 'Type', 'Category', 'Budget Group',
        f'Amount ({user.currency})', 'Merchant', 'Description', 'Notes'
    ])

    for t in txns:
        cat_name = t.category.name if t.category else 'Uncategorized'
        b_group = t.category.budget_group if t.category else 'WANTS'
        amt_str = format_money(t.amount_minor_units, user.currency, include_symbol=False)
        writer.writerow([
            t.id,
            t.transaction_date.isoformat(),
            t.transaction_type,
            cat_name,
            b_group,
            amt_str,
            t.merchant or '',
            t.description or '',
            t.notes or ''
        ])

    output.seek(0)
    return output


def generate_monthly_pdf_report(user_id: int, year: int, month: int) -> io.BytesIO:
    """Generate high-quality PDF report buffer summarizing monthly finances and 50/30/20 performance."""
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("User not found")

    summary = calculate_budget_summary(user_id, year, month)
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#161917'),
        spaceAfter=4
    )
    subhead_style = ParagraphStyle(
        'DocSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=14
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#161917'),
        spaceBefore=12,
        spaceAfter=8
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#1f2937')
    )
    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#111827')
    )

    story = []

    # Header
    story.append(Paragraph(f"MoneyLeak Financial Intelligence Report", header_style))
    month_name = date(year, month, 1).strftime("%B %Y")
    story.append(Paragraph(f"Prepared for: <b>{user.full_name}</b> ({user.email}) | Statement Period: <b>{month_name}</b>", subhead_style))
    story.append(Spacer(1, 10))

    # Executive KPI Summary Table
    story.append(Paragraph("1. Executive Summary & Cashflow", section_title))
    kpi_data = [
        [Paragraph("Metric", cell_bold), Paragraph("Amount", cell_bold), Paragraph("Percentage of Income", cell_bold)],
        [Paragraph("Recognized Monthly Income", cell_style), Paragraph(summary['income']['formatted'], cell_style), Paragraph("100%", cell_style)],
        [Paragraph("Total Outflows (Consumption + Savings)", cell_style), Paragraph(summary['total_outflow']['formatted'], cell_style), Paragraph(f"{(summary['total_outflow']['minor']/summary['income']['minor']*100):.1f}%" if summary['income']['minor']>0 else "0%", cell_style)],
        [Paragraph("Consumption Expenses", cell_style), Paragraph(summary['expenses']['formatted'], cell_style), Paragraph(f"{(summary['expenses']['minor']/summary['income']['minor']*100):.1f}%" if summary['income']['minor']>0 else "0%", cell_style)],
        [Paragraph("Actual Savings Contributed", cell_style), Paragraph(summary['actual_savings']['formatted'], cell_style), Paragraph(f"{summary['savings_rate']}%", cell_style)],
        [Paragraph("Net Monthly Surplus", cell_bold), Paragraph(summary['surplus']['formatted'], cell_bold), Paragraph(f"{(summary['surplus']['minor']/summary['income']['minor']*100):.1f}%" if summary['income']['minor']>0 else "0%", cell_bold)],
    ]
    t_kpi = Table(kpi_data, colWidths=[240, 150, 150])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # 50/30/20 Budget Distribution Table
    story.append(Paragraph("2. 50/30/20 Budget Framework Analysis", section_title))
    budget_data = [
        [Paragraph("Bucket", cell_bold), Paragraph("Target %", cell_bold), Paragraph("Target Budget", cell_bold), Paragraph("Actual Spent", cell_bold), Paragraph("Variance", cell_bold)],
        [
            Paragraph("Needs (Essentials)", cell_style),
            Paragraph(f"{summary['distribution_targets']['needs_pct']}%", cell_style),
            Paragraph(summary['needs']['target_formatted'], cell_style),
            Paragraph(summary['needs']['actual_formatted'], cell_style),
            Paragraph(f"{'+' if summary['needs']['variance_minor']>0 else ''}{format_money(summary['needs']['variance_minor'], user.currency)}", cell_style)
        ],
        [
            Paragraph("Wants (Discretionary)", cell_style),
            Paragraph(f"{summary['distribution_targets']['wants_pct']}%", cell_style),
            Paragraph(summary['wants']['target_formatted'], cell_style),
            Paragraph(summary['wants']['actual_formatted'], cell_style),
            Paragraph(f"{'+' if summary['wants']['variance_minor']>0 else ''}{format_money(summary['wants']['variance_minor'], user.currency)}", cell_style)
        ],
        [
            Paragraph("Savings & Investments", cell_style),
            Paragraph(f"{summary['distribution_targets']['savings_pct']}%", cell_style),
            Paragraph(summary['savings']['target_formatted'], cell_style),
            Paragraph(summary['savings']['actual_formatted'], cell_style),
            Paragraph(f"Gap: {summary['savings']['gap_formatted']}", cell_style)
        ]
    ]
    t_budget = Table(budget_data, colWidths=[130, 80, 110, 110, 110])
    t_budget.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_budget)
    story.append(Spacer(1, 14))

    # Category Breakdown Table
    story.append(Paragraph("3. Category-Level Spending Breakdown", section_title))
    cat_rows = [
        [Paragraph("Category", cell_bold), Paragraph("Group", cell_bold), Paragraph("Total Spent", cell_bold), Paragraph("Share of Income", cell_bold), Paragraph("Tx Count", cell_bold)]
    ]
    for c in summary['category_breakdown'][:10]:  # Top 10 categories
        cat_rows.append([
            Paragraph(c['name'], cell_style),
            Paragraph(c['group'], cell_style),
            Paragraph(c['formatted_amount'], cell_style),
            Paragraph(f"{c['share_of_income_pct']}%", cell_style),
            Paragraph(str(c['tx_count']), cell_style)
        ])
    if not summary['category_breakdown']:
        cat_rows.append([Paragraph("No transactions recorded for this period.", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style)])

    t_cat = Table(cat_rows, colWidths=[160, 90, 130, 100, 60])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 15))

    # Footer note
    footer_text = Paragraph(
        "<i>Generated by MoneyLeak Personal Finance Intelligence. Data is strictly confidential and strictly derived from authenticated user records.</i>",
        subhead_style
    )
    story.append(footer_text)

    doc.build(story)
    buffer.seek(0)
    return buffer
