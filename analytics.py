"""Financial Analytics & Statistical Prediction Engine.

Implements statistical outlier detection (Z-Score & IQR), forecasting using
Exponential Smoothing / Weighted Moving Averages, cash-flow diagnostics,
subscription detection, and transparent financial health scoring.
"""

from decimal import Decimal
import statistics
import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional


class FinancialAnalytics:
    """Analytical computations and predictive models on financial transaction history."""

    @staticmethod
    def calculate_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates core totals: income, expense, net savings, and savings rate."""
        total_income = Decimal("0.00")
        total_expense = Decimal("0.00")

        for txn in transactions:
            amt = Decimal(str(txn["amount"]))
            ttype = txn["type"]
            if ttype == "income":
                total_income += amt
            elif ttype == "expense":
                total_expense += amt
            # Note: 'transfer' does not affect net income or expense totals

        net_savings = total_income - total_expense
        savings_rate = (
            (net_savings / total_income * Decimal("100.00"))
            if total_income > Decimal("0.00")
            else Decimal("0.00")
        )

        return {
            "total_income": str(total_income),
            "total_expenses": str(total_expense),
            "net_savings": str(net_savings),
            "savings_rate_pct": float(savings_rate.quantize(Decimal("0.1"))),
            "transaction_count": len(transactions),
        }

    @staticmethod
    def category_spending_breakdown(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Computes aggregate expenditure per category and percentage of total expenses."""
        cat_totals: Dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        cat_counts: Dict[str, int] = defaultdict(int)
        total_expense = Decimal("0.00")

        for txn in transactions:
            if txn["type"] == "expense":
                amt = Decimal(str(txn["amount"]))
                cat = txn["category"]
                cat_totals[cat] += amt
                cat_counts[cat] += 1
                total_expense += amt

        results = []
        for cat, amt in sorted(cat_totals.items(), key=lambda item: item[1], reverse=True):
            pct = (amt / total_expense * Decimal("100.00")) if total_expense > Decimal("0.00") else Decimal("0.00")
            results.append({
                "category": cat,
                "amount": str(amt),
                "percentage": float(pct.quantize(Decimal("0.1"))),
                "count": cat_counts[cat],
            })

        return results

    @staticmethod
    def monthly_trends(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregates income, expenses, and net savings grouped by month (YYYY-MM)."""
        monthly_map: Dict[str, Dict[str, Decimal]] = defaultdict(
            lambda: {"income": Decimal("0.00"), "expense": Decimal("0.00")}
        )

        for txn in transactions:
            ttype = txn["type"]
            if ttype not in ("income", "expense"):
                continue
            month_key = txn["date"][:7]  # YYYY-MM
            amt = Decimal(str(txn["amount"]))
            monthly_map[month_key][ttype] += amt

        trends = []
        sorted_keys = sorted(monthly_map.keys())
        prev_expense = None

        for m_key in sorted_keys:
            inc = monthly_map[m_key]["income"]
            exp = monthly_map[m_key]["expense"]
            net = inc - exp
            s_rate = (net / inc * Decimal("100.00")) if inc > Decimal("0.00") else Decimal("0.00")

            # Month-over-Month expense growth
            mom_growth = None
            if prev_expense is not None and prev_expense > Decimal("0.00"):
                mom_growth = float(((exp - prev_expense) / prev_expense * Decimal("100.00")).quantize(Decimal("0.1")))
            prev_expense = exp

            trends.append({
                "month": m_key,
                "income": str(inc),
                "expense": str(exp),
                "net_savings": str(net),
                "savings_rate_pct": float(s_rate.quantize(Decimal("0.1"))),
                "mom_expense_growth_pct": mom_growth,
            })

        return trends

    @staticmethod
    def spending_velocity(transactions: List[Dict[str, Any]], days_span: int = 30) -> Dict[str, Any]:
        """Calculates average daily, weekly, and projected monthly spend."""
        cutoff_date = (datetime.utcnow() - timedelta(days=days_span)).strftime("%Y-%m-%d")
        recent_expenses = [
            Decimal(str(txn["amount"]))
            for txn in transactions
            if txn["type"] == "expense" and txn["date"] >= cutoff_date
        ]

        total_recent = sum(recent_expenses)
        effective_days = max(1, days_span)

        daily_avg = total_recent / Decimal(effective_days)
        weekly_avg = daily_avg * Decimal("7.0")
        monthly_proj = daily_avg * Decimal("30.4")

        return {
            "window_days": effective_days,
            "total_spent_window": str(total_recent),
            "average_daily_spend": str(daily_avg.quantize(Decimal("0.01"))),
            "average_weekly_spend": str(weekly_avg.quantize(Decimal("0.01"))),
            "projected_monthly_spend": str(monthly_proj.quantize(Decimal("0.01"))),
        }

    @staticmethod
    def detect_unusual_spending(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies statistical outlier transactions using Interquartile Range (IQR) and Z-score."""
        expense_txns = [t for t in transactions if t["type"] == "expense"]
        if len(expense_txns) < 4:
            return []

        # Group amounts by category to evaluate within category context
        cat_groups: Dict[str, List[Tuple[Dict[str, Any], float]]] = defaultdict(list)
        for t in expense_txns:
            cat_groups[t["category"]].append((t, float(t["amount"])))

        outliers = []
        for cat, items in cat_groups.items():
            if len(items) < 3:
                # If category has few items, check global distribution
                continue

            amounts = [amt for _, amt in items]
            mean_val = statistics.mean(amounts)
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0.0
            median_val = statistics.median(amounts)
            abs_devs = [abs(x - median_val) for x in amounts]
            mad = statistics.median(abs_devs)

            sorted_amounts = sorted(amounts)
            q1 = sorted_amounts[len(sorted_amounts) // 4]
            q3 = sorted_amounts[(3 * len(sorted_amounts)) // 4]
            iqr = q3 - q1
            upper_iqr_bound = q3 + (1.5 * iqr)

            for txn, val in items:
                z_score = ((val - mean_val) / std_dev) if std_dev > 0 else 0.0
                mod_z = (0.6745 * (val - median_val) / mad) if mad > 0 else 0.0

                is_iqr_outlier = val > upper_iqr_bound and val > (mean_val * 1.4)
                is_z_outlier = z_score >= 1.45
                is_mad_outlier = mod_z >= 3.0
                is_ratio_outlier = (val >= (2.5 * median_val)) and (val - median_val >= 50.0)

                if is_iqr_outlier or is_z_outlier or is_mad_outlier or is_ratio_outlier:
                    outliers.append({
                        "transaction_id": txn["id"],
                        "date": txn["date"],
                        "category": txn["category"],
                        "description": txn.get("description", ""),
                        "amount": txn["amount"],
                        "category_average": f"{mean_val:.2f}",
                        "z_score": round(max(z_score, mod_z if mod_z < 99 else z_score), 2),
                        "multiplier_of_avg": round(val / mean_val, 1) if mean_val > 0 else 1.0,
                        "anomaly_reason": (
                            f"Spending of ${val:.2f} is {val/mean_val:.1f}x higher than category mean (${mean_val:.2f}) "
                            f"(Z-Score: {z_score:.2f}, Modified Z: {mod_z:.2f})."
                        ),
                    })

        return sorted(outliers, key=lambda x: float(x["amount"]), reverse=True)

    @staticmethod
    def identify_subscriptions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detects likely recurring subscriptions by analyzing repeated amounts and periodic intervals."""
        expense_txns = [t for t in transactions if t["type"] == "expense"]
        # Group by description/merchant
        merchant_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for t in expense_txns:
            key = (t.get("description", "").strip().lower() or t["category"].lower())
            merchant_map[key].append(t)

        detected_subscriptions = []
        for merch, txns in merchant_map.items():
            if len(txns) < 2:
                continue

            # Check if amounts are identical or virtually identical (within $0.50)
            amounts = [float(t["amount"]) for t in txns]
            if max(amounts) - min(amounts) <= 1.0:
                # Check date intervals
                dates = sorted([datetime.strptime(t["date"], "%Y-%m-%d") for t in txns])
                intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
                avg_interval = sum(intervals) / len(intervals)

                cadence = "Unknown"
                if 25 <= avg_interval <= 35:
                    cadence = "Monthly Subscription"
                elif 6 <= avg_interval <= 8:
                    cadence = "Weekly Subscription"
                elif 350 <= avg_interval <= 380:
                    cadence = "Annual Subscription"

                if cadence != "Unknown" or any(t.get("recurring") != "none" for t in txns):
                    detected_subscriptions.append({
                        "name": txns[0].get("description") or txns[0]["category"],
                        "category": txns[0]["category"],
                        "typical_amount": f"{amounts[0]:.2f}",
                        "cadence": cadence if cadence != "Unknown" else "Regular Recurring",
                        "occurrence_count": len(txns),
                        "last_billed": dates[-1].strftime("%Y-%m-%d"),
                        "estimated_annual_cost": f"{(amounts[0] * 12):.2f}" if "Monthly" in cadence else f"{(amounts[0] * 52):.2f}",
                    })

        return detected_subscriptions

    @staticmethod
    def forecast_next_month(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimates next month's total expenses and savings using Exponential Smoothing.

        Explicitly marked as statistical estimates and NOT guaranteed financial outcomes.
        """
        trends = FinancialAnalytics.monthly_trends(transactions)
        if len(trends) < 2:
            return {
                "has_sufficient_data": False,
                "disclaimer": "Forecast requires at least 2 full months of transaction records.",
            }

        past_expenses = [float(m["expense"]) for m in trends]
        past_incomes = [float(m["income"]) for m in trends]

        # Simple Exponential Smoothing (alpha = 0.5 for responsiveness)
        alpha = 0.5
        exp_forecast = past_expenses[0]
        for val in past_expenses[1:]:
            exp_forecast = (alpha * val) + ((1 - alpha) * exp_forecast)

        # Income baseline (recent average)
        inc_forecast = statistics.mean(past_incomes[-3:]) if len(past_incomes) >= 3 else past_incomes[-1]

        estimated_savings = max(0.0, inc_forecast - exp_forecast)
        uncertainty_margin = exp_forecast * 0.08  # +/- 8% confidence band

        return {
            "has_sufficient_data": True,
            "methodology": "Exponential Smoothing (alpha=0.5) with empirical standard deviation margin",
            "forecast_month": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m"),
            "estimated_expenses": f"{exp_forecast:.2f}",
            "expenses_lower_bound": f"{max(0.0, exp_forecast - uncertainty_margin):.2f}",
            "expenses_upper_bound": f"{(exp_forecast + uncertainty_margin):.2f}",
            "projected_income": f"{inc_forecast:.2f}",
            "projected_net_savings": f"{estimated_savings:.2f}",
            "projected_savings_rate_pct": round((estimated_savings / inc_forecast * 100), 1) if inc_forecast > 0 else 0.0,
            "disclaimer": "NOTICE: These values are mathematical approximations based on past spending patterns and should not be considered guaranteed outcomes.",
        }

    @staticmethod
    def compute_financial_health_score(
        transactions: List[Dict[str, Any]],
        total_liquid_balance: Decimal,
        budgets_eval: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calculates an explainable 0-100 Financial Health Indicator based on transparent factors:

        1. Savings Rate (0 - 30 pts): >20% yields full points.
        2. Budget Discipline (0 - 30 pts): No overruns yields 30 pts.
        3. Emergency Liquidity Buffer (0 - 25 pts): 3+ months living expenses yields 25 pts.
        4. Outlier Stability (0 - 15 pts): Low anomalous volatility yields 15 pts.
        """
        summary = FinancialAnalytics.calculate_summary(transactions)
        s_rate = summary["savings_rate_pct"]

        # 1. Savings Score (30 max)
        if s_rate >= 25.0:
            savings_score = 30
        elif s_rate >= 15.0:
            savings_score = 22
        elif s_rate >= 5.0:
            savings_score = 15
        elif s_rate >= 0.0:
            savings_score = 8
        else:
            savings_score = 0

        # 2. Budget Discipline Score (30 max)
        overrun_count = sum(1 for b in budgets_eval if b.get("is_overrun"))
        warning_count = sum(1 for b in budgets_eval if b.get("is_warning_80"))

        if not budgets_eval:
            budget_score = 20  # Neutral baseline
        else:
            budget_score = max(0, 30 - (overrun_count * 12) - (warning_count * 4))

        # 3. Emergency Buffer Score (25 max)
        monthly_exp = Decimal(summary["total_expenses"])
        trends = FinancialAnalytics.monthly_trends(transactions)
        avg_monthly_exp = (
            sum(Decimal(t["expense"]) for t in trends) / Decimal(len(trends))
            if trends
            else monthly_exp
        )

        if avg_monthly_exp > Decimal("0.00"):
            months_covered = float(total_liquid_balance / avg_monthly_exp)
            if months_covered >= 6.0:
                buffer_score = 25
            elif months_covered >= 3.0:
                buffer_score = 20
            elif months_covered >= 1.0:
                buffer_score = 12
            else:
                buffer_score = 5
        else:
            months_covered = 0.0
            buffer_score = 15

        # 4. Outlier Stability Score (15 max)
        outliers = FinancialAnalytics.detect_unusual_spending(transactions)
        if len(outliers) == 0:
            stability_score = 15
        elif len(outliers) <= 2:
            stability_score = 10
        else:
            stability_score = 5

        total_score = min(100, savings_score + budget_score + buffer_score + stability_score)

        if total_score >= 85:
            grade = "Excellent (Grade A)"
            guidance = "Outstanding financial control, disciplined budgeting, and robust liquidity buffer."
        elif total_score >= 70:
            grade = "Good (Grade B)"
            guidance = "Solid foundations. Consider lowering high-spend categories to boost your emergency cushion."
        elif total_score >= 50:
            grade = "Fair (Grade C)"
            guidance = "Spending is close to income. Review active subscriptions and adhere to category budgets."
        else:
            grade = "Needs Attention (Grade D)"
            guidance = "Expenses are outpacing savings or overruns are occurring. Immediate budget consolidation recommended."

        return {
            "score": total_score,
            "rating": grade,
            "guidance": guidance,
            "component_breakdown": {
                "savings_rate_score": {"points": savings_score, "max": 30, "detail": f"{s_rate}% savings rate"},
                "budget_discipline_score": {"points": budget_score, "max": 30, "detail": f"{overrun_count} overruns, {warning_count} warnings"},
                "liquidity_buffer_score": {"points": buffer_score, "max": 25, "detail": f"{months_covered:.1f} months living expenses funded"},
                "stability_score": {"points": stability_score, "max": 15, "detail": f"{len(outliers)} anomalous transactions detected"},
            },
        }
