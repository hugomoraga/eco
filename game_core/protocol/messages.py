from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageType(str, Enum):
    READY = "ready"
    TURN_START = "turn_start"
    ACTION_RESULT = "action_result"
    TURN_END = "turn_end"
    EVENT = "event"
    QUERY_RESPONSE = "query_response"
    CRISIS = "crisis"
    WORLD_STATE = "world_state"
    TICK = "tick"
    TERMINATED = "terminated"
    ERROR = "error"
    ACTION = "action"
    QUERY = "query"
    QUIT = "quit"
    ECHO_SPAWNED = "echo_spawned"
    REINCARNATION_COMPLETE = "reincarnation_complete"


class QueryType(str, Enum):
    WORLD_STATE = "world_state"
    AVAILABLE_ACTIONS = "available_actions"
    METRIC_HISTORY = "metric_history"
    PERSONS = "persons"
    CIRCLES = "circles"
    FACTIONS = "factions"
    MANIFESTOS = "manifestos"


@dataclass
class ActionCommand:
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
    query_id: str
    query_type: QueryType
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.QUERY.value,
            "query_id": self.query_id,
            "query_type": self.query_type.value,
            "params": self.params,
        }


@dataclass
class QuitCommand:
    def to_dict(self) -> dict[str, Any]:
        return {"type": MessageType.QUIT.value}


@dataclass
class ReadyEvent:
    initial_state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.READY.value,
            "initial_state": self.initial_state,
        }


@dataclass
class TurnStartEvent:
    turn: int
    world_tick: int
    world_state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.TURN_START.value,
            "turn": self.turn,
            "world_tick": self.world_tick,
            "world_state": self.world_state,
        }


@dataclass
class ActionResultEvent:
    turn: int
    action: str
    success: bool
    message: str
    delta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.ACTION_RESULT.value,
            "turn": self.turn,
            "action": self.action,
            "success": self.success,
            "message": self.message,
            "delta": self.delta,
        }


@dataclass
class TurnEndEvent:
    turn: int
    world_tick: int
    action_taken: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.TURN_END.value,
            "turn": self.turn,
            "world_tick": self.world_tick,
            "action_taken": self.action_taken,
        }


@dataclass
class GameEvent:
    turn: int
    event_type: str
    title: str
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.EVENT.value,
            "turn": self.turn,
            "event_type": self.event_type,
            "title": self.title,
            "summary": self.summary,
        }


@dataclass
class QueryResponseEvent:
    query_id: str
    query_type: QueryType
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.QUERY_RESPONSE.value,
            "query_id": self.query_id,
            "query_type": self.query_type.value,
            "data": self.data,
        }


@dataclass
class CrisisEvent:
    turn: int
    metric: str
    value: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.CRISIS.value,
            "turn": self.turn,
            "metric": self.metric,
            "value": self.value,
        }


@dataclass
class WorldStateEvent:
    turn: int
    civ: dict[str, Any]
    echo: dict[str, Any]
    metrics: dict[str, Any]
    entities: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.WORLD_STATE.value,
            "turn": self.turn,
            "civ": self.civ,
            "echo": self.echo,
            "metrics": self.metrics,
            "entities": self.entities,
        }


@dataclass
class TickEvent:
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
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.TERMINATED.value,
            "reason": self.reason,
        }


@dataclass
class ErrorEvent:
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.ERROR.value,
            "message": self.message,
        }


@dataclass
class EchoSpawnedEvent:
    turn: int
    parent_name: str
    daughter_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.ECHO_SPAWNED.value,
            "turn": self.turn,
            "parent_name": self.parent_name,
            "daughter_name": self.daughter_name,
        }


@dataclass
class ReincarnationCompleteEvent:
    turn: int
    new_host_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": MessageType.REINCARNATION_COMPLETE.value,
            "turn": self.turn,
            "new_host_name": self.new_host_name,
        }


UnionMessage = (
    ActionCommand
    | QueryCommand
    | QuitCommand
    | ReadyEvent
    | TurnStartEvent
    | ActionResultEvent
    | TurnEndEvent
    | GameEvent
    | QueryResponseEvent
    | CrisisEvent
    | WorldStateEvent
    | TickEvent
    | TerminatedEvent
    | ErrorEvent
    | EchoSpawnedEvent
    | ReincarnationCompleteEvent
)
