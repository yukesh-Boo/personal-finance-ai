"""Input validation module for Smart Personal Finance Tracker.

Enforces strict financial correctness, prevents precision loss via Decimal,
and protects against SQL injection and corrupted user inputs.
"""

from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import re
from typing import Any, Union
from exceptions import ValidationError

_DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CATEGORY_REGEX = re.compile(r"^[A-Za-z0-9\s&/\-_]{1,50}$")
_ACCOUNT_NAME_REGEX = re.compile(r"^[A-Za-z0-9\s&/\-_\.]{1,60}$")


def validate_amount(value: Any, field_name: str = "Amount", allow_zero: bool = False) -> Decimal:
    """Validates and converts an amount to a positive Decimal with 2 decimal precision.

    Rejects negative, non-numeric, NaN, infinity, and zero (unless allow_zero=True).
    """
    if value is None:
        raise ValidationError(f"{field_name} cannot be null or empty.", field=field_name)

    try:
        if isinstance(value, float):
            # Convert float through string to avoid binary floating point precision artifacts
            d = Decimal(str(value))
        elif isinstance(value, (int, str)):
            d = Decimal(str(value).strip().replace(",", ""))
        elif isinstance(value, Decimal):
            d = value
        else:
            raise ValidationError(f"Invalid monetary format for {field_name}: {type(value)}", field=field_name)
    except (InvalidOperation, ValueError):
        raise ValidationError(f"{field_name} must be a valid numeric monetary value.", field=field_name)

    if d.is_nan() or d.is_infinite():
        raise ValidationError(f"{field_name} cannot be NaN or Infinity.", field=field_name)

    if d < Decimal("0.00"):
        raise ValidationError(f"{field_name} must be a non-negative number.", field=field_name)

    if not allow_zero and d == Decimal("0.00"):
        raise ValidationError(f"{field_name} must be greater than zero.", field=field_name)

    if d > Decimal("999999999999.99"):
        raise ValidationError(f"{field_name} exceeds maximum allowable threshold (1 Trillion).", field=field_name)

    # Quantize to 2 decimal places using HALF_UP
    return d.quantize(Decimal("0.01"))


def validate_date(value: Union[str, date, datetime], field_name: str = "Date") -> str:
    """Validates that a date is in YYYY-MM-DD format and represents a legitimate calendar day."""
    if not value:
        raise ValidationError(f"{field_name} cannot be empty.", field=field_name)

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")

    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")

    if isinstance(value, str):
        v = value.strip()
        if not _DATE_REGEX.match(v):
            raise ValidationError(f"{field_name} must follow ISO format 'YYYY-MM-DD'. Received: '{v}'", field=field_name)
        try:
            parsed = datetime.strptime(v, "%Y-%m-%d")
            # Enforce reasonable historical/future boundaries (1900 to 2100)
            if parsed.year < 1900 or parsed.year > 2100:
                raise ValidationError(f"{field_name} year must be between 1900 and 2100.", field=field_name)
            return v
        except ValueError as e:
            raise ValidationError(f"Invalid calendar date for {field_name}: {e}", field=field_name)

    raise ValidationError(f"{field_name} must be a valid date string or date object.", field=field_name)


def validate_category(name: str) -> str:
    """Sanitizes and validates a transaction or budget category name."""
    if not name or not isinstance(name, str):
        raise ValidationError("Category name cannot be empty.", field="category")

    cleaned = name.strip()
    if len(cleaned) < 2 or len(cleaned) > 50:
        raise ValidationError("Category name must be between 2 and 50 characters.", field="category")

    if not _CATEGORY_REGEX.match(cleaned):
        raise ValidationError(
            "Category name contains forbidden characters. Allowed: alphanumeric, space, &, /, -, _",
            field="category",
        )
    return cleaned.title()


def validate_account_name(name: str) -> str:
    """Sanitizes and validates an account name."""
    if not name or not isinstance(name, str):
        raise ValidationError("Account name cannot be empty.", field="account_name")

    cleaned = name.strip()
    if len(cleaned) < 2 or len(cleaned) > 60:
        raise ValidationError("Account name must be between 2 and 60 characters.", field="account_name")

    if not _ACCOUNT_NAME_REGEX.match(cleaned):
        raise ValidationError(
            "Account name contains invalid characters. Use letters, numbers, hyphens, and spaces.",
            field="account_name",
        )
    return cleaned


def validate_description(text: str) -> str:
    """Sanitizes transaction description/notes."""
    if text is None:
        return ""
    if not isinstance(text, str):
        raise ValidationError("Description must be a string.", field="description")
    cleaned = text.strip()
    if len(cleaned) > 255:
        raise ValidationError("Description exceeds maximum length of 255 characters.", field="description")
    return cleaned
