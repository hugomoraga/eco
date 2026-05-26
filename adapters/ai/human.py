"""
adapter_core.human — HumanGameAdapter for human players via TUI.

NOTE: The current engine.run() owns the loop and is backward-compatible.
HumanGameAdapter provides the adapter interface for future use where
the adapter owns the loop via engine.turn_start()/turn_end()/execute_action().
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.systems.simulation import SimulationEngine

from adapters.ai.base import GameAdapter
from adapters.ai.input_source import PlayerInputSource


class HumanGameAdapter(GameAdapter):
    """
    Adapter for human players via TUI.

    Uses PlayerInputSource for human input.
    The actual game loop integration with engine.run() will be done in a later phase.
    """

    def __init__(self, selector=None):
        input_source = PlayerInputSource(timeout_seconds=60, selector=selector)
        super().__init__(input_source)
        self._selector = selector

    def connect(self, engine: SimulationEngine) -> None:
        """Connect this adapter to a simulation engine."""
        self._engine = engine

    def on_world_state(self, turn: int, world_state: dict) -> None:
        """Called when engine sends world state."""
        pass

    def on_event(self, event_type: str, data: dict) -> None:
        """Called when engine sends an event."""
        pass

    def on_action_result(self, turn: int, action: str, success: bool, message: str) -> None:
        """Called when player's action completes."""
        pass

    def start(self) -> None:
        """Start the game. Currently delegates to engine.run()."""
        if self._engine is None:
            raise RuntimeError("Adapter not connected to engine. Call connect() first.")
        self._engine.run()

    def stop(self) -> None:
        """Stop the game loop."""
        if self._engine:
            self._engine.stop()
