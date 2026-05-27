"""
Protocol messages for CLI <-> TUI communication.

This module defines:
- Commands (from TUI to CLI via stdin): ActionCommand, QueryCommand, QuitCommand
- Events (from CLI to TUI via stdout): re-exported from observer.py

The single source of truth for events is observer.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.application.processors.observer import (
    MessageType,
    ProtocolEvent,
)


class QueryType(str, Enum):
    """Query types for query commands."""

    WORLD_STATE = "world_state"
    AVAILABLE_ACTIONS = "available_actions"
    METRIC_HISTORY = "metric_history"
    PERSONS = "persons"
    CIRCLES = "circles"
    FACTIONS = "factions"
    MANIFESTOS = "manifestos"


@dataclass
class ActionCommand:
    """Command from TUI to CLI to execute an action."""

    turn: int
    action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.ACTION.value,
            "turn": self.turn,
            "action": self.action,
        }


@dataclass
class QueryCommand:
    """Command from TUI to CLI to query state."""

    query_id: str
    query_type: QueryType
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.QUERY.value,
            "query_id": self.query_id,
            "query_type": self.query_type.value
            if hasattr(self.query_type, "value")
            else self.query_type,
            "params": self.params,
        }


@dataclass
class QuitCommand:
    """Command from TUI to CLI to quit."""

    def to_dict(self) -> dict[str, Any]:
        return {"type": MessageType.QUIT.value}


@dataclass
class ReadyEvent:
    """Initial ready event sent when CLI starts."""

    initial_state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.READY.value,
            "initial_state": self.initial_state,
        }


@dataclass
class QueryResponseEvent:
    """Response to a query command."""

    query_id: str
    query_type: QueryType
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.QUERY_RESPONSE.value,
            "query_id": self.query_id,
            "query_type": self.query_type.value
            if hasattr(self.query_type, "value")
            else self.query_type,
            "data": self.data,
        }


@dataclass
class TickEvent:
    """Tick event for periodic updates."""

    turn: int
    world_tick: int
    action_result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.TICK.value,
            "turn": self.turn,
            "world_tick": self.world_tick,
            "action_result": self.action_result,
        }


@dataclass
class TerminatedEvent:
    """Event sent when simulation terminates."""

    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.TERMINATED.value,
            "reason": self.reason,
        }


@dataclass
class ErrorEvent:
    """Error event."""

    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.ERROR.value,
            "message": self.message,
        }


UnionMessage = (
    ActionCommand
    | QueryCommand
    | QuitCommand
    | ReadyEvent
    | QueryResponseEvent
    | TickEvent
    | TerminatedEvent
    | ErrorEvent
    | ProtocolEvent
)
