"""Core event definitions for the Trading Research Framework.

This module defines the framework's foundational event types and event
containers. Events are intentionally lightweight data structures; they carry
typed metadata and payloads without implementing trading, broker, or backtest
business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum, auto
from types import MappingProxyType
from typing import Any, Mapping


class EventType(StrEnum):
    """Enumeration of event categories emitted within the framework."""

    NEW_CANDLE = auto()
    FEATURES_UPDATED = auto()
    SIGNAL_GENERATED = auto()
    ORDER_CREATED = auto()
    ORDER_FILLED = auto()
    POSITION_OPENED = auto()
    POSITION_UPDATED = auto()
    POSITION_CLOSED = auto()
    BACKTEST_STARTED = auto()
    BACKTEST_FINISHED = auto()
    ERROR = auto()


@dataclass(slots=True)
class Event:
    """Base event container used by all framework event messages.

    Attributes:
        event_type: Category describing the event's role in the system.
        timestamp: Time at which the event was created or observed.
        payload: Event-specific data carried as a read-only mapping.
    """

    event_type: EventType
    timestamp: datetime
    payload: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(slots=True)
class CandleEvent(Event):
    """Event emitted when a new market candle is available."""


@dataclass(slots=True)
class SignalEvent(Event):
    """Event emitted when a strategy signal has been generated."""


@dataclass(slots=True)
class OrderEvent(Event):
    """Event emitted for order lifecycle updates."""


@dataclass(slots=True)
class PositionEvent(Event):
    """Event emitted for position lifecycle updates."""
