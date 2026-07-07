"""Trading signal model for the Trading Research Framework.

Signals represent market intent produced by strategies. They describe a
trading opportunity without execution, broker, portfolio, sizing, commission,
or slippage information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class SignalSide(StrEnum):
    """Permitted trading intent directions for a signal."""

    LONG = "LONG"
    SHORT = "SHORT"
    CLOSE = "CLOSE"


class SignalConfidence(StrEnum):
    """Discrete confidence labels assigned by a strategy."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass(frozen=True, slots=True)
class Signal:
    """Immutable trading opportunity produced by a strategy.

    Args:
        symbol: Market symbol for the trading opportunity.
        timeframe: Timeframe associated with the signal.
        timestamp: Time at which the signal was produced.
        side: Trading intent direction.
        entry: Intended entry price.
        stop: Invalidating price for the trading idea.
        target: Intended target price.
        confidence: Strategy-assigned confidence label.
        reason: Human-readable explanation for the signal.
        metadata: Additional signal context that is unrelated to execution.

    Raises:
        ValueError: If prices are not positive or the price relationship is
            invalid for the signal side.
    """

    symbol: str
    timeframe: str
    timestamp: datetime
    side: SignalSide
    entry: Decimal
    stop: Decimal
    target: Decimal
    confidence: SignalConfidence
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        """Validate signal prices and side-specific price relationships."""

        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

        if self.entry <= Decimal("0"):
            raise ValueError("entry must be greater than zero")
        if self.stop <= Decimal("0"):
            raise ValueError("stop must be greater than zero")
        if self.target <= Decimal("0"):
            raise ValueError("target must be greater than zero")

        if self.side is SignalSide.LONG and not self.stop < self.entry < self.target:
            raise ValueError("LONG signals require stop < entry < target")
        if self.side is SignalSide.SHORT and not self.target < self.entry < self.stop:
            raise ValueError("SHORT signals require target < entry < stop")
        if self.side is SignalSide.CLOSE and not self.entry == self.stop == self.target:
            raise ValueError("CLOSE signals require entry == stop == target")

    @property
    def risk(self) -> Decimal:
        """Absolute distance between entry and stop.

        Returns:
            Price risk represented by the signal.
        """

        return abs(self.entry - self.stop)

    @property
    def reward(self) -> Decimal:
        """Absolute distance between entry and target.

        Returns:
            Price reward represented by the signal.
        """

        return abs(self.target - self.entry)

    @property
    def risk_reward_ratio(self) -> Decimal:
        """Reward divided by risk.

        Returns:
            Reward-to-risk ratio. CLOSE signals return Decimal("0") because
            their entry, stop, and target are equal.
        """

        if self.risk == Decimal("0"):
            return Decimal("0")
        return self.reward / self.risk

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the signal.

        Returns:
            Dictionary containing signal intent, price levels, confidence,
            reason, and metadata. Datetime and Decimal values are represented
            as strings.
        """

        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "side": self.side.value,
            "entry": str(self.entry),
            "stop": str(self.stop),
            "target": str(self.target),
            "confidence": self.confidence.value,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }
