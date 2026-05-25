"""
Tests for game_core.domain entities.
"""
from __future__ import annotations

from game_core.domain.entities import (
    Circle,
    CircleEvent,
    CircleEventType,
    CircleStatus,
    Echo,
    EchoAttribute,
    EchoPhase,
    Faction,
    World,
    WorldClock,
)


class TestWorldClock:
    def test_advance(self):
        clock = WorldClock()
        assert clock.action_tick == 0
        assert clock.world_tick == 0

        clock.advance(15)
        assert clock.action_tick == 15
        assert clock.world_tick == 1  # 15 // 10

        clock.advance(25)
        assert clock.action_tick == 40
        assert clock.world_tick == 4

    def test_model_dump(self):
        clock = WorldClock()
        data = clock.model_dump()
        assert data["action_tick"] == 0
        assert data["world_tick"] == 0


class TestEcho:
    def test_create_echo(self):
        echo = Echo(name="Test Echo", essence="anarchism")
        assert echo.name == "Test Echo"
        assert echo.essence == "anarchism"
        assert echo.phase == EchoPhase.DORMANT

    def test_get_attribute(self):
        echo = Echo(
            attributes=[
                EchoAttribute(label="clarity", value=60.0),
                EchoAttribute(label="resonance", value=50.0),
            ]
        )
        attr = echo.get_attribute("clarity")
        assert attr is not None
        assert attr.value == 60.0

        missing = echo.get_attribute("nonexistent")
        assert missing is None

    def test_add_to_circle(self):
        echo = Echo(name="Test", essence="anarchism")
        assert echo.circles == []


class TestCircle:
    def test_create_circle(self):
        circle = Circle(name="Test Circle", essence="anarchism")
        assert circle.name == "Test Circle"
        assert circle.status == CircleStatus.ACTIVE

    def test_add_member(self):
        circle = Circle(name="Test", essence="anarchism", member_ids=[])
        circle.add_member("echo1")
        assert "echo1" in circle.member_ids
        assert circle.member_count == 1

    def test_remove_member(self):
        circle = Circle(name="Test", essence="anarchism", member_ids=["echo1", "echo2"])
        circle.remove_member("echo1")
        assert "echo1" not in circle.member_ids
        assert circle.member_count == 1

    def test_can_grow(self):
        circle = Circle(name="Test", essence="anarchism", influence=20, member_ids=["e1"])
        assert circle.can_grow() is True

        circle.influence = 10
        assert circle.can_grow() is False


class TestCircleEvent:
    def test_create_event(self):
        event = CircleEvent(
            type=CircleEventType.FOUNDED,
            turn=1,
            echo_id="echo1",
            details="Test event",
        )
        assert event.type == CircleEventType.FOUNDED
        assert event.turn == 1


class TestWorld:
    def test_create_world(self):
        world = World()
        assert world.pressure == 30.0
        assert world.legitimacy == 60.0

    def test_clamp_metrics(self):
        world = World(pressure=150, legitimacy=-10)
        world.clamp_metrics()
        assert world.pressure == 100.0
        assert world.legitimacy == 0.0

    def test_get_echo(self):
        echo = Echo(name="Test", essence="anarchism")
        world = World(echoes=[echo])
        found = world.get_echo(echo.id)
        assert found is echo

        missing = world.get_echo("nonexistent")
        assert missing is None

    def test_get_circle(self):
        circle = Circle(name="Test", essence="anarchism")
        world = World(circles=[circle])
        found = world.get_circle(circle.id)
        assert found is circle

    def test_evolve_metrics(self):
        world = World(pressure=30.0, legitimacy=60.0, resources_global=70.0)
        from game_core.systems.random import SeededRandom

        rng = SeededRandom.get_instance(42)
        drift = world.evolve_metrics(rng)

        assert "pressure" in drift
        assert "legitimacy" in drift
        assert "resources_global" in drift