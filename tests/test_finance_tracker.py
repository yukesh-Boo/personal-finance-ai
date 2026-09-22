"""Unit and integration tests for FinanceTracker core engine."""

import unittest
import os
import tempfile
from decimal import Decimal
from finance_tracker import FinanceTracker
from exceptions import (
    InsufficientFundsError,
    ValidationError,
    AccountNotFoundError,
    TransactionNotFoundError,
)
from account import CheckingAccount, SavingsAccount, CashAccount


class TestFinanceTrackerCore(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.tracker = FinanceTracker(db_path=self.temp_db_path)
        self.checking = self.tracker.add_account("Test Checking", "checking", Decimal("1000.00"), allow_overdraft=False)
        self.savings = self.tracker.add_account("Test Savings", "savings", Decimal("500.00"))

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_account_creation_and_balance(self):
        self.assertEqual(self.checking.balance, Decimal("1000.00"))
        self.assertEqual(self.savings.balance, Decimal("500.00"))
        self.assertIsInstance(self.checking, CheckingAccount)
        self.assertIsInstance(self.savings, SavingsAccount)

    def test_add_income_transaction(self):
        txn = self.tracker.add_transaction(
            amount=Decimal("250.00"),
            transaction_type="income",
            category="Salary",
            account_id=self.checking.id,
            date_str="2026-09-01",
            description="Consulting Bonus",
        )
        self.assertEqual(txn.amount, Decimal("250.00"))
        self.assertEqual(self.checking.balance, Decimal("1250.00"))

    def test_add_expense_transaction(self):
        txn = self.tracker.add_transaction(
            amount=Decimal("150.00"),
            transaction_type="expense",
            category="Groceries",
            account_id=self.checking.id,
            date_str="2026-09-02",
        )
        self.assertEqual(txn.amount, Decimal("150.00"))
        self.assertEqual(self.checking.balance, Decimal("850.00"))

    def test_insufficient_funds_rejection(self):
        with self.assertRaises(InsufficientFundsError):
            self.tracker.add_transaction(
                amount=Decimal("2000.00"),
                transaction_type="expense",
                category="Luxury",
                account_id=self.checking.id,
            )
        # Verify balance was unaffected
        self.assertEqual(self.checking.balance, Decimal("1000.00"))

    def test_inter_account_transfer(self):
        """Verifies transfers atomically move funds between accounts without altering net wealth."""
        total_before = self.checking.balance + self.savings.balance

        transfer_txn = self.tracker.transfer(
            from_account_id=self.checking.id,
            to_account_id=self.savings.id,
            amount=Decimal("300.00"),
            description="Emergency Fund Transfer",
        )

        self.assertEqual(transfer_txn.amount, Decimal("300.00"))
        self.assertEqual(self.checking.balance, Decimal("700.00"))
        self.assertEqual(self.savings.balance, Decimal("800.00"))

        total_after = self.checking.balance + self.savings.balance
        self.assertEqual(total_before, total_after)

        # Confirm summary does not classify transfer as expense or income
        dossier = self.tracker.get_analytics_dossier()
        self.assertEqual(Decimal(dossier["summary"]["total_income"]), Decimal("0.00"))
        self.assertEqual(Decimal(dossier["summary"]["total_expenses"]), Decimal("0.00"))

    def test_negative_or_zero_amount_rejection(self):
        with self.assertRaises(ValidationError):
            self.tracker.add_transaction(
                amount=Decimal("-50.00"),
                transaction_type="expense",
                category="Groceries",
                account_id=self.checking.id,
            )

        with self.assertRaises(ValidationError):
            self.tracker.add_transaction(
                amount=Decimal("0.00"),
                transaction_type="income",
                category="Salary",
                account_id=self.checking.id,
            )

    def test_invalid_date_format(self):
        with self.assertRaises(ValidationError):
            self.tracker.add_transaction(
                amount=Decimal("50.00"),
                transaction_type="expense",
                category="Dining",
                account_id=self.checking.id,
                date_str="09/21/2026",  # Not ISO YYYY-MM-DD
            )

    def test_transaction_deletion_and_reconciliation(self):
        txn = self.tracker.add_transaction(
            amount=Decimal("200.00"),
            transaction_type="expense",
            category="Shopping",
            account_id=self.checking.id,
        )
        self.assertEqual(self.checking.balance, Decimal("800.00"))

        # Delete transaction
        self.tracker.delete_transaction(txn.id)
        # Balance restored to 1000.00
        self.assertEqual(self.checking.balance, Decimal("1000.00"))


if __name__ == "__main__":
    unittest.main()
