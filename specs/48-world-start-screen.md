# SPEC-48: World Start Screen + Civ Display

**Estado:** draft
**Creador:** Hugo (ECO architect)
**Creado:** 2026-05-25
**Dependencias:** spec-43 (ui.md), spec-47 (essence-system-v2.md)
**Reemplaza:** parcial de spec-43

---

## Objetivo

Al ejecutar `run.py`, antes del loop de turnos, mostrar:
1. La Civ seleccionada (nombre, descripción, difficulty)
2. El host asignado (persona del jugador + echo encarnado)
3. Las persons destacadas (archetype persons del dataset, alineación)
4. Un header de sistema de turns

---

## Arquitectura

### Nuevo Observer: `on_world_start`

```python
# game_core/systems/observer.py
class SimulationObserver(ABC):
    # ... existing methods ...

    def on_world_start(self, world: World) -> None:
        """Called once at simulation start, before turn 1."""

# simulation.py _run() loop
def run(self) -> dict:
    self._notify("on_world_start", self.world)   # ← nuevo
    self._notify("on_turn_start", 1, self.world)
    # ... rest of loop
```

### ConsoleDisplay.on_world_start()

```python
def on_world_start(self, world: World) -> None:
    console = self.console
    console.print()
    console.rule("[bold cyan]WORLD INITIAL STATE[/bold cyan]", style="cyan")
    console.print()

    # ── 1. Civ ────────────────────────────────────────────────
    selected_civ = None
    if hasattr(world, "civs") and world.civs:
        for c in world.civs:
            if c.meta_id == (getattr(world, "_selected_civ_id", None) or "default"):
                selected_civ = c
                break
        if selected_civ is None:
            selected_civ = world.civs[0]

    if selected_civ:
        console.print(f"[bold yellow]Civ:[/bold yellow] [cyan]{selected_civ.name}[/cyan]")
        console.print(f"[dim]    {selected_civ.description}[/dim]")
        console.print(f"[dim]    Difficulty: {selected_civ.difficulty} | "
                      f"Population: {selected_civ.population:,}[/dim]")
        console.print()

    # ── 2. Host ───────────────────────────────────────────────
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
    if player_echo:
        console.print(f"  [green]Echo:[/green] {player_echo.name}")
        console.print(f"  [dim]  Fase: {player_echo.phase.value} | "
                      f"Claridad: {player_echo.clarity:.0f}[/dim]")
    console.print()

    # ── 3. Persons destacadas (top 10 por influence) ─────────
    console.print("[bold yellow]Persons Destacadas:[/bold yellow]")
    sorted_persons = sorted(
        [p for p in world.persons if p.type == "npc"],
        key=lambda x: x.influence,
        reverse=True
    )[:10]

    if sorted_persons:
        console.print(f"  [dim]{'Nombre':<20} {'Tipo':<12} {'Lealtad':<8} {'Influencia':<10} Esencias[/dim]")
        console.print(f"  [dim]{'-'*70}[/dim]")
        for p in sorted_persons:
            dom = p.essence_profile.dominant_essences() if p.essence_profile else []
            essences_str = ",".join(dom[:2]) if dom else "-"
            console.print(
                f"  [cyan]{p.name:<20}[/cyan] "
                f"[magenta]{p.archetype:<12}[/magenta] "
                f"[yellow]{p.loyalty:<8.0f}[/yellow] "
                f"[green]{p.influence:<10.0f}[/green] "
                f"[dim]{essences_str}[/dim]"
            )
    else:
        console.print("  [dim]Ninguna persona NPC en el mundo aún.[/dim]")
    console.print()

    # ── 4. Turn System ────────────────────────────────────────
    console.print("[bold yellow]Sistema de Turns:[/bold yellow]")
    console.print("  [dim]- Cada turn = 1 accion del Echo (o del autoplayer)[/dim]")
    console.print("  [dim]- 10 turns = 1 World Tick (cambio historico menor)[/dim]")
    console.print("  [dim]- 100 World Ticks = 1 Historical Tick (era)[/dim]")
    console.print()

    console.rule(style="cyan")
```

---

## Flujo Completo de Renderizado

```
run.py:
  engine = SimulationEngine(civ_id=args.civ, ...)
  engine.register_observer(ConsoleDisplay(console))
  engine.run()

SimulationEngine.run():
  1. _notify("on_world_start", world)
     → ConsoleDisplay.on_world_start()
        → Muestra: Civ | Host | Persons | Turn System

  2. for turn in range(1, max_turns+1):
       _notify("on_turn_start", turn, world)
       → ConsoleDisplay.on_turn_start()
          → Turn header + world_metrics_table

       input_source.get_action(turn, world)
       execute action
       _notify("on_action_result", ...)
       events.evaluate(world)
       _notify("on_event", ...)
       _notify("on_turn_end", ...)
       → ConsoleDisplay.on_turn_end()
          → status_line + metrics_delta_table
```

---

## Tasks

- [ ] Añadir `on_world_start(self, world)` a `SimulationObserver` en `observer.py`
- [ ] Implementar `ConsoleDisplay.on_world_start()` en `ui_core/display.py`
- [ ] Añadir `Components.world_start_screen()` (óptimo, para reutilización)
- [ ] Llamar `_notify("on_world_start", world)` en `SimulationEngine.run()` antes del loop
- [ ] Actualizar spec-43 para incluir este flujo

---

## Status History

- 2026-05-25: draft creado