"""
adapter_core.ai — AIGameAdapter for AI/autoplay controlled players.

Uses AutoplayerEngine internally for action selection when in autoplay mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.systems.simulation import SimulationEngine

from adapters.ai.base import GameAdapter
from adapters.ai.input_source import AutoplayInputSource
from adapters.autoplayer import AutoplayerEngine
from core.shared import AutoplayMode, ALL_AVAILABLE_ACTIONS


class AIGameAdapter(GameAdapter):
    """
    Adapter for AI-controlled players.

    Uses AutoplayerEngine internally for action selection.
    Can be configured with different autoplay modes and styles.
    """

    def __init__(
        self,
        mode: str = "autoplay",
        style: str = "preservationist",
        seed: int = 42,
    ):
        super().__init__(AutoplayInputSource())
        self._autoplay_engine = AutoplayerEngine(
            seed=seed,
            mode=AutoplayMode(mode) if mode in [m.value for m in AutoplayMode] else AutoplayMode.AUTOPLAY,
            style_id=style,
        )
        self._available_actions = ALL_AVAILABLE_ACTIONS

    def connect(self, engine: SimulationEngine) -> None:
        """Connect this adapter to a simulation engine."""
        self._engine = engine
        self._autoplay_engine.rng = engine.rng

    def on_world_state(self, turn: int, world_state: dict) -> None:
        """Called when engine sends world state."""
        pass

    def on_event(self, event_type: str, data: dict) -> None:
        """Called when engine sends an event."""
        pass

    def on_action_result(self, turn: int, action: str, success: bool, message: str) -> None:
        """Called when player's action completes."""
        pass

    def get_action(self, turn: int) -> str | None:
        """Get AI decision for this turn."""
        if self._engine is None:
            return None

        echo = self._engine.world.get_active_echo()
        if echo is None:
            return None

        decision = self._autoplay_engine.select_action(
            echo, self._engine.world, self._available_actions
        )
        return decision.selected_action if decision else None

    def start(self) -> None:
        """Start the game. Delegates to engine.run()."""
        if self._engine is None:
            raise RuntimeError("Adapter not connected to engine. Call connect() first.")
        self._engine.run()

    def stop(self) -> None:
        """Stop the game loop."""
        if self._engine:
            self._engine.stop()
