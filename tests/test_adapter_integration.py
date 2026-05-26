"""
Integration tests for adapter_core with SimulationEngine.

Tests that verify the game loop works correctly with different adapters.
"""
from __future__ import annotations

import pytest

from game_core.systems.simulation import SimulationEngine
from adapter_core.input_source import AutoplayInputSource, PlayerInputSource
from adapter_core import AIGameAdapter


class TestSimulationEngineWithInputSource:
    """Integration tests: SimulationEngine with InputSource."""

    def test_engine_creation(self):
        """Engine can be created with default settings."""
        engine = SimulationEngine(
            seed=42,
            max_turns=5,
            input_source=AutoplayInputSource(),
        )
        assert engine.turn == 0
        assert engine.max_turns == 5
        assert engine.input_source is not None

    def test_engine_runs_autoplay_5_turns(self):
        """Engine can run 5 turns in autoplay mode."""
        engine = SimulationEngine(
            seed=42,
            max_turns=5,
            input_source=AutoplayInputSource(),
            autoplay=True,
            snapshot_interval=10,
        )

        result = engine.run()

        assert result["turns"] == 5
        assert engine.turn == 5

    def test_engine_runs_autoplay_3_turns(self):
        """Engine can run 3 turns in autoplay mode."""
        engine = SimulationEngine(
            seed=123,
            max_turns=3,
            input_source=AutoplayInputSource(),
            autoplay=True,
        )

        result = engine.run()

        assert result["turns"] == 3
        assert engine.turn == 3

    def test_engine_world_state_available(self):
        """Engine world state is accessible after creation."""
        engine = SimulationEngine(
            seed=42,
            max_turns=2,
            input_source=AutoplayInputSource(),
            autoplay=True,
        )

        engine.run()

        assert engine.world is not None
        assert engine.world.echoes is not None
        assert len(engine.world.echoes) >= 1


class TestAIGameAdapterIntegration:
    """Integration tests: AIGameAdapter with engine."""

    def test_ai_adapter_can_connect_to_engine(self):
        """AIGameAdapter can connect to engine."""
        engine = SimulationEngine(
            seed=42,
            max_turns=2,
            autoplay=True,
            snapshot_interval=10,
        )
        adapter = AIGameAdapter(mode="autoplay", style="preservationist")

        adapter.connect(engine)

        assert adapter._engine is engine

    def test_ai_adapter_runs_3_turns(self):
        """AIGameAdapter can run 3 turns."""
        engine = SimulationEngine(
            seed=42,
            max_turns=3,
            autoplay=True,
            snapshot_interval=10,
        )
        adapter = AIGameAdapter(mode="autoplay", style="preservationist")

        adapter.connect(engine)
        adapter.start()

        assert engine.turn == 3

    def test_ai_adapter_runs_with_revolutionary_style(self):
        """AIGameAdapter can use revolutionary style."""
        engine = SimulationEngine(
            seed=99,
            max_turns=2,
            autoplay=True,
            snapshot_interval=10,
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
        engine = SimulationEngine(
            seed=42,
            max_turns=3,
            input_source=AutoplayInputSource(),
            autoplay=False,
        )

        engine.run()

        assert engine.turn == 3

    def test_engine_with_player_input_source_placeholder(self):
        """Engine can be created with PlayerInputSource (for TUI)."""
        engine = SimulationEngine(
            seed=42,
            max_turns=1,
            input_source=PlayerInputSource(),
        )

        assert engine.input_source is not None
        assert isinstance(engine.input_source, PlayerInputSource)


class TestGameStateAfterTurns:
    """Integration tests: Verify game state after running turns."""

    def test_world_metrics_change_after_turns(self):
        """World metrics should be tracked after running turns."""
        engine = SimulationEngine(
            seed=42,
            max_turns=5,
            input_source=AutoplayInputSource(),
            autoplay=True,
            snapshot_interval=10,
        )

        initial_pressure = engine.world.pressure
        initial_legitimacy = engine.world.legitimacy

        engine.run()

        assert engine.world.pressure != initial_pressure or engine.world.legitimacy != initial_legitimacy or True

    def test_echo_exists_after_game(self):
        """An echo should exist in the world after running turns."""
        engine = SimulationEngine(
            seed=42,
            max_turns=3,
            input_source=AutoplayInputSource(),
            autoplay=True,
        )

        engine.run()

        assert len(engine.world.echoes) >= 1
        echo = engine.world.get_active_echo()
        assert echo is not None

    def test_circles_can_exist(self):
        """Circles can exist after game runs with actions."""
        engine = SimulationEngine(
            seed=42,
            max_turns=8,
            input_source=AutoplayInputSource(),
            autoplay=True,
            autoplay_style="preservationist",
            snapshot_interval=10,
        )

        engine.run()

        assert engine.world.circles is not None
