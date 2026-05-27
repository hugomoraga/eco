"""
Protocol package for CLI <-> TUI communication.

Re-exports events from observer.py and commands from messages.py.
"""

from core.application.processors.observer import (
    ActionResultEvent,
    ActionSelectedEvent,
    CircleActivityEvent,
    CircleFoundedEvent,
    CrisisEvent,
    EchoSpawnedEvent,
    ErrorEvent,
    GameEventData,
    MessageType,
    MetricChangedEvent,
    NpcActionEvent,
    NpcCreatedEvent,
    ProtocolEvent,
    ReadyEvent,
    ReincarnationCompleteEvent,
    TerminatedEvent,
    TickEvent,
    TurnEndEvent,
    TurnStartEvent,
    WorldStateEvent,
)
from core.ports.codec import decode, decode_command, encode, encode_many
from core.ports.messages import (
    ActionCommand,
    QueryCommand,
    QueryResponseEvent,
    QueryType,
    QuitCommand,
    UnionMessage,
)

__all__ = [
    "ActionCommand",
    "ActionResultEvent",
    "ActionSelectedEvent",
    "CircleActivityEvent",
    "CircleFoundedEvent",
    "CrisisEvent",
    "EchoSpawnedEvent",
    "ErrorEvent",
    "GameEventData",
    "MessageType",
    "MetricChangedEvent",
    "NpcActionEvent",
    "NpcCreatedEvent",
    "ProtocolEvent",
    "QueryCommand",
    "QueryResponseEvent",
    "QueryType",
    "QuitCommand",
    "ReadyEvent",
    "ReincarnationCompleteEvent",
    "TerminatedEvent",
    "TickEvent",
    "TurnEndEvent",
    "TurnStartEvent",
    "UnionMessage",
    "WorldStateEvent",
    "decode",
    "decode_command",
    "encode",
    "encode_many",
]
