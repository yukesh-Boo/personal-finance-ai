"""Main FinanceTracker orchestrator class.

Coordinates accounts, transaction processing, dynamic balance calculation,
inter-account transfers, budgets, analytics, and persistent SQLite storage.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from account import Account, create_account, AccountType
from transaction import Transaction, TransactionType, PaymentMethod, RecurringFrequency
from budget import Budget, BudgetPeriod
from database import DatabaseManager
from analytics import FinancialAnalytics
from reports import ReportGenerator
from exceptions import (
    AccountNotFoundError,
    TransactionNotFoundError,
    InsufficientFundsError,
    ValidationError,
)
from validators import (
    validate_amount,
    validate_date,
    validate_category,
    validate_account_name,
)


class FinanceTracker:
    """Core domain orchestrator for personal finance management.

    Maintains synchronization between in-memory domain models and persistent SQLite store,
    enforcing dynamic balance reconciliation and strict financial correctness.
    """

    def __init__(self, db_path: str = "finance_tracker.db", auto_reconcile: bool = True):
        self.db = DatabaseManager(db_path=db_path)
        self._accounts: Dict[str, Account] = {}
        self._load_accounts_from_db()
        if auto_reconcile:
            self.reconcile_all_balances()

    # --- Account Operations ---
    def _load_accounts_from_db(self) -> None:
        """Loads persistent accounts into domain memory."""
        raw_accounts = self.db.get_all_accounts()
        self._accounts.clear()
        for row in raw_accounts:
            acc = create_account(
                name=row["name"],
                account_type=row["type"],
                initial_balance=Decimal(str(row.get("initial_balance", row["balance"]))),
                account_id=row["id"],
                currency=row.get("currency", "USD"),
                allow_overdraft=bool(row.get("allow_overdraft", 0)),
            )
            # Reconcile stored current balance
            acc.set_balance_from_reconciliation(Decimal(str(row["balance"])))
            self._accounts[acc.id] = acc

    def add_account(
        self,
        name: str,
        account_type: str = "checking",
        initial_balance: Decimal = Decimal("0.00"),
        currency: str = "USD",
        allow_overdraft: bool = False,
    ) -> Account:
        """Creates and stores a new account."""
        clean_name = validate_account_name(name)
        # Check uniqueness
        for acc in self._accounts.values():
            if acc.name.lower() == clean_name.lower():
                raise ValidationError(f"An account with name '{clean_name}' already exists.", field="account_name")

        account = create_account(
            name=clean_name,
            account_type=account_type,
            initial_balance=initial_balance,
            currency=currency,
            allow_overdraft=allow_overdraft,
        )
        self.db.save_account(account.to_dict())
        self._accounts[account.id] = account
        return account

    def get_account(self, account_identifier: str) -> Account:
        """Finds account by ID or Name."""
        # Check by ID
        if account_identifier in self._accounts:
            return self._accounts[account_identifier]
        # Check by name (case-insensitive)
        for acc in self._accounts.values():
            if acc.name.lower() == account_identifier.lower().strip():
                return acc
        raise AccountNotFoundError(account_identifier)

    def get_all_accounts(self) -> List[Account]:
        """Returns all accounts sorted alphabetically."""
        return sorted(list(self._accounts.values()), key=lambda a: a.name)

    def delete_account(self, account_id: str) -> None:
        """Removes an account if it has no associated transactions."""
        acc = self.get_account(account_id)
        self.db.delete_account(acc.id)
        del self._accounts[acc.id]

    # --- Balance Calculation & Reconciliation ---
    def calculate_account_balance(self, account_id: str) -> Decimal:
        """Dynamically computes the exact balance of an account from transaction history.

        Formula:
        Balance = Initial opening balance
                  + Sum(Incomes to this account)
                  - Sum(Expenses from this account)
                  + Sum(Transfers received by this account)
                  - Sum(Transfers sent from this account)
        """
        acc = self.get_account(account_id)
        txns = self.db.get_all_transactions(account_id=acc.id)

        # Baseline starts with initial opening balance
        balance = acc.initial_balance

        for t in txns:
            amt = Decimal(str(t["amount"]))
            ttype = t["type"]

            if ttype == TransactionType.INCOME.value and t["account_id"] == acc.id:
                balance += amt
            elif ttype == TransactionType.EXPENSE.value and t["account_id"] == acc.id:
                balance -= amt
            elif ttype == TransactionType.TRANSFER.value:
                if t["account_id"] == acc.id:
                    # Sender
                    balance -= amt
                if t.get("target_account_id") == acc.id:
                    # Receiver
                    balance += amt

        return balance.quantize(Decimal("0.01"))

    def reconcile_all_balances(self) -> Dict[str, str]:
        """Recalculates and persists balances for all accounts to guarantee audit integrity."""
        reconciled = {}
        for acc in self._accounts.values():
            dyn_bal = self.calculate_account_balance(acc.id)
            acc.set_balance_from_reconciliation(dyn_bal)
            self.db.save_account(acc.to_dict())
            reconciled[acc.name] = str(dyn_bal)
        return reconciled

    # --- Transaction Management ---
    def add_transaction(
        self,
        amount: Union[Decimal, float, str, int],
        transaction_type: Union[TransactionType, str],
        category: str,
        account_id: str,
        date_str: Optional[str] = None,
        description: str = "",
        payment_method: Union[PaymentMethod, str] = PaymentMethod.BANK_TRANSFER,
        recurring: Union[RecurringFrequency, str] = RecurringFrequency.NONE,
        target_account_id: Optional[str] = None,
    ) -> Transaction:
        """Creates and stores an atomic transaction."""
        source_account = self.get_account(account_id)
        dec_amount = validate_amount(amount, field_name="Amount")
        clean_date = validate_date(date_str or datetime.utcnow().strftime("%Y-%m-%d"))
        t_type = TransactionType(transaction_type)

        target_acc = None
        if t_type == TransactionType.TRANSFER:
            if not target_account_id:
                raise ValidationError("Transfers require a destination target_account_id.", field="target_account_id")
            target_acc = self.get_account(target_account_id)
            if source_account.id == target_acc.id:
                raise ValidationError("Cannot transfer funds to the identical account.", field="transfer")

        # Validate balance / overdraft before applying
        if t_type in (TransactionType.EXPENSE, TransactionType.TRANSFER):
            current_bal = source_account.balance
            if not source_account.allow_overdraft and (current_bal - dec_amount < Decimal("0.00")):
                raise InsufficientFundsError(
                    account_name=source_account.name,
                    requested=f"{source_account.currency} {dec_amount}",
                    available=f"{source_account.currency} {current_bal}",
                )

        txn = Transaction(
            amount=dec_amount,
            transaction_type=t_type,
            category=category,
            account_id=source_account.id,
            date_str=clean_date,
            description=description,
            payment_method=PaymentMethod(payment_method),
            recurring=RecurringFrequency(recurring),
            target_account_id=target_acc.id if target_acc else None,
        )

        # Persist transaction
        self.db.insert_transaction(txn.to_dict())

        # Update in-memory balances
        if t_type == TransactionType.INCOME:
            source_account.deposit(dec_amount)
        elif t_type == TransactionType.EXPENSE:
            source_account.withdraw(dec_amount)
        elif t_type == TransactionType.TRANSFER and target_acc:
            source_account.transfer_to(target_acc, dec_amount)
            self.db.save_account(target_acc.to_dict())

        self.db.save_account(source_account.to_dict())
        return txn

    def transfer(
        self,
        from_account_id: str,
        to_account_id: str,
        amount: Union[Decimal, float, str, int],
        date_str: Optional[str] = None,
        description: str = "Account Transfer",
    ) -> Transaction:
        """Executes a first-class inter-account transfer without polluting income/expense metrics."""
        return self.add_transaction(
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
            category="Account Transfer",
            account_id=from_account_id,
            target_account_id=to_account_id,
            date_str=date_str,
            description=description,
            payment_method=PaymentMethod.BANK_TRANSFER,
        )

    def delete_transaction(self, transaction_id: str) -> None:
        """Deletes a transaction and reconciles account balances."""
        existing = self.db.get_transaction(transaction_id)
        if not existing:
            raise TransactionNotFoundError(transaction_id)

        self.db.delete_transaction(transaction_id)
        self.reconcile_all_balances()

    def update_transaction(
        self,
        transaction_id: str,
        amount: Optional[Union[Decimal, float, str]] = None,
        category: Optional[str] = None,
        date_str: Optional[str] = None,
        description: Optional[str] = None,
        payment_method: Optional[str] = None,
    ) -> Transaction:
        """Modifies transaction attributes and recomputes balances."""
        raw = self.db.get_transaction(transaction_id)
        if not raw:
            raise TransactionNotFoundError(transaction_id)

        txn = Transaction.from_dict(raw)
        updated_dict = txn.to_dict()

        if amount is not None:
            updated_dict["amount"] = str(validate_amount(amount))
        if category is not None:
            updated_dict["category"] = validate_category(category)
        if date_str is not None:
            updated_dict["date"] = validate_date(date_str)
        if description is not None:
            updated_dict["description"] = description.strip()
        if payment_method is not None:
            updated_dict["payment_method"] = PaymentMethod(payment_method).value

        new_txn = Transaction.from_dict(updated_dict)
        self.db.update_transaction(new_txn.to_dict())
        self.reconcile_all_balances()
        return new_txn

    def get_transactions(
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
        """Returns filtered transaction records."""
        return self.db.get_all_transactions(
            account_id=account_id,
            category=category,
            start_date=start_date,
            end_date=end_date,
            txn_type=txn_type,
            search_query=search_query,
            limit=limit,
            offset=offset,
        )

    # --- Budget Operations ---
    def set_budget(
        self,
        category: str,
        limit_amount: Union[Decimal, float, str],
        period: str = "monthly",
        period_key: Optional[str] = None,
        allow_rollover: bool = True,
    ) -> Budget:
        """Configures or updates a category budget limit."""
        if not period_key:
            now = datetime.utcnow()
            period_key = now.strftime("%Y-%m") if period == "monthly" else str(now.year)

        budget = Budget(
            category=category,
            limit_amount=Decimal(str(limit_amount)),
            period=BudgetPeriod(period),
            period_key=period_key,
            allow_rollover=allow_rollover,
        )
        self.db.save_budget(budget.to_dict())
        return budget

    def evaluate_budgets(self, period_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Evaluates active budgets against actual spending for the period."""
        if not period_key:
            period_key = datetime.utcnow().strftime("%Y-%m")

        budgets = [Budget.from_dict(b) for b in self.db.get_budgets(period_key=period_key)]
        all_txns = self.db.get_all_transactions()

        # Filter txns for the period
        period_expenses: Dict[str, Decimal] = {}
        for t in all_txns:
            if t["type"] == "expense" and t["date"].startswith(period_key):
                cat = t["category"]
                amt = Decimal(str(t["amount"]))
                period_expenses[cat] = period_expenses.get(cat, Decimal("0.00")) + amt

        evaluations = []
        for b in budgets:
            spent = period_expenses.get(b.category, Decimal("0.00"))
            evaluations.append(b.evaluate(spent))

        return evaluations

    def get_budget_recommendations(self) -> List[Dict[str, Any]]:
        """Generates intelligent recommendations based on past 3-6 months spending."""
        all_txns = self.db.get_all_transactions()
        budgets = [Budget.from_dict(b) for b in self.db.get_budgets()]

        # Group spending by (category, month)
        monthly_cat_spend: Dict[str, Dict[str, Decimal]] = {}
        for t in all_txns:
            if t["type"] == "expense":
                cat = t["category"]
                m_key = t["date"][:7]
                amt = Decimal(str(t["amount"]))
                if cat not in monthly_cat_spend:
                    monthly_cat_spend[cat] = {}
                monthly_cat_spend[cat][m_key] = monthly_cat_spend[cat].get(m_key, Decimal("0.00")) + amt

        recommendations = []
        for b in budgets:
            spends_dict = monthly_cat_spend.get(b.category, {})
            spends_list = list(spends_dict.values())
            rec = b.recommend_adjustment(spends_list)
            recommendations.append(rec)

        return recommendations

    # --- Analytics & Reporting ---
    def get_analytics_dossier(self) -> Dict[str, Any]:
        """Computes comprehensive analytics dossier."""
        all_txns = self.db.get_all_transactions()
        accounts = [a.to_dict() for a in self.get_all_accounts()]
        summary = FinancialAnalytics.calculate_summary(all_txns)
        category_breakdown = FinancialAnalytics.category_spending_breakdown(all_txns)
        trends = FinancialAnalytics.monthly_trends(all_txns)
        velocity = FinancialAnalytics.spending_velocity(all_txns)
        outliers = FinancialAnalytics.detect_unusual_spending(all_txns)
        subscriptions = FinancialAnalytics.identify_subscriptions(all_txns)
        forecast = FinancialAnalytics.forecast_next_month(all_txns)

        total_liquid = sum(Decimal(a["balance"]) for a in accounts)
        budgets_eval = self.evaluate_budgets()
        health = FinancialAnalytics.compute_financial_health_score(all_txns, total_liquid, budgets_eval)

        return {
            "summary": summary,
            "accounts": accounts,
            "category_breakdown": category_breakdown,
            "monthly_trends": trends,
            "spending_velocity": velocity,
            "anomalous_outliers": outliers,
            "subscriptions": subscriptions,
            "forecast": forecast,
            "budget_evaluations": budgets_eval,
            "financial_health": health,
        }

    def generate_report(self, format_type: str = "text") -> str:
        """Generates an executive report in specified format ('text', 'html', or 'csv')."""
        dossier = self.get_analytics_dossier()
        all_txns = self.db.get_all_transactions()

        if format_type.lower() == "csv":
            return ReportGenerator.generate_csv_transactions(all_txns)
        elif format_type.lower() == "html":
            return ReportGenerator.generate_html_report(
                summary=dossier["summary"],
                accounts=dossier["accounts"],
                category_breakdown=dossier["category_breakdown"],
                budget_evaluations=dossier["budget_evaluations"],
                trends=dossier["monthly_trends"],
                outliers=dossier["anomalous_outliers"],
                subscriptions=dossier["subscriptions"],
                health=dossier["financial_health"],
            )
        else:
            return ReportGenerator.generate_text_summary_report(
                summary=dossier["summary"],
                accounts=dossier["accounts"],
                category_breakdown=dossier["category_breakdown"],
                budget_evaluations=dossier["budget_evaluations"],
                health=dossier["financial_health"],
            )
