from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from game_core.utils.config import get_config
from game_core.systems.simulation import SimulationEngine
from game_core.systems.observer import SimulationObserver

if TYPE_CHECKING:
    from game_core.domain.entities import World
    from game_core.actions.base import ActionResult


def main() -> None:
    parser = argparse.ArgumentParser(description="ECO - Memetic Simulation Engine")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--turns", type=int, help="Max turns")
    parser.add_argument("--autoplay", action="store_true", help="Enable autoplay mode")
    parser.add_argument("--autoplay-mode", type=str,
                        choices=["manual", "suggest", "autoplay", "director", "replay"],
                        help="Autoplay mode")
    parser.add_argument("--autoplay-style", type=str,
                        choices=["preservationist", "revolutionary", "manipulator", "mystic", "technocrat"],
                        help="Autoplayer style")
    parser.add_argument("--run-dir", type=str, help="Run directory for logs")
    parser.add_argument("--ai-adapter", type=str,
                        choices=["mock", "openai", "minimax"],
                        help="AI adapter to use")
    parser.add_argument("--lang", type=str, choices=["es", "en"], help="Language")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--headless", action="store_true", help="No console output")
    args = parser.parse_args()

    cfg = get_config()

    seed = args.seed if args.seed is not None else cfg.simulation.seed
    max_turns = args.turns if args.turns is not None else cfg.simulation.max_turns
    autoplay = args.autoplay or cfg.simulation.autoplay
    autoplay_mode = args.autoplay_mode or cfg.autoplay.default_mode
    autoplay_style = args.autoplay_style or cfg.autoplay.default_style
    run_dir = args.run_dir or cfg.run_dir
    ai_adapter_type = args.ai_adapter or cfg.ai.adapter
    lang = args.lang or cfg.i18n_language
    verbose = args.verbose or cfg.verbose
    headless = args.headless

    if lang != cfg.i18n_language:
        import os
        os.environ["ECO_LANG"] = lang

    if headless:
        from game_core.systems.observer import NullObserver
        input_source = None
    else:
        from player_core.modes.autoplay import AutoplayInputSource
        input_source = AutoplayInputSource()

    engine = SimulationEngine(
        seed=seed,
        max_turns=max_turns,
        autoplay=autoplay,
        autoplay_mode=autoplay_mode,
        autoplay_style=autoplay_style,
        run_dir=run_dir,
        ai_adapter_type=ai_adapter_type,
        verbose=verbose,
        input_source=input_source,
    )

    if not headless:
        from ui_core.interface import Interface
        from ui_core.components import Components
        interface = Interface(engine.world, {})
        engine.register_observer(_ConsoleDisplay(interface, Components))

    result = engine.run()
    print(f"Simulation complete. Results: {result}")


class _ConsoleDisplay(SimulationObserver):
    def __init__(self, interface, components):
        self.interface = interface
        self.Components = components

    def on_turn_start(self, turn: int, world: "World") -> None:
        self.interface.console.print()
        self.interface.console.print(self.Components.turn_header(turn), justify="center")

    def on_turn_end(self, turn: int, world: "World", action_taken: str | None) -> None:
        self.interface.print_status_line(turn, world)

    def on_action_selected(self, turn: int, action_name: str | None) -> None:
        if action_name:
            self.interface.console.print(f"[cyan]>>>[/cyan] [bold]{action_name}[/bold] selected")

    def on_action_result(self, turn: int, action_name: str, result: "ActionResult") -> None:
        if result.success:
            self.interface.print_action_result(turn, action_name, result.message, getattr(result, 'state_delta', None))
        elif result.message:
            self.interface.print_action_result(turn, action_name, f"FAIL: {result.message}", None)

    def on_event(self, turn: int, event_type: str, title: str, summary: str) -> None:
        self.interface.show_event(event_type, title, summary)

    def on_crisis(self, turn: int, metric: str, value: float) -> None:
        self.interface.console.print(f"[red]CRISIS:[/red] {metric} = {value:.2f}")

    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float) -> None:
        delta = new_val - old_val
        if abs(delta) < 0.5:
            return
        sign = "+" if delta >= 0 else ""
        color = "green" if delta >= 0 else "red"
        self.interface.console.print(f"  [cyan]{metric}:[/cyan] {old_val:.1f} -> {new_val:.1f} ([{color}]{sign}{delta:.1f}[/{color}])")

    def on_circle_founded(self, turn: int, circle_name: str, members: int) -> None:
        self.interface.console.print(f"[yellow]O[/yellow] Circle founded: {circle_name} ({members} members)")

    def on_npc_created(self, turn: int, npc_name: str, npc_role: str) -> None:
        self.interface.console.print(f"[magenta]@[/magenta] NPC created: {npc_name} ({npc_role})")


if __name__ == "__main__":
    main()