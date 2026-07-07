"""Risk management primitives for the Trading Research Framework.

The risk manager converts signal risk into a position size. It does not create
orders, access portfolio state, or communicate with brokers.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from trf.core.signal import Signal


@dataclass(slots=True)
class RiskConfig:
    """Configuration for deterministic position sizing.

    Args:
        risk_per_trade: Fraction of account balance risked per trade.
        max_position_size: Maximum permitted position size.
        min_position_size: Minimum permitted position size.
        allow_fractional: Whether fractional position sizes are allowed.

    Raises:
        ValueError: If risk or position size constraints are invalid.
    """

    risk_per_trade: Decimal
    max_position_size: Decimal
    min_position_size: Decimal
    allow_fractional: bool = True

    def __post_init__(self) -> None:
        """Validate risk configuration values."""

        if self.risk_per_trade <= Decimal("0"):
            raise ValueError("risk_per_trade must be greater than zero")
        if self.max_position_size <= Decimal("0"):
            raise ValueError("max_position_size must be greater than zero")
        if self.min_position_size <= Decimal("0"):
            raise ValueError("min_position_size must be greater than zero")
        if self.min_position_size > self.max_position_size:
            raise ValueError("min_position_size must be less than or equal to max_position_size")


class RiskManager:
    """Calculates position size from account balance and signal risk.

    Args:
        config: Risk configuration used for all position size calculations.
    """

    def __init__(self, config: RiskConfig) -> None:
        """Initialize the risk manager.

        Args:
            config: Risk configuration used for sizing.
        """

        self._config = config

    def calculate_position_size(
        self,
        account_balance: Decimal,
        signal: Signal,
    ) -> Decimal:
        """Calculate the executable position size for a signal.

        Args:
            account_balance: Account balance available for risk calculation.
            signal: Signal containing entry and stop distance.

        Returns:
            Position size clamped to the configured minimum and maximum.

        Raises:
            ValueError: If account_balance is not positive or signal risk is
                zero.
        """

        if account_balance <= Decimal("0"):
            raise ValueError("account_balance must be greater than zero")
        if signal.risk <= Decimal("0"):
            raise ValueError("signal risk must be greater than zero")

        risk_amount = account_balance * self._config.risk_per_trade
        position_size = risk_amount / signal.risk
        position_size = max(self._config.min_position_size, position_size)
        position_size = min(self._config.max_position_size, position_size)

        if not self._config.allow_fractional:
            return Decimal(int(position_size))

        return position_size
