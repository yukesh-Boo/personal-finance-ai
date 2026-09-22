"""Unit tests for Financial Analytics and Statistical Forecasting Engine."""

import unittest
from decimal import Decimal
from analytics import FinancialAnalytics


class TestFinancialAnalytics(unittest.TestCase):
    def setUp(self):
        self.sample_txns = [
            {"id": "t1", "amount": "4000.00", "type": "income", "category": "Salary", "date": "2026-07-01", "description": "Paycheck"},
            {"id": "t2", "amount": "1200.00", "type": "expense", "category": "Rent", "date": "2026-07-02", "description": "Rent"},
            {"id": "t3", "amount": "300.00", "type": "expense", "category": "Groceries", "date": "2026-07-05", "description": "Store A"},
            {"id": "t4", "amount": "4000.00", "type": "income", "category": "Salary", "date": "2026-08-01", "description": "Paycheck"},
            {"id": "t5", "amount": "1200.00", "type": "expense", "category": "Rent", "date": "2026-08-02", "description": "Rent"},
            {"id": "t6", "amount": "350.00", "type": "expense", "category": "Groceries", "date": "2026-08-05", "description": "Store B"},
            {"id": "t7", "amount": "15.99", "type": "expense", "category": "Subscriptions", "date": "2026-07-10", "description": "Netflix", "recurring": "monthly"},
            {"id": "t8", "amount": "15.99", "type": "expense", "category": "Subscriptions", "date": "2026-08-10", "description": "Netflix", "recurring": "monthly"},
        ]

    def test_summary_calculation(self):
        summary = FinancialAnalytics.calculate_summary(self.sample_txns)
        self.assertEqual(summary["total_income"], "8000.00")
        self.assertEqual(summary["total_expenses"], "3081.98")
        self.assertEqual(summary["net_savings"], "4918.02")
        self.assertAlmostEqual(summary["savings_rate_pct"], 61.5, places=1)

    def test_category_breakdown(self):
        breakdown = FinancialAnalytics.category_spending_breakdown(self.sample_txns)
        categories = {b["category"]: b for b in breakdown}
        self.assertIn("Rent", categories)
        self.assertIn("Groceries", categories)
        self.assertEqual(categories["Rent"]["amount"], "2400.00")

    def test_monthly_trends(self):
        trends = FinancialAnalytics.monthly_trends(self.sample_txns)
        self.assertEqual(len(trends), 2)
        m1 = trends[0]
        self.assertEqual(m1["month"], "2026-07")
        self.assertEqual(m1["income"], "4000.00")

    def test_outlier_anomaly_detection(self):
        # Add a massive anomalous dining transaction
        txns_with_outlier = list(self.sample_txns)
        txns_with_outlier.extend([
            {"id": "d1", "amount": "45.00", "type": "expense", "category": "Dining", "date": "2026-08-01", "description": "Dinner"},
            {"id": "d2", "amount": "50.00", "type": "expense", "category": "Dining", "date": "2026-08-08", "description": "Lunch"},
            {"id": "d3", "amount": "40.00", "type": "expense", "category": "Dining", "date": "2026-08-15", "description": "Dinner"},
            {"id": "d4", "amount": "850.00", "type": "expense", "category": "Dining", "date": "2026-08-20", "description": "VIP Caviar Banquet"},
        ])

        outliers = FinancialAnalytics.detect_unusual_spending(txns_with_outlier)
        self.assertTrue(len(outliers) > 0)
        top_anomaly = outliers[0]
        self.assertEqual(top_anomaly["category"], "Dining")
        self.assertEqual(top_anomaly["amount"], "850.00")
        self.assertGreaterEqual(top_anomaly["z_score"], 1.5)

    def test_subscription_identification(self):
        subs = FinancialAnalytics.identify_subscriptions(self.sample_txns)
        self.assertTrue(any(s["name"] == "Netflix" for s in subs))

    def test_financial_health_score(self):
        health = FinancialAnalytics.compute_financial_health_score(
            transactions=self.sample_txns,
            total_liquid_balance=Decimal("15000.00"),
            budgets_eval=[],
        )
        self.assertGreaterEqual(health["score"], 70)
        self.assertIn("Grade", health["rating"])


if __name__ == "__main__":
    unittest.main()
