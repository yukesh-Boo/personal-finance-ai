"""Custom exceptions for Smart Personal Finance Tracker.

Follows SOLID principles with a clear hierarchy of financial domain exceptions.
"""

class FinanceTrackerError(Exception):
    """Base exception for all domain errors in the personal finance application."""
    def __init__(self, message: str, code: str = "FINANCE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationError(FinanceTrackerError):
    """Raised when user input fails structural or financial validation."""
    def __init__(self, message: str, field: str = "general"):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class InsufficientFundsError(FinanceTrackerError):
    """Raised when an account lacks sufficient balance for an expense or transfer."""
    def __init__(self, account_name: str, requested: str, available: str):
        message = (
            f"Account '{account_name}' has insufficient funds. "
            f"Requested: {requested}, Available: {available}"
        )
        super().__init__(message, code="INSUFFICIENT_FUNDS")
        self.account_name = account_name
        self.requested = requested
        self.available = available


class AccountNotFoundError(FinanceTrackerError):
    """Raised when an account with the specified ID or name cannot be located."""
    def __init__(self, account_id: str):
        super().__init__(f"Account not found: '{account_id}'", code="ACCOUNT_NOT_FOUND")
        self.account_id = account_id


class DuplicateAccountError(FinanceTrackerError):
    """Raised when attempting to create an account with a duplicate name or ID."""
    def __init__(self, account_name: str):
        super().__init__(f"Account already exists: '{account_name}'", code="DUPLICATE_ACCOUNT")
        self.account_name = account_name


class TransactionNotFoundError(FinanceTrackerError):
    """Raised when a transaction record cannot be found."""
    def __init__(self, transaction_id: str):
        super().__init__(f"Transaction not found: '{transaction_id}'", code="TRANSACTION_NOT_FOUND")
        self.transaction_id = transaction_id


class DuplicateTransactionError(FinanceTrackerError):
    """Raised when a duplicate transaction ID or idempotent collision occurs."""
    def __init__(self, transaction_id: str):
        super().__init__(f"Duplicate transaction ID: '{transaction_id}'", code="DUPLICATE_TRANSACTION")
        self.transaction_id = transaction_id


class BudgetExceededError(FinanceTrackerError):
    """Raised when spending breaches strict budget constraints."""
    def __init__(self, category: str, limit: str, attempted: str):
        message = (
            f"Strict budget exceeded for '{category}'. "
            f"Limit: {limit}, Attempted total: {attempted}"
        )
        super().__init__(message, code="BUDGET_EXCEEDED")
        self.category = category
        self.limit = limit
        self.attempted = attempted


class DatabaseConnectionError(FinanceTrackerError):
    """Raised when database connection or transaction operations fail."""
    def __init__(self, message: str):
        super().__init__(f"Database operation failed: {message}", code="DATABASE_ERROR")


class SecurityError(FinanceTrackerError):
    """Raised when unauthorized operations or input tampering are detected."""
    def __init__(self, message: str):
        super().__init__(f"Security constraint violated: {message}", code="SECURITY_ERROR")
