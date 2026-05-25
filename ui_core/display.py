"""
ConsoleDisplay — SimulationObserver implementation for ui_core.

Registers with SimulationEngine to render events to console.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.actions.base import ActionResult
    from game_core.domain.entities import World

from ui_core.components import Components
from ui_core.console import Console


class ConsoleDisplay:
    """
    Observer that renders simulation events to the console.

    Implements SimulationObserver interface from game_core.systems.observer.
    Registered with SimulationEngine via engine.register_observer().
    """

    def __init__(self, console: Console | None = None):
        self.console = console or Console.get()
        self._last_metrics: dict[str, float] = {}

    # ─── SimulationObserver implementation ─────────────────────────────────

    def on_turn_start(self, turn: int, world: World) -> None:
        """Called at the start of each turn, before any action is taken."""
        self.console.print()
        self.console.print(Components.turn_header(turn), justify="center")

        metrics = self._extract_metrics(world)
        self.console.print(Components.world_metrics_table(metrics))
        self._last_metrics = metrics

    def on_turn_end(self, turn: int, world: World, action_taken: str | None) -> None:
        """Called at the end of each turn, after all effects are applied."""
        self.console.print()
        self.console.print(Components.status_line(
            turn=turn,
            world_tick=world.clock.world_tick if world else 0,
            echoes=len(world.echoes) if world else 0,
            circles=len(world.circles) if world else 0,
            factions=len(world.factions) if world else 0,
            influence=int(self._total_influence(world)),
            persons=len(world.persons) if world else 0,
        ))

        # Show delta if metrics changed
        new_metrics = self._extract_metrics(world)
        if new_metrics != self._last_metrics:
            self.console.print(Components.metrics_delta_table(self._last_metrics, new_metrics))
            self._last_metrics = new_metrics

    def on_action_selected(self, turn: int, action_name: str | None) -> None:
        """Called when an action is selected (player or autoplay)."""
        if action_name:
            self.console.print(f"[cyan]>>>[/cyan] [bold]{action_name}[/bold] selected")
        else:
            self.console.print("[dim]>>> autoplay decision[/dim]")

    def on_action_result(self, turn: int, action_name: str, result: ActionResult) -> None:
        """Called after an action is executed with its result."""
        success = getattr(result, "success", True)
        message = getattr(result, "message", "")
        state_delta = getattr(result, "state_delta", None)

        self.console.print()
        self.console.print(Components.action_result(action_name, message, success))

        if state_delta and isinstance(state_delta, dict):
            for key, value in state_delta.items():
                self.console.print(Components.action_detail(key, value))

    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float) -> None:
        """Called when a metric changes significantly."""
        delta = new_val - old_val
        if abs(delta) < 0.5:
            return
        sign = "+" if delta >= 0 else ""
        color = "green" if delta >= 0 else "red"
        self.console.print(
            f"  [cyan]{metric}:[/cyan] {old_val:.1f} -> {new_val:.1f} "
            f"([{color}]{sign}{delta:.1f}[/{color}])"
        )

    def on_event(self, turn: int, event_type: str, title: str, summary: str) -> None:
        """Called when an event is generated (crisis, opportunity, etc.)."""
        self.console.print()
        self.console.print(Components.event_banner(event_type, title, summary))

    def on_circle_founded(self, turn: int, circle_name: str, members: int) -> None:
        """Called when a circle is founded."""
        self.console.print(f"[yellow]⭕[/yellow] Circle founded: {circle_name} ({members} members)")

    def on_npc_created(self, turn: int, npc_name: str, npc_role: str) -> None:
        """Called when a new NPC is created."""
        self.console.print(f"[magenta]@[/magenta] NPC created: {npc_name} ({npc_role})")

    def on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str) -> None:
        """Called when a new echo is spawned."""
        self.console.print(f"[green]🌱[/green] Echo spawned: {daughter_name} (from {parent_name})")

    def on_crisis(self, turn: int, metric: str, value: float) -> None:
        """Called when a crisis threshold is crossed."""
        self.console.print()
        self.console.print(f"[red]⚠ CRISIS:[/red] {metric} = {value:.2f}")

    def on_circle_activity(self, turn: int, circle_name: str, activity: str) -> None:
        """Called when a circle performs an activity."""
        self.console.print(f"[yellow]▸[/yellow] {circle_name}: {activity}")

    def on_world_state(self, turn: int, world: World) -> None:
        """Called with the full world state at end of turn (for snapshots)."""
        # Snapshot handling is done by SimulationEngine directly

    # ─── Helpers ──────────────────────────────────────────────────────────

    def _total_influence(self, world: World) -> float:
        """Compute total influence from factions + circles."""
        if world is None:
            return 0.0
        faction_inf = sum(f.influence for f in world.factions)
        circle_inf = sum(c.influence for c in world.circles)
        return faction_inf + circle_inf

    def _extract_metrics(self, world: World) -> dict[str, float]:
        """
        Extract ALL metrics from world for display.

        Maps to actual World structure:
        - Civilization metrics: stability, pressure, legitimacy, resources_global, population
        - Resource dict: food, infrastructure, energy, knowledge, legitimacy
        - Entity counts: echoes, circles, factions, persons, hosts
        - Influence: computed from factions + circles
        """
        if world is None:
            return {}

        # Base civilization metrics
        metrics = {
            "Stability": world.stability,
            "Civil Unrest": world.pressure,
            "Authority": world.legitimacy,
            "Resources (G)": world.resources_global,
        }

        # Resource dict — food, infrastructure, energy, knowledge, legitimacy
        if hasattr(world, "resources") and isinstance(world.resources, dict):
            for key, value in world.resources.items():
                metrics[f"  {key.capitalize()}"] = float(value)

        # Population
        metrics["Population"] = float(world.population)

        # Entity counts
        metrics["Echoes"] = float(len(world.echoes))
        metrics["Circles"] = float(len(world.circles))
        metrics["Factions"] = float(len(world.factions))
        metrics["Persons"] = float(len(world.persons))
        metrics["Hosts"] = float(len(world.hosts))

        # Influence (computed, not stored)
        metrics["Influence (F+C)"] = self._total_influence(world)

        return metrics