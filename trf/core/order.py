"""Order model for the Trading Research Framework.

Orders represent executable instructions produced after risk management. They
carry execution inputs but do not execute themselves or represent open trades.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class OrderSide(StrEnum):
    """Executable order side."""

    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"


class OrderStatus(StrEnum):
    """Lifecycle status of an order instruction."""

    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class Order:
    """Immutable executable instruction.

    Args:
        id: Unique order identifier.
        symbol: Market symbol for the order.
        timeframe: Timeframe associated with the order.
        timestamp: Time at which the order was created.
        side: Executable side for the order.
        status: Current order lifecycle status.
        quantity: Quantity to execute.
        entry: Intended entry price.
        stop: Stop price associated with the order.
        target: Target price associated with the order.
        metadata: Additional order context unrelated to broker or portfolio
            state.

    Raises:
        ValueError: If quantity or price values are not positive.
    """

    id: str
    symbol: str
    timeframe: str
    timestamp: datetime
    side: OrderSide
    status: OrderStatus
    quantity: Decimal
    entry: Decimal
    stop: Decimal
    target: Decimal
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        """Validate order values and freeze metadata."""

        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

        if self.quantity <= Decimal("0"):
            raise ValueError("quantity must be greater than zero")
        if self.entry <= Decimal("0"):
            raise ValueError("entry must be greater than zero")
        if self.stop <= Decimal("0"):
            raise ValueError("stop must be greater than zero")
        if self.target <= Decimal("0"):
            raise ValueError("target must be greater than zero")

    @property
    def risk_per_unit(self) -> Decimal:
        """Absolute distance between entry and stop.

        Returns:
            Price risk per single unit.
        """

        return abs(self.entry - self.stop)

    @property
    def reward_per_unit(self) -> Decimal:
        """Absolute distance between entry and target.

        Returns:
            Price reward per single unit.
        """

        return abs(self.target - self.entry)

    @property
    def risk_reward_ratio(self) -> Decimal:
        """Reward divided by risk.

        Returns:
            Reward-to-risk ratio. Returns Decimal("0") when risk is zero.
        """

        if self.risk_per_unit == Decimal("0"):
            return Decimal("0")
        return self.reward_per_unit / self.risk_per_unit

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the order.

        Returns:
            Dictionary containing order fields. Datetime and Decimal values are
            represented as strings.
        """

        return {
            "id": self.id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "side": self.side.value,
            "status": self.status.value,
            "quantity": str(self.quantity),
            "entry": str(self.entry),
            "stop": str(self.stop),
            "target": str(self.target),
            "metadata": dict(self.metadata),
        }
