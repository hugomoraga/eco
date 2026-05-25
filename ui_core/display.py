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
        self._selected_civ_id: str = "default"

    # ─── SimulationObserver implementation ─────────────────────────────────

    def on_world_start(self, world: World) -> None:
        """Called once at simulation start, before turn 1."""
        from game_core.domain.entities import CivAlignment

        console = self.console
        console.print()
        console.rule("[bold cyan]WORLD INITIAL STATE[/bold cyan]", style="cyan")
        console.print()

        # ── 1. Civ ───────────────────────────────────────────────────────────
        selected_civ = None
        if hasattr(world, "civs") and world.civs:
            for c in world.civs:
                if c.meta_id == self._selected_civ_id:
                    selected_civ = c
                    break
            if selected_civ is None:
                selected_civ = world.civs[0]

        if selected_civ:
            console.print(f"[bold yellow]Civ:[/bold yellow] [cyan]{selected_civ.name}[/cyan]")
            console.print(f"  [dim]{selected_civ.description}[/dim]")
            console.print(f"  [dim]Dificultad: {selected_civ.difficulty} | "
                          f"Poblacion: {selected_civ.population:,}[/dim]")
            dom_essences = selected_civ.essence_profile.dominant_essences()
            console.print(f"  [dim]Esencias dominantes: {', '.join(dom_essences) if dom_essences else '-'}[/dim]")
            console.print()

        # ── 2. Host ──────────────────────────────────────────────────────────
        player_person = None
        player_host = None
        player_echo = None

        for p in world.persons:
            if p.type == "player":
                player_person = p
                break
        if player_person:
            player_host = world.get_host_for_person(player_person.id)
        if player_host:
            player_echo = world.get_echo(player_host.echo_id)

        console.print("[bold yellow]Host:[/bold yellow]")
        if player_person:
            console.print(f"  [green]Persona:[/green] {player_person.name}")
            if player_person.essence_profile:
                dom = player_person.essence_profile.dominant_essences()
                console.print(f"  [dim]  Esencias: {', '.join(dom) if dom else 'ninguna'}[/dim]")
            console.print(f"  [dim]  Lealtad: {player_person.loyalty:.0f} | "
                          f"Influencia: {player_person.influence:.0f}[/dim]")
        if player_echo:
            console.print(f"  [green]Echo:[/green] {player_echo.name}")
            console.print(f"  [dim]  Fase: {player_echo.phase.value} | "
                          f"Claridad: {player_echo.clarity:.0f}[/dim]")
            dom_e = player_echo.dominant_essences
            console.print(f"  [dim]  Esencias: {', '.join(dom_e) if dom_e else '-'}[/dim]")
        console.print()

        # ── 3. Persons destacadas (top 10 por influence) ───────────────────
        console.print("[bold yellow]Persons Destacadas:[/bold yellow]")
        npc_persons = [p for p in world.persons if p.type == "npc"]
        sorted_persons = sorted(npc_persons, key=lambda x: x.influence, reverse=True)[:10]

        if sorted_persons:
            console.print(f"  [dim]{'Nombre':<18} {'Tipo':<12} {'Lealtad':<8} {'Influ.':<7} Esencias[/dim]")
            console.print(f"  [dim]{'-'*65}[/dim]")
            for p in sorted_persons:
                dom = p.essence_profile.dominant_essences() if p.essence_profile else []
                essences_str = ",".join(dom[:2]) if dom else "-"
                alignment = ""
                if selected_civ and selected_civ.id == p.civ_id:
                    status = selected_civ.alignment_status(p.essence_profile)
                    color = {"aligned": "green", "neutral": "yellow", "disident": "red"}.get(status.value, "dim")
                    alignment = f"[{color}]{status.value[:4]}[/{color}]"
                console.print(
                    f"  [cyan]{p.name:<18}[/cyan] "
                    f"[magenta]{p.archetype:<12}[/magenta] "
                    f"[yellow]{p.loyalty:<8.0f}[/yellow] "
                    f"[green]{p.influence:<7.0f}[/green] "
                    f"[dim]{essences_str}[/dim] {alignment}"
                )
        else:
            console.print("  [dim]Ninguna persona NPC en el mundo aun.[/dim]")
        console.print()

        # ── 4. Turn System ─────────────────────────────────────────────────
        console.print("[bold yellow]Sistema de Turns:[/bold yellow]")
        console.print("  [dim]- Cada turn = 1 accion del Echo (o del autoplayer)[/dim]")
        console.print("  [dim]- 10 turns = 1 World Tick (cambio historico menor)[/dim]")
        console.print("  [dim]- 100 World Ticks = 1 Historical Tick (era)[/dim]")
        console.print()

        console.rule(style="cyan")

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