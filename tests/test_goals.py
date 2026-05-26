"""
Tests for game_core.domain.goals module.
"""
from __future__ import annotations

import pytest
from core.domain.entities import World, WorldClock, Circle, CircleStatus, Echo
from core.domain.rules.goals import (
    Goal,
    GoalType,
    ProgressGoal,
    MaintainGoal,
    AccumulateGoal,
    SurviveGoal,
)


class TestProgressGoal:
    def test_progress_goal_evaluate_at_start(self):
        world = _create_world_with_circles(0)
        goal = ProgressGoal(
            goal_id="test_1",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        assert goal.evaluate(world, current_turn=1) < 1.0

    def test_progress_goal_evaluate_complete(self):
        world = _create_world_with_circles(5)
        goal = ProgressGoal(
            goal_id="test_2",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        assert goal.evaluate(world, current_turn=10) == 1.0

    def test_progress_goal_evaluate_partial(self):
        world = _create_world_with_circles(3)
        goal = ProgressGoal(
            goal_id="test_3",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=6.0,
            description="Fundar 6 círculos",
        )
        progress = goal.evaluate(world, current_turn=10)
        assert 0.0 < progress < 1.0

    def test_progress_goal_remaining_turns(self):
        goal = ProgressGoal(
            goal_id="test_4",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        assert goal.remaining_turns(5) == 15
        assert goal.remaining_turns(20) == 0
        assert goal.remaining_turns(25) == 0

    def test_progress_goal_progress_bar(self):
        world = _create_world_with_circles(3)
        goal = ProgressGoal(
            goal_id="test_5",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        bar = goal.progress_bar(world, current_turn=10)
        assert len(bar) == 10
        assert "█" in bar
        assert "░" in bar

    def test_progress_goal_is_player(self):
        goal = ProgressGoal(
            goal_id="test_6",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        assert goal.is_player is True

        npc_goal = ProgressGoal(
            goal_id="test_7",
            owner_id="npc_123",
            owner_name="NPC",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        assert npc_goal.is_player is False

    def test_progress_goal_to_dict(self):
        goal = ProgressGoal(
            goal_id="test_8",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        d = goal.to_dict()
        assert d["goal_id"] == "test_8"
        assert d["owner_id"] == "player"
        assert d["goal_type"] == "progress"
        assert d["metric"] == "circles"


class TestMaintainGoal:
    def test_maintain_goal_above_threshold(self):
        world = _create_world_with_state(legitimacy=75, pressure=30)
        goal = MaintainGoal(
            goal_id="test_m1",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="legitimacy",
            operator="gt",
            threshold=50.0,
            description="Mantener legitimidad > 50",
        )
        assert goal.evaluate(world, current_turn=10) == 1.0

    def test_maintain_goal_below_threshold(self):
        world = _create_world_with_state(legitimacy=30, pressure=30)
        goal = MaintainGoal(
            goal_id="test_m2",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="legitimacy",
            operator="gt",
            threshold=50.0,
            description="Mantener legitimidad > 50",
        )
        progress = goal.evaluate(world, current_turn=10)
        assert 0.0 < progress < 1.0

    def test_maintain_goal_lt_operator(self):
        world = _create_world_with_state(legitimacy=30, pressure=80)
        goal = MaintainGoal(
            goal_id="test_m3",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="pressure",
            operator="lt",
            threshold=50.0,
            description="Mantener presión < 50",
        )
        progress = goal.evaluate(world, current_turn=10)
        assert 0.0 < progress < 1.0


class TestAccumulateGoal:
    def test_accumulate_goal_full(self):
        world = _create_world_with_state(resources=100)
        goal = AccumulateGoal(
            goal_id="test_a1",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="resources",
            target=50.0,
            description="Acumular 50 recursos",
        )
        assert goal.evaluate(world, current_turn=10) == 1.0

    def test_accumulate_goal_partial(self):
        world = _create_world_with_state(resources=25)
        goal = AccumulateGoal(
            goal_id="test_a2",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="resources",
            target=100.0,
            description="Acumular 100 recursos",
        )
        progress = goal.evaluate(world, current_turn=10)
        assert 0.0 < progress < 1.0


class TestSurviveGoal:
    def test_survive_goal_full(self):
        world = _create_world_with_state()
        goal = SurviveGoal(
            goal_id="test_s1",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            turns_needed=15,
        )
        assert goal.evaluate(world, current_turn=15) == 1.0

    def test_survive_goal_partial(self):
        world = _create_world_with_state()
        goal = SurviveGoal(
            goal_id="test_s2",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            turns_needed=20,
        )
        progress = goal.evaluate(world, current_turn=10)
        assert progress == 0.5

    def test_survive_goal_description(self):
        goal = SurviveGoal(
            goal_id="test_s3",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            turns_needed=15,
        )
        assert "15" in goal.description


class TestGoalProgress:
    def test_goal_progress_bar(self):
        world = _create_world_with_circles(3)
        goal = ProgressGoal(
            goal_id="test_p1",
            owner_id="player",
            owner_name="Test",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        bar = goal.progress_bar(world, current_turn=10)
        assert len(bar) == 10
        filled = bar.count("█")
        empty = bar.count("░")
        assert filled + empty == 10
        assert filled >= 3 and filled <= 6


def _create_world_with_circles(num_circles: int) -> World:
    circles = [
        Circle(
            id=f"circle_{i}",
            name=f"Circle {i}",
            status=CircleStatus.ACTIVE,
        )
        for i in range(num_circles)
    ]
    world = World(
        clock=WorldClock(),
        circles=circles,
        legitimacy=50.0,
        pressure=30.0,
        resources_global=50.0,
    )
    return world


def _create_world_with_state(
    legitimacy: float = 50.0,
    pressure: float = 30.0,
    resources: float = 50.0,
) -> World:
    world = World(
        clock=WorldClock(),
        circles=[],
        legitimacy=legitimacy,
        pressure=pressure,
        resources_global=resources,
    )
    return world
