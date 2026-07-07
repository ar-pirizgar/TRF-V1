"""Market state model for the Trading Research Framework.

This module defines a structured container for the complete observable market
state at a single point in time. It stores candle data, indicator values,
strategy context, and extensible metadata without implementing trading
decisions or indicator calculations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum, auto
from typing import Any

from trf.data.candle import Candle


class MarketBias(StrEnum):
    """Directional market bias labels."""

    LONG = auto()
    SHORT = auto()
    NEUTRAL = auto()


@dataclass(slots=True)
class MarketState:
    """Complete market state for a symbol and timeframe at one point in time.

    Args:
        symbol: Market symbol represented by the state.
        timeframe: Candle timeframe represented by the state.
        candle: Current OHLCV candle.
        ema_fast: Fast exponential moving average value, if available.
        ema_slow: Slow exponential moving average value, if available.
        atr: Average true range value, if available.
        adx: Average directional index value, if available.
        rsi: Relative strength index value, if available.
        bias: Strategy bias associated with the state.
        active_zone: Active strategy zone label, if available.
        scenario: Strategy scenario label, if available.
        extra: Additional metadata associated with the state.
    """

    symbol: str
    timeframe: str
    candle: Candle
    ema_fast: Decimal | None = None
    ema_slow: Decimal | None = None
    atr: Decimal | None = None
    adx: Decimal | None = None
    rsi: Decimal | None = None
    bias: MarketBias = MarketBias.NEUTRAL
    active_zone: str | None = None
    scenario: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        """Set a metadata value in the state's extra dictionary.

        Args:
            key: Metadata key to store.
            value: Metadata value to associate with the key.
        """

        self.extra[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Return a metadata value from the state's extra dictionary.

        Args:
            key: Metadata key to read.
            default: Value returned when the key is not present.

        Returns:
            Stored metadata value, or the provided default.
        """

        return self.extra.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable dictionary of the current market state.

        Returns:
            Dictionary containing core state, indicator values, strategy
            context, and metadata. Datetime and Decimal values are represented
            as strings.
        """

        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "candle": {
                "timestamp": self.candle.timestamp.isoformat(),
                "open": str(self.candle.open),
                "high": str(self.candle.high),
                "low": str(self.candle.low),
                "close": str(self.candle.close),
                "volume": str(self.candle.volume),
            },
            "indicators": {
                "ema_fast": self._decimal_to_string(self.ema_fast),
                "ema_slow": self._decimal_to_string(self.ema_slow),
                "atr": self._decimal_to_string(self.atr),
                "adx": self._decimal_to_string(self.adx),
                "rsi": self._decimal_to_string(self.rsi),
            },
            "strategy_context": {
                "bias": self.bias,
                "active_zone": self.active_zone,
                "scenario": self.scenario,
            },
            "extra": dict(self.extra),
        }

    @staticmethod
    def _decimal_to_string(value: Decimal | None) -> str | None:
        """Convert an optional Decimal value to a string.

        Args:
            value: Decimal value to convert.

        Returns:
            String representation of the value, or None.
        """

        if value is None:
            return None
        return str(value)
