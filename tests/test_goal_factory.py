"""
Tests for game_core.factory.goal_factory module.
"""

from __future__ import annotations

from core.domain import Person, World, WorldClock
from core.domain.rules.goals import (
    GoalType,
    ProgressGoal,
)
from core.factories.goal_factory import (
    GOAL_TEMPLATES,
    PLAYER_GOAL_POOL,
    GoalFactory,
)


class TestGoalFactoryCreatePlayerGoals:
    def test_creates_correct_number_of_goals(self):
        goals = GoalFactory.create_player_goals(n_options=3, turn_limit=20)
        assert len(goals) == 3

    def test_goals_are_progress_type(self):
        goals = GoalFactory.create_player_goals(n_options=3, turn_limit=20)
        for goal in goals:
            assert isinstance(goal, ProgressGoal)

    def test_goals_have_player_owner(self):
        goals = GoalFactory.create_player_goals(n_options=3, turn_limit=20)
        for goal in goals:
            assert goal.owner_id == "player"
            assert goal.is_player is True

    def test_goals_have_correct_turn_limit(self):
        goals = GoalFactory.create_player_goals(n_options=3, turn_limit=15)
        for goal in goals:
            assert goal.turn_limit == 15

    def test_goals_are_unique(self):
        goals = GoalFactory.create_player_goals(n_options=3, turn_limit=20)
        descriptions = [g.description for g in goals]
        assert len(descriptions) == len(set(descriptions))


class TestGoalFactoryCreateNpcGoal:
    def test_creates_goal_for_artisan(self):
        npc = Person(id="npc_1", name="Test Artisan", archetype="artisan", type="npc")
        goal = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=42)
        assert goal.owner_id == "npc_1"
        assert goal.owner_name == "Test Artisan"
        assert goal.is_player is False

    def test_creates_goal_for_warrior(self):
        npc = Person(id="npc_2", name="Test Warrior", archetype="warrior", type="npc")
        goal = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=42)
        assert goal is not None
        assert goal.goal_type in [
            GoalType.PROGRESS,
            GoalType.MAINTAIN,
            GoalType.ACCUMULATE,
            GoalType.SURVIVE,
        ]

    def test_creates_goal_for_neutral_archetype(self):
        npc = Person(id="npc_3", name="Test Neutral", archetype="neutral", type="npc")
        goal = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=42)
        assert goal is not None

    def test_same_seed_produces_same_goal_type(self):
        npc = Person(id="npc_4", name="Test NPC", archetype="merchant", type="npc")
        goal1 = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=123)
        goal2 = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=123)
        assert type(goal1) == type(goal2)

    def test_different_seeds_may_produce_different_goals(self):
        npc = Person(id="npc_5", name="Test NPC", archetype="scholar", type="npc")
        goal1 = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=1)
        goal2 = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=2)
        assert goal1 is not None
        assert goal2 is not None


class TestGoalTemplates:
    def test_goal_templates_exist(self):
        assert "circles" in GOAL_TEMPLATES
        assert "legitimacy" in GOAL_TEMPLATES
        assert "resources" in GOAL_TEMPLATES
        assert len(GOAL_TEMPLATES["circles"]) > 0


class TestPlayerGoalPool:
    def test_player_goal_pool_has_variety(self):
        assert len(PLAYER_GOAL_POOL) >= 5
        metrics = [g["metric"] for g in PLAYER_GOAL_POOL]
        assert "circles" in metrics
        assert "legitimacy" in metrics

    def test_player_goal_pool_has_difficulty(self):
        for goal in PLAYER_GOAL_POOL:
            assert "difficulty" in goal
            assert 1 <= goal["difficulty"] <= 5


class TestGoalEvaluateInContext:
    def test_npc_goal_evaluates_against_world(self):
        world = World(
            clock=WorldClock(),
            circles=[],
            legitimacy=50.0,
            pressure=30.0,
            resources_global=50.0,
        )
        npc = Person(id="npc_eval", name="Eval NPC", archetype="artisan", type="npc")
        goal = GoalFactory.create_npc_goal(npc, turn_limit=20, seed=42)

        progress = goal.evaluate(world, current_turn=10)
        assert isinstance(progress, float)
        assert 0.0 <= progress <= 1.0
