"""
Tests for the event protocol system.

Ensures that events are properly defined and serialized through the protocol.
"""
import pytest

from core.application.processors.observer import (
    MessageType,
    ProtocolEvent,
    TurnStartEvent,
    TurnEndEvent,
    ActionResultEvent,
    GameEventData,
    CrisisEvent,
    CircleActivityEvent,
    NpcActionEvent,
    EchoSpawnedEvent,
    ReincarnationCompleteEvent,
    WorldStateEvent,
    TickEvent,
    TerminatedEvent,
    ErrorEvent,
)
from core.ports.codec import encode, decode


class TestEventSerialization:
    """Test that events serialize and deserialize correctly."""

    def test_npc_action_event_to_dict(self):
        """NpcActionEvent should serialize with all fields."""
        event = NpcActionEvent(
            turn=5,
            npc_name="Test NPC",
            action="talk",
            message="Test message",
            success=True,
        )
        d = event.to_dict()
        assert d["type"] == "npc_action"
        assert d["turn"] == 5
        assert d["npc_name"] == "Test NPC"
        assert d["action"] == "talk"
        assert d["message"] == "Test message"
        assert d["success"] is True

    def test_npc_action_event_roundtrip(self):
        """NpcActionEvent should survive encode/decode cycle."""
        event = NpcActionEvent(
            turn=5,
            npc_name="Test NPC",
            action="talk",
            message="Test message",
            success=True,
        )
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, NpcActionEvent)
        assert decoded.turn == 5
        assert decoded.npc_name == "Test NPC"
        assert decoded.action == "talk"

    def test_crisis_event_roundtrip(self):
        """CrisisEvent should survive encode/decode cycle."""
        event = CrisisEvent(turn=3, metric="pressure", value=95.0)
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, CrisisEvent)
        assert decoded.turn == 3
        assert decoded.metric == "pressure"
        assert decoded.value == 95.0

    def test_turn_start_event_roundtrip(self):
        """TurnStartEvent should survive encode/decode cycle."""
        event = TurnStartEvent(turn=1, world_state={"pressure": 30.0})
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, TurnStartEvent)
        assert decoded.turn == 1

    def test_action_result_event_roundtrip(self):
        """ActionResultEvent should survive encode/decode cycle."""
        event = ActionResultEvent(
            turn=2,
            action="found_circle",
            success=True,
            message="Circle founded",
            state_delta={"circles_added": 1},
        )
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, ActionResultEvent)
        assert decoded.action == "found_circle"
        assert decoded.success is True

    def test_game_event_data_roundtrip(self):
        """GameEventData should survive encode/decode cycle."""
        event = GameEventData(
            turn=4,
            event_type="crisis",
            title="Test Crisis",
            summary="A test crisis occurred",
        )
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, GameEventData)
        assert decoded.title == "Test Crisis"

    def test_circle_activity_event_roundtrip(self):
        """CircleActivityEvent should survive encode/decode cycle."""
        event = CircleActivityEvent(
            turn=6,
            circle_name="Test Circle",
            activity="grew by attracting new member",
        )
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, CircleActivityEvent)
        assert decoded.circle_name == "Test Circle"

    def test_echo_spawned_event_roundtrip(self):
        """EchoSpawnedEvent should survive encode/decode cycle."""
        event = EchoSpawnedEvent(
            turn=7,
            parent_name="Parent Echo",
            daughter_name="Daughter Echo",
        )
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, EchoSpawnedEvent)
        assert decoded.parent_name == "Parent Echo"
        assert decoded.daughter_name == "Daughter Echo"

    def test_reincarnation_complete_event_roundtrip(self):
        """ReincarnationCompleteEvent should survive encode/decode cycle."""
        event = ReincarnationCompleteEvent(
            turn=8,
            new_host_name="New Host",
        )
        encoded = encode(event)
        decoded = decode(encoded)
        assert decoded is not None
        assert isinstance(decoded, ReincarnationCompleteEvent)
        assert decoded.new_host_name == "New Host"


class TestMessageType:
    """Test MessageType enum values."""

    def test_npc_action_type(self):
        """NPC_ACTION message type should exist and have correct value."""
        assert MessageType.NPC_ACTION.value == "npc_action"

    def test_all_event_types_defined(self):
        """All expected event types should be defined."""
        expected_types = [
            "ready",
            "turn_start",
            "action_result",
            "turn_end",
            "event",
            "crisis",
            "world_state",
            "tick",
            "terminated",
            "error",
            "action",
            "query",
            "quit",
            "echo_spawned",
            "reincarnation_complete",
            "circle_activity",
            "npc_action",
        ]
        for type_name in expected_types:
            assert hasattr(MessageType, type_name.upper()), f"Missing MessageType.{type_name.upper()}"


class TestProtocolObserver:
    """Test that ProtocolObserver properly converts events."""

    def test_protocol_observer_import(self):
        """ProtocolObserver should be importable."""
        from adapters.cli import ProtocolObserver
        assert ProtocolObserver is not None

    def test_npc_action_event_in_union(self):
        """NpcActionEvent should be usable in protocol."""
        event = NpcActionEvent(
            turn=1,
            npc_name="Test",
            action="test",
            message="test",
        )
        encoded = encode(event)
        assert encoded is not None
        assert '"type": "npc_action"' in encoded
