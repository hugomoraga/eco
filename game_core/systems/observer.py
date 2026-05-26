"""
Simulation Observer Interface — decoupled display/input from engine core.

The SimulationEngine notifies observers on significant events.
Observers are free to render, log, or forward events as they wish.
The engine knows nothing about how events are displayed.
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.actions.base import ActionResult
    from game_core.domain.entities import World


class SimulationObserver(ABC):
    """
    Observer interface for simulation events.

    All methods are optional — observers implement only what they need.
    The engine calls these at specific points; observers can not affect
    the simulation by returning values (read-only pattern).
    """

    def on_world_start(self, world: World) -> None:
        """Called once at simulation start, before turn 1."""

    def on_turn_start(self, turn: int, world: World) -> None:
        """Called at the start of each turn, before any action is taken."""

    def on_turn_end(self, turn: int, world: World, action_taken: str | None) -> None:
        """Called at the end of each turn, after all effects are applied."""

    def on_action_selected(self, turn: int, action_name: str | None) -> None:
        """Called when an action is selected (player or autoplay)."""

    def on_action_result(self, turn: int, action_name: str, result: ActionResult) -> None:
        """Called after an action is executed with its result."""

    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float) -> None:
        """Called when a metric changes significantly."""

    def on_event(self, turn: int, event_type: str, title: str, summary: str) -> None:
        """Called when an event is generated (crisis, opportunity, etc.)."""

    def on_circle_founded(self, turn: int, circle_name: str, members: int) -> None:
        """Called when a circle is founded."""

    def on_npc_created(self, turn: int, npc_name: str, npc_role: str) -> None:
        """Called when a new NPC is created."""

    def on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str) -> None:
        """Called when a new echo is spawned."""

    def on_world_state(self, turn: int, world: World) -> None:
        """Called with the full world state at end of turn (for snapshots)."""

    def on_crisis(self, turn: int, metric: str, value: float) -> None:
        """Called when a crisis threshold is crossed."""

    def on_circle_activity(self, turn: int, circle_name: str, activity: str) -> None:
        """Called when a circle performs an activity."""

    def on_reincarnation_complete(self, turn: int, new_host_name: str) -> None:
        """Called when echo reincarnation process completes."""


class NullObserver(SimulationObserver):
    """No-op observer — does nothing. Used as placeholder."""
