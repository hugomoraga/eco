"""
test_defensive_error_handling.py — Tests for SPEC-55 defensive error handling.

Verifies that critical methods log exceptions before propagating.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestEngineNeverDiesSilently:
    """Tests that engine methods fail loudly with proper logging."""

    def test_execute_turn_logs_exception(self):
        """execute_turn failure should be logged with error_type."""
        from core.application.processors.simulation_engine import SimulationEngine

        engine = SimulationEngine(seed=42, max_turns=1)
        engine.world = MagicMock()

        with patch.object(engine, "_execute_turn", side_effect=RuntimeError("turn failed")):
            with patch.object(engine._log, "error") as mock_log:
                with pytest.raises(RuntimeError):
                    engine.run()

                mock_log.assert_called()
                call_args = mock_log.call_args
                assert "execute_turn_failed" in str(call_args)
                assert call_args.kwargs.get("error_type") == "RuntimeError"

    def test_get_player_action_logs_exception(self):
        """_get_player_action failure should be logged."""
        from core.application.processors.simulation_engine import SimulationEngine
        from core.domain.entities.echo import Echo

        engine = SimulationEngine(seed=42, max_turns=1)
        echo = MagicMock(spec=Echo)

        with patch.object(engine._player, "select_action", side_effect=ValueError("bad input")):
            with patch.object(engine._log, "error") as mock_log:
                with pytest.raises(ValueError):
                    engine._get_player_action(echo)

                mock_log.assert_called()
                call_args = mock_log.call_args
                assert "get_player_action_failed" in str(call_args)
                assert call_args.kwargs.get("error_type") == "ValueError"

    def test_execute_player_action_logs_exception(self):
        """_execute_player_action failure should be logged."""
        from core.application.processors.action_registry import ACTION_CLASSES
        from core.application.processors.simulation_engine import SimulationEngine
        from core.domain.entities.echo import Echo

        engine = SimulationEngine(seed=42, max_turns=1)
        echo = MagicMock(spec=Echo)

        fake_action = MagicMock()
        fake_action.can_execute.return_value = True
        fake_action.execute.side_effect = TypeError("wrong type")

        with patch.dict(ACTION_CLASSES, {"fake_action": lambda: fake_action}):
            with patch.object(engine._log, "error") as mock_log:
                with pytest.raises(TypeError):
                    engine._execute_player_action(echo, "fake_action", lambda x: False)

                mock_log.assert_called()
                call_args = mock_log.call_args
                assert "execute_player_action_failed" in str(call_args)
                assert call_args.kwargs.get("error_type") == "TypeError"


class TestProcessorsNeverDieSilently:
    """Tests that processor functions log exceptions."""

    def test_process_npc_turns_logs_exception(self):
        """process_npc_turns failure should be logged."""
        from core.application.processors.npc_processor import process_npc_turns

        mock_world = MagicMock()
        mock_world.persons = [MagicMock(type="npc")]
        mock_world.clock.world_tick = 1

        mock_executor = MagicMock()
        mock_ai = MagicMock()
        mock_notify = MagicMock()
        mock_log = MagicMock()
        mock_log_event = MagicMock()

        with patch(
            "adapters.autoplayer.npc_engine.NPCEngine", side_effect=RuntimeError("engine error")
        ):
            with pytest.raises(RuntimeError):
                process_npc_turns(
                    mock_world, 42, 1, mock_executor, mock_ai, mock_notify, mock_log, mock_log_event
                )

            mock_log.error.assert_called()
            call_args = mock_log.error.call_args
            assert "process_npc_turns_failed" in str(call_args)

    def test_process_circle_activities_logs_exception(self):
        """process_circle_activities failure should be logged."""
        from core.application.processors.circle_processor import process_circle_activities

        mock_world = MagicMock()
        mock_world.circles = [MagicMock()]
        mock_world.circles[0].member_count = 0

        mock_rng = MagicMock()
        mock_ai = MagicMock()
        mock_notify = MagicMock()
        mock_log = MagicMock()
        mock_log_event = MagicMock()

        with patch("core.factories.process_circle_tick", side_effect=RuntimeError("tick error")):
            with pytest.raises(RuntimeError):
                process_circle_activities(
                    mock_world, mock_rng, 42, 1, mock_ai, mock_notify, mock_log, mock_log_event
                )

            mock_log.error.assert_called()
            call_args = mock_log.error.call_args
            assert "process_circle_activities_failed" in str(call_args)
