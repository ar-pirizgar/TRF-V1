"""Feature pipeline abstractions for the Trading Research Framework.

The feature pipeline executes registered market features in deterministic
priority order. Features receive a MarketWindow and MarketState, then update
only the provided state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from trf.core.market_state import MarketState
from trf.core.market_window import MarketWindow


class Feature(ABC):
    """Abstract base class for market feature implementations.

    Feature implementations calculate one independent market feature and write
    the result to the supplied MarketState.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique feature name.

        Returns:
            Stable feature name used for registration.
        """

    @property
    @abstractmethod
    def priority(self) -> int:
        """Feature execution priority.

        Returns:
            Integer priority. Lower values run earlier.
        """

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """Whether this feature should execute.

        Returns:
            True when the feature should run; otherwise False.
        """

    @abstractmethod
    def compute(
        self,
        window: MarketWindow,
        state: MarketState,
    ) -> None:
        """Compute the feature and update the market state.

        Args:
            window: Rolling historical candle window.
            state: Current market state to update.
        """


class FeaturePipeline:
    """Ordered registry and executor for market features.

    Features are registered by unique name and executed in ascending priority.
    Disabled features remain registered but are skipped during execution.
    """

    _DUPLICATE_NAME_MESSAGE: Final[str] = "duplicate feature name"

    def __init__(self) -> None:
        """Initialize an empty feature pipeline."""

        self._features: list[Feature] = []

    def register(self, feature: Feature) -> None:
        """Register a feature for pipeline execution.

        Args:
            feature: Feature instance to register.

        Raises:
            ValueError: If another registered feature uses the same name.
        """

        if feature.name in self.names():
            raise ValueError(self._DUPLICATE_NAME_MESSAGE)

        self._features.append(feature)
        self._features.sort(key=lambda item: item.priority)

    def unregister(self, feature: Feature) -> None:
        """Unregister a feature from the pipeline.

        Args:
            feature: Feature instance to remove.
        """

        self._features = [item for item in self._features if item is not feature]

    def clear(self) -> None:
        """Remove all registered features from the pipeline."""

        self._features.clear()

    def run(self, window: MarketWindow, state: MarketState) -> None:
        """Execute enabled features in ascending priority order.

        Args:
            window: Rolling historical candle window supplied to each feature.
            state: Market state supplied to each feature.
        """

        for feature in self._features:
            if feature.enabled:
                feature.compute(window, state)

    def names(self) -> list[str]:
        """Return registered feature names in execution order.

        Returns:
            List of registered feature names.
        """

        return [feature.name for feature in self._features]
