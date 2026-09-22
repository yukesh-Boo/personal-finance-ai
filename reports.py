"""Financial reporting and export engine.

Generates comprehensive audit-ready financial statements, CSV exports,
tabular text reports, and styled HTML/PDF-ready documents.
"""

import csv
import io
import json
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime


class ReportGenerator:
    """Produces multi-format reports from financial data structures."""

    @staticmethod
    def generate_csv_transactions(transactions: List[Dict[str, Any]]) -> str:
        """Exports transaction history into standard RFC-4180 CSV format."""
        output = io.StringIO()
        fieldnames = [
            "id",
            "date",
            "type",
            "category",
            "amount",
            "account_id",
            "target_account_id",
            "description",
            "payment_method",
            "recurring",
            "created_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        for t in transactions:
            row = {k: t.get(k, "") for k in fieldnames}
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def generate_text_summary_report(
        summary: Dict[str, Any],
        accounts: List[Dict[str, Any]],
        category_breakdown: List[Dict[str, Any]],
        budget_evaluations: List[Dict[str, Any]],
        health: Dict[str, Any],
    ) -> str:
        """Produces a clean CLI text report with financial metrics."""
        divider = "=" * 65
        subdivider = "-" * 65
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            divider,
            "         SMART PERSONAL FINANCE TRACKER - EXECUTIVE REPORT",
            divider,
            f"Generated: {now_str}",
            "",
            "1. FINANCIAL SNAPSHOT",
            subdivider,
            f"  Total Income:         ${Decimal(summary['total_income']):,.2f}",
            f"  Total Expenses:       ${Decimal(summary['total_expenses']):,.2f}",
            f"  Net Savings:          ${Decimal(summary['net_savings']):,.2f}",
            f"  Savings Rate:         {summary['savings_rate_pct']:.1f}%",
            f"  Total Transactions:   {summary['transaction_count']}",
            "",
            "2. ACCOUNT BALANCES",
            subdivider,
        ]

        total_assets = Decimal("0.00")
        for acc in accounts:
            bal = Decimal(acc["balance"])
            total_assets += bal
            lines.append(f"  [{acc['type'].upper():<10}] {acc['name']:<25} ${bal:,.2f} ({acc.get('currency', 'USD')})")
        lines.append(f"  TOTAL LIQUID WEALTH:                ${total_assets:,.2f}")

        lines.extend(["", "3. TOP SPENDING CATEGORIES", subdivider])
        for c in category_breakdown[:6]:
            amt = Decimal(c["amount"])
            lines.append(f"  {c['category']:<25} ${amt:,.2f}  ({c['percentage']:.1f}%) [{c['count']} txns]")

        lines.extend(["", "4. BUDGET STATUS", subdivider])
        if not budget_evaluations:
            lines.append("  No active budgets configured.")
        else:
            for b in budget_evaluations:
                status_symbol = "❌" if b["is_overrun"] else ("⚠️" if b["is_warning_80"] else "✅")
                lines.append(
                    f"  {status_symbol} {b['category']:<20} Spent: ${Decimal(b['actual_spent']):,.2f} / "
                    f"${Decimal(b['effective_limit']):,.2f} ({b['utilization_percentage']:.1f}%) - {b['status']}"
                )

        lines.extend([
            "",
            "5. FINANCIAL HEALTH SCORECARD",
            subdivider,
            f"  Overall Score:        {health['score']}/100",
            f"  Rating:               {health['rating']}",
            f"  Advisory Guidance:    {health['guidance']}",
            divider,
        ])

        return "\n".join(lines)

    @staticmethod
    def generate_html_report(
        summary: Dict[str, Any],
        accounts: List[Dict[str, Any]],
        category_breakdown: List[Dict[str, Any]],
        budget_evaluations: List[Dict[str, Any]],
        trends: List[Dict[str, Any]],
        outliers: List[Dict[str, Any]],
        subscriptions: List[Dict[str, Any]],
        health: Dict[str, Any],
    ) -> str:
        """Produces a responsive, printable HTML executive financial report."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Smart Personal Finance Tracker - Executive Financial Statement</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 30px; }}
    .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }}
    h1 {{ font-size: 26px; color: #0f172a; margin: 0 0 6px 0; }}
    .meta {{ font-size: 13px; color: #64748b; }}
    .cards-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }}
    .card {{ background: #f1f5f9; border-radius: 8px; padding: 18px; }}
    .card-label {{ font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 6px; }}
    .card-val {{ font-size: 22px; font-weight: 700; color: #0f172a; }}
    .text-green {{ color: #16a34a; }}
    .text-red {{ color: #dc2626; }}
    .section-title {{ font-size: 18px; font-weight: 700; margin: 28px 0 14px 0; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 14px; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #f1f5f9; }}
    th {{ background: #f8fafc; color: #475569; font-weight: 600; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
    .badge-ok {{ background: #dcfce7; color: #166534; }}
    .badge-warn {{ background: #fef9c3; color: #854d0e; }}
    .badge-danger {{ background: #fee2e2; color: #991b1b; }}
    .health-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 20px; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1>Smart Personal Finance Tracker</h1>
        <div class="meta">Automated Financial Statement & Analytics Dossier</div>
      </div>
      <div class="meta">Date: {datetime.utcnow().strftime("%B %d, %Y")}</div>
    </div>

    <div class="cards-grid">
      <div class="card">
        <div class="card-label">Total Income</div>
        <div class="card-val text-green">${Decimal(summary['total_income']):,.2f}</div>
      </div>
      <div class="card">
        <div class="card-label">Total Expenses</div>
        <div class="card-val text-red">${Decimal(summary['total_expenses']):,.2f}</div>
      </div>
      <div class="card">
        <div class="card-label">Net Savings</div>
        <div class="card-val">${Decimal(summary['net_savings']):,.2f}</div>
      </div>
      <div class="card">
        <div class="card-label">Savings Rate</div>
        <div class="card-val">{summary['savings_rate_pct']}%</div>
      </div>
    </div>

    <div class="section-title">Account Holdings</div>
    <table>
      <thead>
        <tr><th>Account Name</th><th>Type</th><th>Currency</th><th>Current Balance</th></tr>
      </thead>
      <tbody>
        {"".join(f"<tr><td><strong>{a['name']}</strong></td><td>{a['type'].title()}</td><td>{a.get('currency', 'USD')}</td><td>${Decimal(a['balance']):,.2f}</td></tr>" for a in accounts)}
      </tbody>
    </table>

    <div class="section-title">Category Spending Allocation</div>
    <table>
      <thead>
        <tr><th>Category</th><th>Spent Amount</th><th>Allocation</th><th>Transaction Count</th></tr>
      </thead>
      <tbody>
        {"".join(f"<tr><td>{c['category']}</td><td>${Decimal(c['amount']):,.2f}</td><td>{c['percentage']}%</td><td>{c['count']}</td></tr>" for c in category_breakdown)}
      </tbody>
    </table>

    <div class="section-title">Budget Performance</div>
    <table>
      <thead>
        <tr><th>Category</th><th>Spent</th><th>Effective Limit</th><th>Utilization</th><th>Status</th></tr>
      </thead>
      <tbody>
        {"".join(f"<tr><td>{b['category']}</td><td>${Decimal(b['actual_spent']):,.2f}</td><td>${Decimal(b['effective_limit']):,.2f}</td><td>{b['utilization_percentage']}%</td><td><span class='badge badge-{'danger' if b['is_overrun'] else ('warn' if b['is_warning_80'] else 'ok')}'>{b['status']}</span></td></tr>" for b in budget_evaluations) if budget_evaluations else "<tr><td colspan='5'>No active budgets configured.</td></tr>"}
      </tbody>
    </table>

    <div class="health-box">
      <h3 style="margin: 0 0 8px 0; color: #1e3a8a;">Financial Health Score: {health['score']} / 100 ({health['rating']})</h3>
      <p style="margin: 0; font-size: 14px; color: #1e40af;">{health['guidance']}</p>
    </div>
  </div>
</body>
</html>
"""
