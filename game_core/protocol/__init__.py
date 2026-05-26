"""
Protocol package for CLI <-> TUI communication.

Re-exports events from observer.py and commands from messages.py.
"""

from game_core.systems.observer import (
    MessageType,
    ProtocolEvent,
    TurnStartEvent,
    TurnEndEvent,
    ActionResultEvent,
    ActionSelectedEvent,
    GameEventData,
    MetricChangedEvent,
    CrisisEvent,
    CircleFoundedEvent,
    NpcCreatedEvent,
    NpcActionEvent,
    EchoSpawnedEvent,
    CircleActivityEvent,
    ReincarnationCompleteEvent,
    WorldStateEvent,
    TickEvent,
    TerminatedEvent,
    ErrorEvent,
)

from game_core.protocol.messages import (
    ActionCommand,
    QueryCommand,
    QueryType,
    QuitCommand,
    ReadyEvent,
    QueryResponseEvent,
    TickEvent,
    TerminatedEvent,
    ErrorEvent,
    UnionMessage,
)

from game_core.protocol.codec import encode, decode, encode_many, decode_command

__all__ = [
    "MessageType",
    "ProtocolEvent",
    "ActionCommand",
    "QueryCommand",
    "QueryType",
    "QuitCommand",
    "ReadyEvent",
    "QueryResponseEvent",
    "encode",
    "decode",
    "encode_many",
    "decode_command",
    "TurnStartEvent",
    "TurnEndEvent",
    "ActionResultEvent",
    "ActionSelectedEvent",
    "GameEventData",
    "MetricChangedEvent",
    "CrisisEvent",
    "CircleFoundedEvent",
    "NpcCreatedEvent",
    "NpcActionEvent",
    "EchoSpawnedEvent",
    "CircleActivityEvent",
    "ReincarnationCompleteEvent",
    "WorldStateEvent",
    "TickEvent",
    "TerminatedEvent",
    "ErrorEvent",
    "UnionMessage",
]
