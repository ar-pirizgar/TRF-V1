"""Rolling market data window for the Trading Research Framework.

This module provides the framework's only historical candle container. Feature
components receive a MarketWindow instance instead of raw candle collections,
which keeps historical market access explicit and isolated.
"""

from __future__ import annotations

from collections import deque
from decimal import Decimal
from typing import Iterator

from trf.data.candle import Candle


class MarketWindow:
    """Rolling history of immutable candle objects.

    Args:
        max_size: Maximum number of candles retained in the rolling window.

    Raises:
        ValueError: If max_size is not greater than zero.
    """

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize the rolling market window.

        Args:
            max_size: Maximum number of candles retained in the window.

        Raises:
            ValueError: If max_size is not greater than zero.
        """

        if max_size <= 0:
            raise ValueError("max_size must be greater than zero")

        self._candles: deque[Candle] = deque(maxlen=max_size)

    @property
    def size(self) -> int:
        """Current number of candles in the window.

        Returns:
            Number of candles currently stored.
        """

        return len(self._candles)

    @property
    def empty(self) -> bool:
        """Whether the window contains no candles.

        Returns:
            True when the window is empty; otherwise False.
        """

        return len(self._candles) == 0

    @property
    def first(self) -> Candle | None:
        """Oldest candle in the window.

        Returns:
            Oldest candle, or None when the window is empty.
        """

        if self.empty:
            return None
        return self._candles[0]

    @property
    def last(self) -> Candle | None:
        """Newest candle in the window.

        Returns:
            Newest candle, or None when the window is empty.
        """

        if self.empty:
            return None
        return self._candles[-1]

    def append(self, candle: Candle) -> None:
        """Append a candle to the rolling window.

        Args:
            candle: Candle instance to append.

        Raises:
            TypeError: If candle is not a Candle instance.
        """

        if not isinstance(candle, Candle):
            raise TypeError("candle must be a Candle instance")

        self._candles.append(candle)

    def clear(self) -> None:
        """Remove all candles from the window."""

        self._candles.clear()

    def has(self, count: int) -> bool:
        """Return whether at least count candles are available.

        Args:
            count: Required number of candles.

        Returns:
            True when the window contains at least count candles; otherwise
            False.
        """

        return len(self._candles) >= count

    def get(self, index: int) -> Candle:
        """Return a candle by index.

        Args:
            index: Zero-based candle index. Negative indexes are supported.

        Returns:
            Candle at the requested index.

        Raises:
            IndexError: If index is outside the current window.
        """

        return self._candles[index]

    def tail(self, count: int) -> list[Candle]:
        """Return the most recent candles.

        Args:
            count: Number of recent candles to return.

        Returns:
            List containing up to count most recent candles in chronological
            order.

        Raises:
            ValueError: If count is negative.
        """

        if count < 0:
            raise ValueError("count must be greater than or equal to zero")
        if count == 0:
            return []
        return list(self._candles)[-count:]

    def opens(self) -> list[Decimal]:
        """Return open prices for all candles in chronological order.

        Returns:
            List of open prices.
        """

        return [candle.open for candle in self._candles]

    def highs(self) -> list[Decimal]:
        """Return high prices for all candles in chronological order.

        Returns:
            List of high prices.
        """

        return [candle.high for candle in self._candles]

    def lows(self) -> list[Decimal]:
        """Return low prices for all candles in chronological order.

        Returns:
            List of low prices.
        """

        return [candle.low for candle in self._candles]

    def closes(self) -> list[Decimal]:
        """Return close prices for all candles in chronological order.

        Returns:
            List of close prices.
        """

        return [candle.close for candle in self._candles]

    def volumes(self) -> list[Decimal]:
        """Return volumes for all candles in chronological order.

        Returns:
            List of candle volumes.
        """

        return [candle.volume for candle in self._candles]

    def __len__(self) -> int:
        """Return the number of candles in the window.

        Returns:
            Current window size.
        """

        return len(self._candles)

    def __iter__(self) -> Iterator[Candle]:
        """Iterate over candles in chronological order.

        Returns:
            Iterator over stored candles.
        """

        return iter(self._candles)

    def __getitem__(self, index: int) -> Candle:
        """Return a candle by index.

        Args:
            index: Zero-based candle index. Negative indexes are supported.

        Returns:
            Candle at the requested index.

        Raises:
            IndexError: If index is outside the current window.
        """

        return self.get(index)
