"""
Reports routes and export downloads (CSV and PDF).
"""
from datetime import date
from flask import Blueprint, render_template, request, jsonify, g, send_file, Response
from app.routes.auth import login_required
from app.services.budget_engine import calculate_budget_summary
from app.services.report_service import generate_transactions_csv, generate_monthly_pdf_report

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def view_reports():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    summary = calculate_budget_summary(user.id, year, month)
    return render_template('reports.html', user=user, summary=summary, current_year=year, current_month=month)


@reports_bp.route('/api/reports/monthly', methods=['GET'])
@login_required
def api_monthly_report():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    summary = calculate_budget_summary(user.id, year, month)
    return jsonify({'success': True, 'report': summary})


@reports_bp.route('/api/reports/export/csv', methods=['GET'])
@login_required
def export_csv():
    user = g.current_user
    year = request.args.get('year')
    month = request.args.get('month')

    y = int(year) if year and year.isdigit() else None
    m = int(month) if month and month.isdigit() else None

    csv_buffer = generate_transactions_csv(user.id, y, m)

    period_str = f"{y}_{m:02d}" if y and m else "all_time"
    filename = f"MoneyLeak_transactions_{user.id}_{period_str}.csv"

    return Response(
        csv_buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@reports_bp.route('/api/reports/export/pdf', methods=['GET'])
@login_required
def export_pdf():
    user = g.current_user
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    pdf_buffer = generate_monthly_pdf_report(user.id, year, month)
    filename = f"MoneyLeak_Financial_Report_{year}_{month:02d}.pdf"

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
