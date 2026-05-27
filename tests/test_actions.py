"""
Tests for game_core.actions.
"""
from __future__ import annotations

from core.application.actions.base import Action, ActionContext, ActionResult
from core.application.actions.circle_actions import FoundCircle, JoinCircle, LeaveCircle
from core.application.actions.manifesto_actions import WriteManifesto
from core.application.actions.social_actions import PropagateIdea, Talk, Sabotage, Ritualize
from core.domain import Circle, Echo, World, WorldClock


class TestActionContext:
    def test_create_context(self):
        ctx = ActionContext(world_tick=5, action_tick=10, autoplay=False)
        assert ctx.world_tick == 5
        assert ctx.action_tick == 10
        assert ctx.autoplay is False


class TestActionResult:
    def test_create_result(self):
        result = ActionResult(
            success=True,
            message="Test action",
            state_delta={"test": 1},
        )
        assert result.success is True
        assert result.message == "Test action"


class TestFoundCircle:
    def test_found_circle(self):
        echo = Echo(name="Founder", essence="anarchism")
        world = World(echoes=[echo])

        ctx = ActionContext(world_tick=0, action_tick=0, autoplay=False)
        action = FoundCircle()

        result = action.execute(echo, world, ctx)
        assert result.success is True
        assert len(world.circles) == 1
        assert echo.circles == [world.circles[0].id]


class TestJoinCircle:
    def test_join_circle_no_circles(self):
        echo = Echo(name="Test", essence="anarchism")
        world = World(echoes=[echo], circles=[])

        ctx = ActionContext(world_tick=0, action_tick=0, autoplay=False)
        action = JoinCircle()

        result = action.execute(echo, world, ctx)
        assert result.success is False
        assert "No hay" in result.message


class TestLeaveCircle:
    def test_leave_circle_not_member(self):
        echo = Echo(name="Test", essence="anarchism", circles=[])
        world = World(echoes=[echo])

        ctx = ActionContext(world_tick=0, action_tick=0, autoplay=False)
        action = LeaveCircle()

        result = action.execute(echo, world, ctx)
        assert result.success is False
        assert "No eres" in result.message


class TestTalk:
    def test_talk_stub(self):
        echo = Echo(name="Test", essence="anarchism")
        world = World(echoes=[echo])

        ctx = ActionContext(world_tick=0, action_tick=0, autoplay=False)
        action = Talk()

        result = action.execute(echo, world, ctx)
        assert result.success is True
        assert result.message is not None


class TestSabotage:
    def test_sabotage_effects(self):
        echo = Echo(name="Test", essence="anarchism")
        world = World(echoes=[echo], legitimacy=60.0, resources_global=70.0, pressure=30.0)

        ctx = ActionContext(world_tick=0, action_tick=0, autoplay=False)
        action = Sabotage()

        result = action.execute(echo, world, ctx)
        assert result.success is True
        assert world.legitimacy == 55.0  # -5
        assert world.resources_global == 65.0  # -5
        assert world.pressure == 38.0  # +8