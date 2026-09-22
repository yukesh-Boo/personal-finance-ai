"""Account domain model and management.

Demonstrates OOP principles: encapsulation, polymorphism, inheritance, and clean domain design.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, Optional
from exceptions import InsufficientFundsError, ValidationError
from validators import validate_amount, validate_account_name


class AccountType(str, Enum):
    """Supported financial account types."""
    CHECKING = "checking"
    SAVINGS = "savings"
    CASH = "cash"
    CREDIT = "credit"
    INVESTMENT = "investment"


class Account(ABC):
    """Abstract base class for all financial accounts.

    Encapsulates account identification, name, balance tracking, and transaction safety.
    """

    def __init__(
        self,
        name: str,
        account_type: AccountType,
        initial_balance: Decimal = Decimal("0.00"),
        account_id: Optional[str] = None,
        currency: str = "USD",
        allow_overdraft: bool = False,
    ):
        self._id = account_id or f"acc_{uuid.uuid4().hex[:12]}"
        self._name = validate_account_name(name)
        self._type = account_type
        self._initial_balance = validate_amount(initial_balance, field_name="Initial Balance", allow_zero=True)
        self._balance = self._initial_balance
        self._currency = currency.upper().strip() or "USD"
        self._allow_overdraft = allow_overdraft

    @property
    def id(self) -> str:
        return self._id

    @property
    def initial_balance(self) -> Decimal:
        return self._initial_balance

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = validate_account_name(new_name)

    @property
    def account_type(self) -> AccountType:
        return self._type

    @property
    def balance(self) -> Decimal:
        return self._balance

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def allow_overdraft(self) -> bool:
        return self._allow_overdraft

    def set_balance_from_reconciliation(self, calculated_balance: Decimal) -> None:
        """Sets balance during system audit / reconciliation."""
        self._balance = calculated_balance.quantize(Decimal("0.01"))

    def deposit(self, amount: Decimal) -> Decimal:
        """Deposits a positive monetary amount into the account."""
        clean_amount = validate_amount(amount, field_name="Deposit Amount")
        self._balance += clean_amount
        return self._balance

    def withdraw(self, amount: Decimal) -> Decimal:
        """Withdraws an amount from the account, checking overdraft constraints."""
        clean_amount = validate_amount(amount, field_name="Withdrawal Amount")
        if not self._allow_overdraft and (self._balance - clean_amount < Decimal("0.00")):
            raise InsufficientFundsError(
                account_name=self._name,
                requested=f"{self._currency} {clean_amount}",
                available=f"{self._currency} {self._balance}",
            )
        self._balance -= clean_amount
        return self._balance

    def transfer_to(self, target_account: "Account", amount: Decimal) -> None:
        """Transfers funds to a destination account atomically in memory."""
        if self._id == target_account.id:
            raise ValidationError("Cannot transfer funds to the identical account.", field="transfer")
        clean_amount = validate_amount(amount, field_name="Transfer Amount")
        self.withdraw(clean_amount)
        target_account.deposit(clean_amount)

    @abstractmethod
    def get_account_perks(self) -> Dict[str, Any]:
        """Polymorphic method returning account-specific characteristics."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializes account to dictionary."""
        return {
            "id": self._id,
            "name": self._name,
            "type": self._type.value,
            "initial_balance": str(self._initial_balance),
            "balance": str(self._balance),
            "currency": self._currency,
            "allow_overdraft": self._allow_overdraft,
            "perks": self.get_account_perks(),
        }


class CheckingAccount(Account):
    """Checking account designed for day-to-day liquidity with optional overdraft."""

    def __init__(
        self,
        name: str,
        initial_balance: Decimal = Decimal("0.00"),
        account_id: Optional[str] = None,
        currency: str = "USD",
        overdraft_limit: Decimal = Decimal("500.00"),
        allow_overdraft: bool = True,
    ):
        super().__init__(name, AccountType.CHECKING, initial_balance, account_id, currency, allow_overdraft)
        self.overdraft_limit = validate_amount(overdraft_limit, field_name="Overdraft Limit", allow_zero=True)

    def withdraw(self, amount: Decimal) -> Decimal:
        clean_amount = validate_amount(amount, field_name="Withdrawal Amount")
        if self._allow_overdraft:
            if (self._balance - clean_amount) < (-self.overdraft_limit):
                raise InsufficientFundsError(
                    account_name=self._name,
                    requested=f"{self._currency} {clean_amount}",
                    available=f"{self._currency} {self._balance + self.overdraft_limit} (including overdraft limit)",
                )
            self._balance -= clean_amount
            return self._balance
        return super().withdraw(amount)

    def get_account_perks(self) -> Dict[str, Any]:
        return {
            "overdraft_protected": self._allow_overdraft,
            "overdraft_limit": str(self.overdraft_limit),
            "transaction_fee": "0.00",
        }


class SavingsAccount(Account):
    """Savings account designed for capital preservation and interest yield."""

    def __init__(
        self,
        name: str,
        initial_balance: Decimal = Decimal("0.00"),
        account_id: Optional[str] = None,
        currency: str = "USD",
        annual_interest_rate: Decimal = Decimal("4.25"),
    ):
        super().__init__(name, AccountType.SAVINGS, initial_balance, account_id, currency, allow_overdraft=False)
        self.annual_interest_rate = annual_interest_rate

    def get_account_perks(self) -> Dict[str, Any]:
        return {
            "interest_rate_apy": f"{self.annual_interest_rate}%",
            "overdraft_permitted": False,
            "yield_type": "high_yield_savings",
        }


class CashAccount(Account):
    """Physical cash / pocket wallet account."""

    def __init__(
        self,
        name: str = "Cash Wallet",
        initial_balance: Decimal = Decimal("0.00"),
        account_id: Optional[str] = None,
        currency: str = "USD",
    ):
        super().__init__(name, AccountType.CASH, initial_balance, account_id, currency, allow_overdraft=False)

    def get_account_perks(self) -> Dict[str, Any]:
        return {
            "physical_currency": True,
            "digital_connectivity": False,
        }


class InvestmentAccount(Account):
    """Brokerage / Investment portfolio account."""

    def __init__(
        self,
        name: str,
        initial_balance: Decimal = Decimal("0.00"),
        account_id: Optional[str] = None,
        currency: str = "USD",
    ):
        super().__init__(name, AccountType.INVESTMENT, initial_balance, account_id, currency, allow_overdraft=False)

    def get_account_perks(self) -> Dict[str, Any]:
        return {
            "asset_class": "equities_bonds_etfs",
            "capital_gains_tracking": True,
        }


def create_account(
    name: str,
    account_type: str,
    initial_balance: Decimal = Decimal("0.00"),
    account_id: Optional[str] = None,
    currency: str = "USD",
    allow_overdraft: bool = False,
) -> Account:
    """Factory function for creating appropriate Account instances based on type."""
    normalized_type = account_type.lower().strip()
    if normalized_type == AccountType.CHECKING.value:
        return CheckingAccount(name, initial_balance, account_id, currency, allow_overdraft=allow_overdraft)
    elif normalized_type == AccountType.SAVINGS.value:
        return SavingsAccount(name, initial_balance, account_id, currency)
    elif normalized_type == AccountType.CASH.value:
        return CashAccount(name, initial_balance, account_id, currency)
    elif normalized_type == AccountType.INVESTMENT.value:
        return InvestmentAccount(name, initial_balance, account_id, currency)
    else:
        # Default checking
        return CheckingAccount(name, initial_balance, account_id, currency, allow_overdraft=allow_overdraft)
