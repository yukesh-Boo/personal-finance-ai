"""Unit and integration tests for SQLite Database operations and ACID integrity."""

import unittest
import os
import tempfile
from decimal import Decimal
from database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = DatabaseManager(db_path=self.temp_db_path)

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_account_persistence_and_retrieval(self):
        acc = {
            "id": "acc_001",
            "name": "Primary Checking",
            "type": "checking",
            "balance": "1500.00",
            "currency": "USD",
            "allow_overdraft": 0,
        }
        self.db.save_account(acc)
        retrieved = self.db.get_account("acc_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Primary Checking")
        self.assertEqual(retrieved["balance"], "1500.00")

    def test_transaction_crud_and_indexing(self):
        acc = {
            "id": "acc_002",
            "name": "Operations Checking",
            "type": "checking",
            "balance": "2000.00",
            "currency": "USD",
        }
        self.db.save_account(acc)

        txn = {
            "id": "txn_001",
            "amount": "120.50",
            "type": "expense",
            "category": "Groceries",
            "account_id": "acc_002",
            "date": "2026-09-15",
            "description": "Weekly grocery shopping",
            "payment_method": "Debit Card",
        }
        self.db.insert_transaction(txn)

        fetched = self.db.get_transaction("txn_001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["amount"], "120.50")
        self.assertEqual(fetched["category"], "Groceries")

        # Verify audit log entry was captured
        logs = self.db.get_audit_logs()
        self.assertTrue(any(log["entity_id"] == "txn_001" for log in logs))

    def test_backup_and_restore(self):
        acc = {
            "id": "acc_backup",
            "name": "Backup Test Vault",
            "type": "savings",
            "balance": "9999.00",
        }
        self.db.save_account(acc)

        backup_file = self.temp_db_path + ".bak"
        try:
            self.db.backup_to_file(backup_file)
            self.assertTrue(os.path.exists(backup_file))

            # Modify live DB
            self.db.delete_account("acc_backup")
            self.assertIsNone(self.db.get_account("acc_backup"))

            # Restore from backup
            self.db.restore_from_file(backup_file)
            restored_acc = self.db.get_account("acc_backup")
            self.assertIsNotNone(restored_acc)
            self.assertEqual(restored_acc["balance"], "9999.00")
        finally:
            if os.path.exists(backup_file):
                os.remove(backup_file)


if __name__ == "__main__":
    unittest.main()
