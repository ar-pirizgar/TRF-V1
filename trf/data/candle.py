"""Immutable OHLCV candle model.

This module defines the core market candle value object used by the Trading
Research Framework. The model is intentionally independent of pandas and other
third-party libraries so it can be reused across data, backtesting, and live
trading boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Self


@dataclass(frozen=True, slots=True)
class Candle:
    """Immutable OHLCV market candle.

    Args:
        timestamp: Timestamp associated with the candle.
        open: Opening price for the candle interval.
        high: Highest traded price during the candle interval.
        low: Lowest traded price during the candle interval.
        close: Closing price for the candle interval.
        volume: Traded volume during the candle interval.

    Raises:
        ValueError: If prices are not positive, the OHLC relationship is
            invalid, or volume is negative.
    """

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        """Validate OHLC price consistency and non-negative volume."""

        if self.open <= Decimal("0"):
            raise ValueError("open must be greater than zero")
        if self.high <= Decimal("0"):
            raise ValueError("high must be greater than zero")
        if self.low <= Decimal("0"):
            raise ValueError("low must be greater than zero")
        if self.close <= Decimal("0"):
            raise ValueError("close must be greater than zero")
        if self.high < self.open:
            raise ValueError("high must be greater than or equal to open")
        if self.high < self.close:
            raise ValueError("high must be greater than or equal to close")
        if self.high < self.low:
            raise ValueError("high must be greater than or equal to low")
        if self.low > self.open:
            raise ValueError("low must be less than or equal to open")
        if self.low > self.close:
            raise ValueError("low must be less than or equal to close")
        if self.low > self.high:
            raise ValueError("low must be less than or equal to high")
        if self.volume < Decimal("0"):
            raise ValueError("volume must be greater than or equal to zero")

    @property
    def body(self) -> Decimal:
        """Absolute distance between the candle open and close.

        Returns:
            Absolute price difference between close and open.
        """

        return abs(self.close - self.open)

    @property
    def range(self) -> Decimal:
        """Total distance between the candle high and low.

        Returns:
            Difference between high and low.
        """

        return self.high - self.low

    @property
    def upper_wick(self) -> Decimal:
        """Distance from the candle high to the higher of open and close.

        Returns:
            Upper wick size.
        """

        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> Decimal:
        """Distance from the lower of open and close to the candle low.

        Returns:
            Lower wick size.
        """

        return min(self.open, self.close) - self.low

    @property
    def midpoint(self) -> Decimal:
        """Midpoint between the candle high and low.

        Returns:
            Average of high and low.
        """

        return (self.high + self.low) / Decimal("2")

    @property
    def typical_price(self) -> Decimal:
        """Average of high, low, and close prices.

        Returns:
            Typical price calculated from high, low, and close.
        """

        return (self.high + self.low + self.close) / Decimal("3")

    @property
    def ohlc4(self) -> Decimal:
        """Average of open, high, low, and close prices.

        Returns:
            Four-price average calculated from open, high, low, and close.
        """

        return (self.open + self.high + self.low + self.close) / Decimal("4")

    @property
    def is_bullish(self) -> bool:
        """Whether the close price is greater than the open price.

        Returns:
            True when close is greater than open; otherwise False.
        """

        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Whether the close price is less than the open price.

        Returns:
            True when close is less than open; otherwise False.
        """

        return self.close < self.open

    @property
    def is_doji(self) -> bool:
        """Whether the candle body is no more than 5% of the candle range.

        Returns:
            True when body is less than or equal to 5% of range; otherwise
            False.
        """

        return self.body <= self.range * Decimal("0.05")

    def to_dict(self) -> dict[str, datetime | Decimal]:
        """Convert the candle to a dictionary.

        Returns:
            Dictionary containing the candle timestamp and OHLCV values.
        """

        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a candle from a dictionary.

        Args:
            data: Dictionary containing timestamp, open, high, low, close, and
                volume values.

        Returns:
            Candle instance built from the provided dictionary.

        Raises:
            KeyError: If any required key is missing.
            ValueError: If the resulting candle has invalid OHLCV values.
        """

        return cls(
            timestamp=data["timestamp"],
            open=Decimal(str(data["open"])),
            high=Decimal(str(data["high"])),
            low=Decimal(str(data["low"])),
            close=Decimal(str(data["close"])),
            volume=Decimal(str(data["volume"])),
        )

    def __repr__(self) -> str:
        """Return a concise developer representation of the candle.

        Returns:
            String representation containing all candle fields.
        """

        return (
            "Candle("
            f"timestamp={self.timestamp!r}, "
            f"open={self.open!r}, "
            f"high={self.high!r}, "
            f"low={self.low!r}, "
            f"close={self.close!r}, "
            f"volume={self.volume!r}"
            ")"
        )
