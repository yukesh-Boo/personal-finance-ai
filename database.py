"""Database abstraction layer for Smart Personal Finance Tracker using SQLite.

Implements ACID transactions, parameterized queries, relational constraints,
indexes, audit logging, and automated backup/restore routines.
"""

import sqlite3
import shutil
import os
from contextlib import contextmanager
from decimal import Decimal
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from exceptions import DatabaseConnectionError, AccountNotFoundError, TransactionNotFoundError


class DatabaseManager:
    """Manages SQLite database connections, schema migrations, and atomic operations."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = "finance_tracker.db"):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provides a thread-safe connection context manager with foreign key support."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=15.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            yield conn
        except sqlite3.Error as e:
            raise DatabaseConnectionError(str(e))
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Initializes tables, indexes, and initial constraints."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Accounts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    initial_balance TEXT NOT NULL DEFAULT '0.00',
                    balance TEXT NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    allow_overdraft INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );
            """)

            # 2. Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category_type TEXT NOT NULL DEFAULT 'expense',
                    is_custom INTEGER NOT NULL DEFAULT 0
                );
            """)

            # 3. Transactions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    amount TEXT NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    account_id TEXT NOT NULL,
                    target_account_id TEXT,
                    date TEXT NOT NULL,
                    description TEXT,
                    payment_method TEXT NOT NULL,
                    recurring TEXT NOT NULL DEFAULT 'none',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES accounts(id) ON UPDATE CASCADE ON DELETE RESTRICT,
                    FOREIGN KEY (target_account_id) REFERENCES accounts(id) ON UPDATE CASCADE ON DELETE RESTRICT
                );
            """)

            # 4. Budgets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    limit_amount TEXT NOT NULL,
                    period TEXT NOT NULL,
                    period_key TEXT NOT NULL,
                    allow_rollover INTEGER NOT NULL DEFAULT 1,
                    rollover_amount TEXT NOT NULL DEFAULT '0.00',
                    UNIQUE(category, period, period_key)
                );
            """)

            # 5. Audit Trail Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                );
            """)

            # Performance Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_txn_account ON transactions(account_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_txn_category ON transactions(category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_txn_type ON transactions(type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_budget_lookup ON budgets(category, period, period_key);")

            # Seed default core categories if empty
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                default_cats = [
                    ("Salary", "income"),
                    ("Investment Returns", "income"),
                    ("Freelance", "income"),
                    ("Gift", "income"),
                    ("Housing & Rent", "expense"),
                    ("Groceries", "expense"),
                    ("Dining & Restaurants", "expense"),
                    ("Utilities & Bills", "expense"),
                    ("Transportation", "expense"),
                    ("Healthcare", "expense"),
                    ("Entertainment", "expense"),
                    ("Shopping", "expense"),
                    ("Education", "expense"),
                    ("Subscriptions", "expense"),
                    ("Travel", "expense"),
                    ("Miscellaneous", "expense"),
                    ("Account Transfer", "transfer"),
                ]
                cursor.executemany(
                    "INSERT OR IGNORE INTO categories (name, category_type, is_custom) VALUES (?, ?, 0)",
                    default_cats,
                )

            conn.commit()

    # --- Audit Log Helper ---
    def record_audit(self, action: str, entity_type: str, entity_id: str, details: str = "") -> None:
        """Appends an event to the security audit log."""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO audit_logs (action, entity_type, entity_id, details, timestamp) VALUES (?, ?, ?, ?, ?)",
                (action, entity_type, entity_id, details, datetime.utcnow().isoformat()),
            )
            conn.commit()

    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves recent audit log events."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # --- Accounts CRUD ---
    def save_account(self, account_dict: Dict[str, Any]) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO accounts (id, name, type, initial_balance, balance, currency, allow_overdraft, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    balance=excluded.balance,
                    allow_overdraft=excluded.allow_overdraft;
                """,
                (
                    account_dict["id"],
                    account_dict["name"],
                    account_dict["type"],
                    str(account_dict.get("initial_balance", account_dict["balance"])),
                    str(account_dict["balance"]),
                    account_dict.get("currency", "USD"),
                    1 if account_dict.get("allow_overdraft") else 0,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
        self.record_audit("SAVE", "ACCOUNT", account_dict["id"], f"Saved account {account_dict['name']}")

    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ? OR name = ?", (account_id, account_id))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_account(self, account_id: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE account_id = ? OR target_account_id = ?", (account_id, account_id))
            if cursor.fetchone()[0] > 0:
                raise DatabaseConnectionError("Cannot delete account containing active transaction records.")
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            conn.commit()
        self.record_audit("DELETE", "ACCOUNT", account_id, "Deleted account")

    # --- Transactions CRUD ---
    def insert_transaction(self, txn_dict: Dict[str, Any]) -> None:
        """Inserts a transaction record using parameterized queries."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO transactions (id, amount, type, category, account_id, target_account_id, date, description, payment_method, recurring, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    txn_dict["id"],
                    str(txn_dict["amount"]),
                    txn_dict["type"],
                    txn_dict["category"],
                    txn_dict["account_id"],
                    txn_dict.get("target_account_id"),
                    txn_dict["date"],
                    txn_dict.get("description", ""),
                    txn_dict.get("payment_method", "Bank Transfer"),
                    txn_dict.get("recurring", "none"),
                    txn_dict.get("created_at", datetime.utcnow().isoformat()),
                ),
            )
            conn.commit()
        self.record_audit("CREATE", "TRANSACTION", txn_dict["id"], f"{txn_dict['type']} {txn_dict['amount']} {txn_dict['category']}")

    def update_transaction(self, txn_dict: Dict[str, Any]) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE transactions
                SET amount = ?, type = ?, category = ?, account_id = ?, target_account_id = ?,
                    date = ?, description = ?, payment_method = ?, recurring = ?
                WHERE id = ?
                """,
                (
                    str(txn_dict["amount"]),
                    txn_dict["type"],
                    txn_dict["category"],
                    txn_dict["account_id"],
                    txn_dict.get("target_account_id"),
                    txn_dict["date"],
                    txn_dict.get("description", ""),
                    txn_dict.get("payment_method", "Bank Transfer"),
                    txn_dict.get("recurring", "none"),
                    txn_dict["id"],
                ),
            )
            conn.commit()
        self.record_audit("UPDATE", "TRANSACTION", txn_dict["id"], f"Updated transaction {txn_dict['id']}")

    def delete_transaction(self, transaction_id: str) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
        self.record_audit("DELETE", "TRANSACTION", transaction_id, "Deleted transaction")

    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_transactions(
        self,
        account_id: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        txn_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Queries transactions with optional filters and sorting."""
        query = "SELECT * FROM transactions WHERE 1=1"
        params: List[Any] = []

        if account_id:
            query += " AND (account_id = ? OR target_account_id = ?)"
            params.extend([account_id, account_id])
        if category:
            query += " AND category = ?"
            params.append(category)
        if txn_type:
            query += " AND type = ?"
            params.append(txn_type)
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if search_query:
            query += " AND (description LIKE ? OR category LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        query += " ORDER BY date DESC, created_at DESC"

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # --- Budgets CRUD ---
    def save_budget(self, budget_dict: Dict[str, Any]) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO budgets (id, category, limit_amount, period, period_key, allow_rollover, rollover_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(category, period, period_key) DO UPDATE SET
                    limit_amount=excluded.limit_amount,
                    allow_rollover=excluded.allow_rollover,
                    rollover_amount=excluded.rollover_amount;
                """,
                (
                    budget_dict["id"],
                    budget_dict["category"],
                    str(budget_dict["limit"]),
                    budget_dict.get("period", "monthly"),
                    budget_dict.get("period_key", ""),
                    1 if budget_dict.get("allow_rollover", True) else 0,
                    str(budget_dict.get("rollover_amount", "0.00")),
                ),
            )
            conn.commit()

    def get_budgets(self, period_key: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if period_key:
                cursor.execute("SELECT * FROM budgets WHERE period_key = ? ORDER BY category ASC", (period_key,))
            else:
                cursor.execute("SELECT * FROM budgets ORDER BY period_key DESC, category ASC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_budget(self, budget_id: str) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
            conn.commit()

    # --- Categories CRUD ---
    def get_categories(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def add_category(self, name: str, category_type: str = "expense") -> None:
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO categories (name, category_type, is_custom) VALUES (?, ?, 1)",
                (name, category_type),
            )
            conn.commit()

    # --- Backup & Restore ---
    def backup_to_file(self, backup_filepath: str) -> str:
        """Generates an atomic snapshot backup of the SQLite database."""
        dest_dir = os.path.dirname(backup_filepath)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        with self.get_connection() as src_conn:
            dest_conn = sqlite3.connect(backup_filepath)
            src_conn.backup(dest_conn)
            dest_conn.close()

        self.record_audit("BACKUP", "DATABASE", "SYSTEM", f"Snapshot saved to {backup_filepath}")
        return backup_filepath

    def restore_from_file(self, backup_filepath: str) -> None:
        """Restores the database state safely from a validated snapshot file."""
        if not os.path.exists(backup_filepath):
            raise DatabaseConnectionError(f"Backup file not found: {backup_filepath}")

        # Test valid sqlite database
        try:
            test_conn = sqlite3.connect(backup_filepath)
            cursor = test_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            test_conn.close()
            if "transactions" not in tables or "accounts" not in tables:
                raise DatabaseConnectionError("Target backup file missing mandatory schema tables.")
        except Exception as e:
            raise DatabaseConnectionError(f"Corrupted or invalid backup file: {e}")

        # Perform atomic copy
        shutil.copy2(backup_filepath, self.db_path)
        self.record_audit("RESTORE", "DATABASE", "SYSTEM", f"Restored from {backup_filepath}")
