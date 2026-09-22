"""Sample financial data generator.

Populates realistic multi-month financial history with incomes, expenses,
transfers, subscriptions, budget allocations, and deliberate anomalies
for testing statistical detectors.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
from finance_tracker import FinanceTracker


def seed_sample_data(tracker: FinanceTracker, clear_first: bool = False) -> None:
    """Populates realistic accounts, budgets, and transactions into the database."""
    # Ensure standard accounts exist
    existing_accounts = {a.name: a for a in tracker.get_all_accounts()}

    checking = existing_accounts.get("Chase Checking")
    if not checking:
        checking = tracker.add_account(
            name="Chase Checking",
            account_type="checking",
            initial_balance=Decimal("0.00"),
            currency="USD",
            allow_overdraft=True,
        )

    savings = existing_accounts.get("Marcus High-Yield Savings")
    if not savings:
        savings = tracker.add_account(
            name="Marcus High-Yield Savings",
            account_type="savings",
            initial_balance=Decimal("0.00"),
            currency="USD",
        )

    cash = existing_accounts.get("Wallet Cash")
    if not cash:
        cash = tracker.add_account(
            name="Wallet Cash",
            account_type="cash",
            initial_balance=Decimal("0.00"),
            currency="USD",
        )

    investments = existing_accounts.get("Vanguard Brokerage")
    if not investments:
        investments = tracker.add_account(
            name="Vanguard Brokerage",
            account_type="investment",
            initial_balance=Decimal("0.00"),
            currency="USD",
        )

    # Configure budgets for current month
    current_month = datetime.utcnow().strftime("%Y-%m")
    tracker.set_budget("Groceries", Decimal("550.00"), period="monthly", period_key=current_month)
    tracker.set_budget("Dining & Restaurants", Decimal("300.00"), period="monthly", period_key=current_month)
    tracker.set_budget("Utilities & Bills", Decimal("220.00"), period="monthly", period_key=current_month)
    tracker.set_budget("Entertainment", Decimal("180.00"), period="monthly", period_key=current_month)
    tracker.set_budget("Subscriptions", Decimal("140.00"), period="monthly", period_key=current_month)
    tracker.set_budget("Shopping", Decimal("250.00"), period="monthly", period_key=current_month)

    # Generate 4 months of transactions backwards from today
    today = datetime.utcnow().date()

    # Recurring templates
    for month_offset in [3, 2, 1, 0]:
        base_date = today - timedelta(days=month_offset * 30)
        m_str = base_date.strftime("%Y-%m")

        # 1. Salary (1st and 15th)
        s1_date = f"{m_str}-01"
        s2_date = f"{m_str}-15"
        tracker.add_transaction(
            amount=Decimal("3450.00"),
            transaction_type="income",
            category="Salary",
            account_id=checking.id,
            date_str=s1_date,
            description="Bi-Weekly Payroll Direct Deposit - ACME Tech",
            payment_method="Bank Transfer",
            recurring="monthly",
        )
        tracker.add_transaction(
            amount=Decimal("3450.00"),
            transaction_type="income",
            category="Salary",
            account_id=checking.id,
            date_str=s2_date,
            description="Bi-Weekly Payroll Direct Deposit - ACME Tech",
            payment_method="Bank Transfer",
            recurring="monthly",
        )

        # 2. Freelance Consulting
        tracker.add_transaction(
            amount=Decimal("750.00"),
            transaction_type="income",
            category="Freelance",
            account_id=checking.id,
            date_str=f"{m_str}-18",
            description="Client UI/UX Consulting Retainer",
            payment_method="Bank Transfer",
        )

        # 3. Rent
        tracker.add_transaction(
            amount=Decimal("1750.00"),
            transaction_type="expense",
            category="Housing & Rent",
            account_id=checking.id,
            date_str=f"{m_str}-02",
            description="Apartment Lease Payment",
            payment_method="Bank Transfer",
            recurring="monthly",
        )

        # 4. Utilities & Internet
        tracker.add_transaction(
            amount=Decimal("110.50"),
            transaction_type="expense",
            category="Utilities & Bills",
            account_id=checking.id,
            date_str=f"{m_str}-05",
            description="Electric & Power Utility",
            payment_method="Debit Card",
        )
        tracker.add_transaction(
            amount=Decimal("79.99"),
            transaction_type="expense",
            category="Utilities & Bills",
            account_id=checking.id,
            date_str=f"{m_str}-12",
            description="Fiber Gigabit Internet",
            payment_method="Credit Card",
            recurring="monthly",
        )

        # 5. Groceries (weekly)
        for d in [3, 10, 17, 24]:
            tracker.add_transaction(
                amount=Decimal("115.40") + Decimal(str(d)),
                transaction_type="expense",
                category="Groceries",
                account_id=checking.id,
                date_str=f"{m_str}-{d:02d}",
                description="Whole Foods Market / Trader Joe's",
                payment_method="Credit Card",
            )

        # 6. Dining & Coffee
        for d in [7, 14, 21, 28]:
            tracker.add_transaction(
                amount=Decimal("45.20") + Decimal(str(d % 15)),
                transaction_type="expense",
                category="Dining & Restaurants",
                account_id=checking.id,
                date_str=f"{m_str}-{d:02d}",
                description="Local Bistro & Specialty Coffee",
                payment_method="Credit Card",
            )

        # 7. Fixed Subscriptions
        tracker.add_transaction(
            amount=Decimal("19.99"),
            transaction_type="expense",
            category="Subscriptions",
            account_id=checking.id,
            date_str=f"{m_str}-08",
            description="Netflix Premium 4K",
            payment_method="Credit Card",
            recurring="monthly",
        )
        tracker.add_transaction(
            amount=Decimal("11.99"),
            transaction_type="expense",
            category="Subscriptions",
            account_id=checking.id,
            date_str=f"{m_str}-09",
            description="Spotify Family Plan",
            payment_method="Credit Card",
            recurring="monthly",
        )
        tracker.add_transaction(
            amount=Decimal("45.00"),
            transaction_type="expense",
            category="Subscriptions",
            account_id=checking.id,
            date_str=f"{m_str}-16",
            description="Cloud VPS & Development Tools",
            payment_method="Credit Card",
            recurring="monthly",
        )
        tracker.add_transaction(
            amount=Decimal("55.00"),
            transaction_type="expense",
            category="Subscriptions",
            account_id=checking.id,
            date_str=f"{m_str}-20",
            description="Equinox / Local Fitness Center",
            payment_method="Debit Card",
            recurring="monthly",
        )

        # 8. Systematic Monthly Savings Transfers (Checking -> High Yield Savings)
        tracker.transfer(
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("1200.00"),
            date_str=f"{m_str}-03",
            description="Automated Monthly Wealth Building Transfer",
        )

        # 9. Cash ATM withdrawal (Checking -> Cash Wallet)
        tracker.transfer(
            from_account_id=checking.id,
            to_account_id=cash.id,
            amount=Decimal("150.00"),
            date_str=f"{m_str}-06",
            description="ATM Cash Withdrawal",
        )

        # 10. Cash pocket expense
        tracker.add_transaction(
            amount=Decimal("35.00"),
            transaction_type="expense",
            category="Miscellaneous",
            account_id=cash.id,
            date_str=f"{m_str}-11",
            description="Farmers Market & Street Food",
            payment_method="Cash",
        )

    # Inject one deliberate anomaly in the previous month to trigger the outlier detector
    anomaly_date = (today - timedelta(days=22)).strftime("%Y-%m-%d")
    tracker.add_transaction(
        amount=Decimal("1280.00"),
        transaction_type="expense",
        category="Transportation",
        account_id=checking.id,
        date_str=anomaly_date,
        description="Emergency Engine & Brake System Overhaul",
        payment_method="Credit Card",
    )

    # Reconcile final balances
    tracker.reconcile_all_balances()
