"""Transaction model and definitions for Smart Personal Finance Tracker.

Represents financial transactions with immutability helpers, categorization,
payment methods, recurring schedules, and distinct transfer semantics.
"""

from decimal import Decimal
from enum import Enum
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from validators import validate_amount, validate_date, validate_category, validate_description


class TransactionType(str, Enum):
    """Primary transaction classification."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class PaymentMethod(str, Enum):
    """Common payment channels."""
    CASH = "Cash"
    DEBIT_CARD = "Debit Card"
    CREDIT_CARD = "Credit Card"
    BANK_TRANSFER = "Bank Transfer"
    UPI = "UPI"
    OTHER = "Other"


class RecurringFrequency(str, Enum):
    """Recurring automation frequency."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Transaction:
    """Represents an atomic financial transaction.

    Ensures that transfers are explicitly identified and separated
    from net income or expense accounting.
    """

    def __init__(
        self,
        amount: Decimal,
        transaction_type: TransactionType,
        category: str,
        account_id: str,
        date_str: str,
        description: str = "",
        payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER,
        recurring: RecurringFrequency = RecurringFrequency.NONE,
        target_account_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self._id = transaction_id or f"txn_{uuid.uuid4().hex[:12]}"
        self._amount = validate_amount(amount, field_name="Transaction Amount")
        self._type = transaction_type if isinstance(transaction_type, TransactionType) else TransactionType(transaction_type)
        self._category = validate_category(category)
        self._account_id = account_id.strip()
        self._date = validate_date(date_str)
        self._description = validate_description(description)
        self._payment_method = payment_method if isinstance(payment_method, PaymentMethod) else PaymentMethod(payment_method)
        self._recurring = recurring if isinstance(recurring, RecurringFrequency) else RecurringFrequency(recurring)
        self._target_account_id = target_account_id.strip() if target_account_id else None
        self._created_at = created_at or datetime.utcnow().isoformat()

    @property
    def id(self) -> str:
        return self._id

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def transaction_type(self) -> TransactionType:
        return self._type

    @property
    def category(self) -> str:
        return self._category

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def date(self) -> str:
        return self._date

    @property
    def description(self) -> str:
        return self._description

    @property
    def payment_method(self) -> PaymentMethod:
        return self._payment_method

    @property
    def recurring(self) -> RecurringFrequency:
        return self._recurring

    @property
    def target_account_id(self) -> Optional[str]:
        return self._target_account_id

    @property
    def created_at(self) -> str:
        return self._created_at

    def is_income(self) -> bool:
        return self._type == TransactionType.INCOME

    def is_expense(self) -> bool:
        return self._type == TransactionType.EXPENSE

    def is_transfer(self) -> bool:
        return self._type == TransactionType.TRANSFER

    def to_dict(self) -> Dict[str, Any]:
        """Converts transaction to serializable dictionary."""
        return {
            "id": self._id,
            "amount": str(self._amount),
            "type": self._type.value,
            "category": self._category,
            "account_id": self._account_id,
            "date": self._date,
            "description": self._description,
            "payment_method": self._payment_method.value,
            "recurring": self._recurring.value,
            "target_account_id": self._target_account_id,
            "created_at": self._created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Instantiates a Transaction from a dictionary or database row."""
        return cls(
            amount=Decimal(str(data["amount"])),
            transaction_type=TransactionType(data["type"]),
            category=data["category"],
            account_id=data["account_id"],
            date_str=data["date"],
            description=data.get("description", ""),
            payment_method=PaymentMethod(data.get("payment_method", PaymentMethod.BANK_TRANSFER.value)),
            recurring=RecurringFrequency(data.get("recurring", RecurringFrequency.NONE.value)),
            target_account_id=data.get("target_account_id"),
            transaction_id=data.get("id"),
            created_at=data.get("created_at"),
        )
