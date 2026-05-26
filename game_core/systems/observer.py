"""
Simulation Observer Interface — decoupled display/input from engine core.

The SimulationEngine notifies observers on significant events.
Observers are free to render, log, or forward events as they wish.
The engine knows nothing about how events are displayed.

Events are defined as ProtocolEvent subclasses that can be serialized
to dict for protocol transmission.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game_core.actions.base import ActionResult
    from game_core.domain.entities import World


class MessageType(Enum):
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
    CIRCLE_ACTIVITY = "circle_activity"
    NPC_ACTION = "npc_action"


class ProtocolEvent:
    """Base class for all protocol events."""

    message_type: MessageType = MessageType.ERROR

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        d = {"type": self.message_type.value}
        for key, value in asdict(self).items():
            if key == "message_type":
                continue
            if value is not None:
                d[key] = value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProtocolEvent | None:
        """Reconstruct from dict. Override in subclasses for complex events."""
        return None


@dataclass
class WorldStartEvent(ProtocolEvent):
    message_type: MessageType = MessageType.READY
    turn: int = 0
    world: dict = None

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.message_type.value, "turn": self.turn, "world": self.world}


@dataclass
class TurnStartEvent(ProtocolEvent):
    message_type: MessageType = MessageType.TURN_START
    turn: int = 0
    world_state: dict = None

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.message_type.value, "turn": self.turn, "world_state": self.world_state or {}}


@dataclass
class TurnEndEvent(ProtocolEvent):
    message_type: MessageType = MessageType.TURN_END
    turn: int = 0
    action_taken: str = None
    world_tick: int = 0


@dataclass
class ActionResultEvent(ProtocolEvent):
    message_type: MessageType = MessageType.ACTION_RESULT
    turn: int = 0
    action: str = ""
    success: bool = False
    message: str = ""
    state_delta: dict = None


@dataclass
class ActionSelectedEvent(ProtocolEvent):
    message_type: MessageType = MessageType.ACTION_RESULT
    turn: int = 0
    action: str = None


@dataclass
class MetricChangedEvent(ProtocolEvent):
    message_type: MessageType = MessageType.TICK
    turn: int = 0
    metric: str = ""
    old_val: float = 0.0
    new_val: float = 0.0


@dataclass
class GameEventData(ProtocolEvent):
    message_type: MessageType = MessageType.EVENT
    turn: int = 0
    event_type: str = ""
    title: str = ""
    summary: str = ""


@dataclass
class CrisisEvent(ProtocolEvent):
    message_type: MessageType = MessageType.CRISIS
    turn: int = 0
    metric: str = ""
    value: float = 0.0


@dataclass
class CircleFoundedEvent(ProtocolEvent):
    message_type: MessageType = MessageType.EVENT
    turn: int = 0
    circle_name: str = ""
    members: int = 0


@dataclass
class NpcCreatedEvent(ProtocolEvent):
    message_type: MessageType = MessageType.EVENT
    turn: int = 0
    npc_name: str = ""
    npc_role: str = ""


@dataclass
class NpcActionEvent(ProtocolEvent):
    message_type: MessageType = MessageType.NPC_ACTION
    turn: int = 0
    npc_name: str = ""
    action: str = ""
    message: str = ""
    success: bool = True


@dataclass
class EchoSpawnedEvent(ProtocolEvent):
    message_type: MessageType = MessageType.ECHO_SPAWNED
    turn: int = 0
    parent_name: str = ""
    daughter_name: str = ""


@dataclass
class CircleActivityEvent(ProtocolEvent):
    message_type: MessageType = MessageType.CIRCLE_ACTIVITY
    turn: int = 0
    circle_name: str = ""
    activity: str = ""


@dataclass
class ReincarnationCompleteEvent(ProtocolEvent):
    message_type: MessageType = MessageType.REINCARNATION_COMPLETE
    turn: int = 0
    new_host_name: str = ""


@dataclass
class WorldStateEvent(ProtocolEvent):
    message_type: MessageType = MessageType.WORLD_STATE
    turn: int = 0
    civ: dict = None
    world_state: dict = None
    entities: dict = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.message_type.value,
            "turn": self.turn,
            "civ": self.civ or {},
            "world_state": self.world_state or {},
            "entities": self.entities or {},
        }


@dataclass
class TickEvent(ProtocolEvent):
    message_type: MessageType = MessageType.TICK
    turn: int = 0
    world_tick: int = 0
    pressure: float = 0.0
    legitimacy: float = 0.0
    resources: float = 0.0
    events: list = None


@dataclass
class TerminatedEvent(ProtocolEvent):
    message_type: MessageType = MessageType.TERMINATED
    reason: str = ""


@dataclass
class ErrorEvent(ProtocolEvent):
    message_type: MessageType = MessageType.ERROR
    message: str = ""


class SimulationObserver(ABC):
    """
    Observer interface for simulation events.

    All methods return ProtocolEvent | None.
    Returning None means the observer doesn't care about this event.
    """

    def on_world_start(self, world: World) -> WorldStartEvent | None:
        """Called once at simulation start, before turn 1."""

    def on_turn_start(self, turn: int, world: World) -> TurnStartEvent | None:
        """Called at the start of each turn, before any action is taken."""

    def on_turn_end(self, turn: int, world: World, action_taken: str | None) -> TurnEndEvent | None:
        """Called at the end of each turn, after all effects are applied."""

    def on_action_selected(self, turn: int, action_name: str | None) -> ActionSelectedEvent | None:
        """Called when an action is selected (player or autoplay)."""

    def on_action_result(self, turn: int, action_name: str, result: ActionResult) -> ActionResultEvent | None:
        """Called after an action is executed with its result."""

    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float) -> MetricChangedEvent | None:
        """Called when a metric changes significantly."""

    def on_event(self, turn: int, event_type: str, title: str, summary: str) -> GameEventData | None:
        """Called when an event is generated (crisis, opportunity, etc.)."""

    def on_circle_founded(self, turn: int, circle_name: str, members: int) -> CircleFoundedEvent | None:
        """Called when a circle is founded."""

    def on_npc_created(self, turn: int, npc_name: str, npc_role: str) -> NpcCreatedEvent | None:
        """Called when a new NPC is created."""

    def on_npc_action(self, turn: int, npc_name: str, action: str, message: str) -> NpcActionEvent | None:
        """Called when an NPC takes an action."""

    def on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str) -> EchoSpawnedEvent | None:
        """Called when a new echo is spawned."""

    def on_world_state(self, turn: int, world: World) -> WorldStateEvent | None:
        """Called with the full world state at end of turn (for snapshots)."""

    def on_crisis(self, turn: int, metric: str, value: float) -> CrisisEvent | None:
        """Called when a crisis threshold is crossed."""

    def on_circle_activity(self, turn: int, circle_name: str, activity: str) -> CircleActivityEvent | None:
        """Called when a circle performs an activity."""

    def on_reincarnation_complete(self, turn: int, new_host_name: str) -> ReincarnationCompleteEvent | None:
        """Called when echo reincarnation process completes."""


class NullObserver(SimulationObserver):
    """No-op observer — does nothing. Used as placeholder."""
