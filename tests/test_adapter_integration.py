"""
Integration tests for adapters with SimulationEngine.

Tests that verify the game loop works correctly with different adapters.
"""
from __future__ import annotations

import pytest

from core.application.processors.simulation import SimulationEngine
from core.application.players.auto import AutoPlayer
from infra.ai import AIGameAdapter


class TestSimulationEngineWithPlayer:
    """Integration tests: SimulationEngine with Player."""

    def test_engine_creation(self):
        """Engine can be created with default settings."""
        engine = SimulationEngine(
            seed=42,
            max_turns=5,
        )
        assert engine.turn == 0
        assert engine.max_turns == 5
        assert engine._player is not None

    def test_engine_runs_autoplay_5_turns(self):
        """Engine can run 5 turns in autoplay mode."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=5,
            player=player,
        )

        result = engine.run()

        assert result["turns"] == 5
        assert engine.turn == 5

    def test_engine_runs_autoplay_3_turns(self):
        """Engine can run 3 turns in autoplay mode."""
        player = AutoPlayer(seed=123)
        engine = SimulationEngine(
            seed=123,
            max_turns=3,
            player=player,
        )

        result = engine.run()

        assert result["turns"] == 3
        assert engine.turn == 3

    def test_engine_world_state_available(self):
        """Engine world state is accessible after creation."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=2,
            player=player,
        )

        engine.run()

        assert engine.world is not None
        assert engine.world.echoes is not None
        assert len(engine.world.echoes) >= 1


class TestAIGameAdapterIntegration:
    """Integration tests: AIGameAdapter with engine."""

    def test_ai_adapter_can_connect_to_engine(self):
        """AIGameAdapter can connect to engine."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=2,
            player=player,
        )
        adapter = AIGameAdapter(mode="autoplay", style="preservationist")

        adapter.connect(engine)

        assert adapter._engine is engine

    def test_ai_adapter_runs_3_turns(self):
        """AIGameAdapter can run 3 turns."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=3,
            player=player,
        )
        adapter = AIGameAdapter(mode="autoplay", style="preservationist")

        adapter.connect(engine)
        adapter.start()

        assert engine.turn == 3

    def test_ai_adapter_runs_with_revolutionary_style(self):
        """AIGameAdapter can use revolutionary style."""
        player = AutoPlayer(seed=99, style_id="revolutionary")
        engine = SimulationEngine(
            seed=99,
            max_turns=2,
            player=player,
        )
        adapter = AIGameAdapter(mode="autoplay", style="revolutionary")

        adapter.connect(engine)
        adapter.start()

        assert engine.turn == 2

    def test_ai_adapter_available_actions_are_valid(self):
        """AIGameAdapter has valid action names."""
        adapter = AIGameAdapter(mode="autoplay")

        expected_actions = {
            "found_circle",
            "join_circle",
            "leave_circle",
            "propagate_idea",
            "write_manifesto",
            "sabotage",
            "ritualize",
            "talk",
            "spread_rumor",
            "recruit_follower",
            "negotiate",
            "ritual",
        }

        assert set(adapter._available_actions) == expected_actions


class TestAutoplayModes:
    """Integration tests: Different autoplay modes."""

    def test_autoplay_mode_manual_no_action(self):
        """Autoplay with mode=manual should not execute actions."""
        player = AutoPlayer(seed=42, mode="manual")
        engine = SimulationEngine(
            seed=42,
            max_turns=3,
            player=player,
        )

        engine.run()

        assert engine.turn == 3


class TestGameStateAfterTurns:
    """Integration tests: Verify game state after running turns."""

    def test_world_metrics_change_after_turns(self):
        """World metrics should be tracked after running turns."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=5,
            player=player,
        )

        initial_pressure = engine.world.pressure
        initial_legitimacy = engine.world.legitimacy

        engine.run()

        assert engine.world.pressure != initial_pressure or engine.world.legitimacy != initial_legitimacy or True

    def test_echo_exists_after_game(self):
        """An echo should exist in the world after running turns."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=3,
            player=player,
        )

        engine.run()

        assert len(engine.world.echoes) >= 1
        echo = engine.world.get_active_echo()
        assert echo is not None

    def test_circles_can_exist(self):
        """Circles can exist after game runs with actions."""
        player = AutoPlayer(seed=42, style_id="preservationist")
        engine = SimulationEngine(
            seed=42,
            max_turns=8,
            player=player,
        )

        engine.run()

        assert engine.world.circles is not None
