"""
Simulation Observer Interface — decoupled display/input from engine core.

The SimulationEngine notifies observers on significant events.
Observers are free to render, log, or forward events as they wish.
The engine knows nothing about how events are displayed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import World, Echo, Circle, Faction
    from game_core.actions.base import ActionResult


class SimulationObserver(ABC):
    """
    Observer interface for simulation events.

    All methods are optional — observers implement only what they need.
    The engine calls these at specific points; observers can not affect
    the simulation by returning values (read-only pattern).
    """

    def on_turn_start(self, turn: int, world: World) -> None:
        """Called at the start of each turn, before any action is taken."""
        pass

    def on_turn_end(self, turn: int, world: World, action_taken: str | None) -> None:
        """Called at the end of each turn, after all effects are applied."""
        pass

    def on_action_selected(self, turn: int, action_name: str | None) -> None:
        """Called when an action is selected (player or autoplay)."""
        pass

    def on_action_result(self, turn: int, action_name: str, result: ActionResult) -> None:
        """Called after an action is executed with its result."""
        pass

    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float) -> None:
        """Called when a metric changes significantly."""
        pass

    def on_event(self, turn: int, event_type: str, title: str, summary: str) -> None:
        """Called when an event is generated (crisis, opportunity, etc.)."""
        pass

    def on_circle_founded(self, turn: int, circle_name: str, members: int) -> None:
        """Called when a circle is founded."""
        pass

    def on_npc_created(self, turn: int, npc_name: str, npc_role: str) -> None:
        """Called when a new NPC is created."""
        pass

    def on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str) -> None:
        """Called when a new echo is spawned."""
        pass

    def on_world_state(self, turn: int, world: World) -> None:
        """Called with the full world state at end of turn (for snapshots)."""
        pass

    def on_crisis(self, turn: int, metric: str, value: float) -> None:
        """Called when a crisis threshold is crossed."""
        pass

    def on_circle_activity(self, turn: int, circle_name: str, activity: str) -> None:
        """Called when a circle performs an activity."""
        pass


class NullObserver(SimulationObserver):
    """No-op observer — does nothing. Used as placeholder."""
    pass