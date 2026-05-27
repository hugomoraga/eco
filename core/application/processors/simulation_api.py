"""
simulation_api.py — Adapter-friendly API for SimulationEngine.
Provides turn-based interface for external controllers (TUI, autoplayer).
"""

from __future__ import annotations

from core.application.actions.base import ActionContext
from core.application.processors.action_registry import ACTION_CLASSES, get_action
from core.application.processors.turn_context import handle_npc_damage_to_player, track_echo_action


class SimulationAPI:
    """
    Turn-based API for controlling simulation from external adapters.
    """

    def __init__(self, engine):
        self._engine = engine

    def turn_start(self) -> dict:
        """Begin a turn. Returns world state for adapters."""
        self._engine.turn += 1
        self._engine.world.clock.advance(1)
        self._engine._notify("on_turn_start", self._engine.turn, self._engine.world)
        return self._engine._serialize_world()

    def turn_end(self, action_name: str | None = None) -> None:
        """End current turn. Evolves metrics and notifies observers."""
        self._engine.world.evolve_metrics(self._engine.rng)
        new_metrics = self._snapshot_metrics()
        for metric, new_val in new_metrics.items():
            old_val = getattr(self._engine, '_last_metrics', {}).get(metric, new_val)
            if abs(new_val - old_val) >= 0.5:
                self._engine._notify("on_metric_changed", self._engine.turn, metric, old_val, new_val)
        self._engine._last_metrics = new_metrics
        self._engine._notify("on_turn_end", self._engine.turn, self._engine.world, action_name)
        self._engine._log_event("tick", {
            "turn": self._engine.turn,
            "world_tick": self._engine.world.clock.world_tick,
            "action": action_name,
        })

    def execute_action(self, turn: int, action_name: str):
        """Execute an action. Called by adapter after getting action from InputSource."""
        from core.application.processors.damage import should_deal_damage_to_player

        if action_name not in ACTION_CLASSES:
            return None

        echo = self._engine.world.get_active_echo()
        action = ACTION_CLASSES[action_name]()
        context = ActionContext(
            world_tick=self._engine.world.clock.world_tick,
            action_tick=self._engine.world.clock.action_tick,
            autoplay=False,
        )

        result = None
        if action.can_execute(echo, self._engine.world, context):
            result = action.execute(echo, self._engine.world, context)
            self._engine._log.info("action_executed", turn=turn, action=action_name, success=result.success, message=result.message)
            self._engine._notify("on_action_result", turn, action_name, result)

            track_echo_action(echo, action_name, turn)

            if should_deal_damage_to_player(action_name) and result and result.success:
                try:
                    handle_npc_damage_to_player(action_name, self._engine.world, self._engine._notify, turn)
                except Exception as e:
                    self._engine._log.error("npc_damage", turn=turn, action=action_name, stage="error", error=str(e))

        return result

    def get_world_state(self) -> dict:
        """Return current world state for adapters."""
        return self._engine._serialize_world()

    def is_running(self) -> bool:
        """Check if simulation is active."""
        return self._engine._running and self._engine.turn < self._engine.max_turns

    def stop(self) -> None:
        """Signal simulation to stop."""
        self._engine._running = False

    def _snapshot_metrics(self) -> dict:
        from core.application.processors.turn_context import snapshot_metrics
        return snapshot_metrics(self._engine.world)
