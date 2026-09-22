"""Unit tests for Budget Domain and Evaluation Engine."""

import unittest
from decimal import Decimal
from budget import Budget, BudgetPeriod


class TestBudgetSystem(unittest.TestCase):
    def test_budget_utilization_under_limit(self):
        b = Budget("Groceries", Decimal("500.00"), period=BudgetPeriod.MONTHLY)
        eval_res = b.evaluate(Decimal("250.00"))
        self.assertEqual(eval_res["utilization_percentage"], 50.0)
        self.assertFalse(eval_res["is_warning_80"])
        self.assertFalse(eval_res["is_overrun"])
        self.assertEqual(eval_res["status"], "HEALTHY")

    def test_budget_80_percent_warning_trigger(self):
        b = Budget("Entertainment", Decimal("200.00"), period=BudgetPeriod.MONTHLY)
        eval_res = b.evaluate(Decimal("165.00"))
        self.assertEqual(eval_res["utilization_percentage"], 82.5)
        self.assertTrue(eval_res["is_warning_80"])
        self.assertFalse(eval_res["is_overrun"])
        self.assertEqual(eval_res["status"], "WARNING")

    def test_budget_overrun_detection(self):
        b = Budget("Dining", Decimal("300.00"), period=BudgetPeriod.MONTHLY)
        eval_res = b.evaluate(Decimal("350.00"))
        self.assertGreater(eval_res["utilization_percentage"], 100.0)
        self.assertTrue(eval_res["is_overrun"])
        self.assertEqual(eval_res["overrun_amount"], "50.00")
        self.assertEqual(eval_res["status"], "OVERRUN")

    def test_budget_rollover_carryforward(self):
        # A budget with $100 positive rollover balance
        b = Budget("Utilities", Decimal("200.00"), rollover_amount=Decimal("50.00"))
        self.assertEqual(b.effective_limit, Decimal("250.00"))
        eval_res = b.evaluate(Decimal("220.00"))
        # Within effective limit of 250, so NOT overrun
        self.assertFalse(eval_res["is_overrun"])
        self.assertEqual(eval_res["remaining"], "30.00")

    def test_budget_adjustment_recommendation(self):
        b = Budget("Groceries", Decimal("300.00"))
        # Historical spending is consistently ~$450
        history = [Decimal("440.00"), Decimal("460.00"), Decimal("450.00")]
        rec = b.recommend_adjustment(history)
        self.assertIn("raising limit", rec["reason"].lower())
        self.assertGreater(Decimal(rec["recommended_limit"]), Decimal("300.00"))


if __name__ == "__main__":
    unittest.main()
