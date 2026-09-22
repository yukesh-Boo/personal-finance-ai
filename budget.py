"""Intelligent budget management module.

Handles category-specific spending limits, monthly/yearly periods,
utilization percentage tracking, 80% threshold warnings, overrun alarms,
rollover balance accounting, and historical spending adjustments.
"""

from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, Optional, List
from validators import validate_amount, validate_category


class BudgetPeriod(str, Enum):
    """Budget recurrence period."""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Budget:
    """Represents a budget policy for a category in a given cycle."""

    def __init__(
        self,
        category: str,
        limit_amount: Decimal,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        period_key: str = "",  # e.g., '2026-09' or '2026'
        allow_rollover: bool = True,
        rollover_amount: Decimal = Decimal("0.00"),
        budget_id: Optional[str] = None,
    ):
        self._id = budget_id or f"bdg_{uuid.uuid4().hex[:12]}"
        self._category = validate_category(category)
        self._limit = validate_amount(limit_amount, field_name="Budget Limit")
        self._period = period if isinstance(period, BudgetPeriod) else BudgetPeriod(period)
        self._period_key = period_key.strip()
        self._allow_rollover = allow_rollover
        self._rollover_amount = Decimal(str(rollover_amount)).quantize(Decimal("0.01"))

    @property
    def id(self) -> str:
        return self._id

    @property
    def category(self) -> str:
        return self._category

    @property
    def limit(self) -> Decimal:
        return self._limit

    @limit.setter
    def limit(self, new_limit: Decimal) -> None:
        self._limit = validate_amount(new_limit, field_name="Budget Limit")

    @property
    def period(self) -> BudgetPeriod:
        return self._period

    @property
    def period_key(self) -> str:
        return self._period_key

    @property
    def allow_rollover(self) -> bool:
        return self._allow_rollover

    @property
    def rollover_amount(self) -> Decimal:
        return self._rollover_amount

    @property
    def effective_limit(self) -> Decimal:
        """The spending limit adjusted by previous cycle's rollover."""
        effective = self._limit + self._rollover_amount
        return effective if effective > Decimal("0.00") else Decimal("0.00")

    def evaluate(self, actual_spent: Decimal) -> Dict[str, Any]:
        """Calculates utilization, 80% warning threshold, and overruns."""
        spent = Decimal(str(actual_spent)).quantize(Decimal("0.01"))
        eff_limit = self.effective_limit

        if eff_limit > Decimal("0.00"):
            utilization_pct = (spent / eff_limit) * Decimal("100.00")
        else:
            utilization_pct = Decimal("100.00") if spent > 0 else Decimal("0.00")

        remaining = eff_limit - spent
        is_warning = (utilization_pct >= Decimal("80.00")) and (spent <= eff_limit)
        is_overrun = spent > eff_limit
        overrun_amount = (spent - eff_limit) if is_overrun else Decimal("0.00")

        return {
            "budget_id": self._id,
            "category": self._category,
            "base_limit": str(self._limit),
            "rollover_amount": str(self._rollover_amount),
            "effective_limit": str(eff_limit),
            "actual_spent": str(spent),
            "remaining": str(remaining),
            "utilization_percentage": float(utilization_pct.quantize(Decimal("0.1"))),
            "is_warning_80": bool(is_warning),
            "is_overrun": bool(is_overrun),
            "overrun_amount": str(overrun_amount),
            "status": "OVERRUN" if is_overrun else ("WARNING" if is_warning else "HEALTHY"),
        }

    def recommend_adjustment(self, historical_spends: List[Decimal]) -> Dict[str, Any]:
        """Recommends budget adjustment based on historical spending averages."""
        if not historical_spends:
            return {
                "category": self._category,
                "current_limit": str(self._limit),
                "recommended_limit": str(self._limit),
                "reason": "Insufficient historical data for adjustment.",
            }

        avg_spend = sum(historical_spends) / Decimal(len(historical_spends))
        # Provide a 10% safety buffer over historical average
        recommended = (avg_spend * Decimal("1.10")).quantize(Decimal("0.01"))

        diff = recommended - self._limit
        if diff > Decimal("20.00"):
            reason = f"Historical spend averages {avg_spend:.2f}. Recommend raising limit by {diff:.2f}."
        elif diff < Decimal("-20.00"):
            reason = f"Historical spend averages {avg_spend:.2f}. Recommend lowering limit by {abs(diff):.2f} to boost savings."
        else:
            reason = "Current budget is closely aligned with spending trends."

        return {
            "category": self._category,
            "current_limit": str(self._limit),
            "average_historical_spend": str(avg_spend.quantize(Decimal("0.01"))),
            "recommended_limit": str(recommended),
            "adjustment_delta": str(diff),
            "reason": reason,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "category": self._category,
            "limit": str(self._limit),
            "period": self._period.value,
            "period_key": self._period_key,
            "allow_rollover": self._allow_rollover,
            "rollover_amount": str(self._rollover_amount),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Budget":
        limit_val = data.get("limit_amount") if "limit_amount" in data else data.get("limit", "0.00")
        return cls(
            category=data["category"],
            limit_amount=Decimal(str(limit_val)),
            period=BudgetPeriod(data.get("period", BudgetPeriod.MONTHLY.value)),
            period_key=data.get("period_key", ""),
            allow_rollover=bool(data.get("allow_rollover", True)),
            rollover_amount=Decimal(str(data.get("rollover_amount", "0.00"))),
            budget_id=data.get("id"),
        )
