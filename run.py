"""
run.py — ECO entry point.

Single entry point that:
1. Reads config + args
2. Creates SimulationEngine
3. Registers observers (ui_core.display.ConsoleDisplay)
4. Runs the simulation loop
"""

from __future__ import annotations

import argparse
import os

from game_core.systems.simulation import SimulationEngine
from game_core.utils.config import get_config
from ui_core.console import Console
from ui_core.display import ConsoleDisplay


def main() -> None:
    parser = argparse.ArgumentParser(description="ECO - Memetic Simulation Engine")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--turns", type=int, help="Max turns")
    parser.add_argument("--autoplay", action="store_true", help="Enable autoplay mode (input + engine)")
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
    parser.add_argument("--civ", type=str,
                        choices=["default", "technocracy", "theocracy", "anarchist_utopia", "dark_ages"],
                        default="default", help="Civilization template to use")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--headless", action="store_true", help="No console output")
    parser.add_argument("--no-layout", action="store_true", help="Disable adaptive layout")
    args = parser.parse_args()

    cfg = get_config()

    seed = args.seed if args.seed is not None else cfg.simulation.seed
    max_turns = args.turns if args.turns is not None else cfg.simulation.max_turns
    autoplay_mode = args.autoplay_mode or cfg.autoplay.default_mode
    autoplay_style = args.autoplay_style or cfg.autoplay.default_style
    run_dir = args.run_dir or cfg.run_dir
    ai_adapter_type = args.ai_adapter or cfg.ai.adapter
    lang = args.lang or cfg.i18n_language
    verbose = args.verbose or cfg.verbose
    headless = args.headless
    no_layout = args.no_layout

    if lang != cfg.i18n_language:
        os.environ["ECO_LANG"] = lang

    # ─── Input mode & engine autoplay ──────────────────────────────────
    # --autoplay flag enables both input autoplay AND engine autoplay
    is_autoplay = args.autoplay

    if headless:
        input_source = None
    elif is_autoplay:
        from adapter_core.input_source.autoplay import AutoplayInputSource
        input_source = AutoplayInputSource()
    else:
        from adapter_core.input_source.player import PlayerInputSource
        input_source = PlayerInputSource(timeout_seconds=60)

    # ─── Simulation engine ────────────────────────────────────────────
    engine = SimulationEngine(
        seed=seed,
        max_turns=max_turns,
        autoplay=is_autoplay,
        autoplay_mode=autoplay_mode,
        autoplay_style=autoplay_style,
        run_dir=run_dir,
        ai_adapter_type=ai_adapter_type,
        verbose=verbose,
        input_source=input_source,
        civ_id=args.civ,
    )

    # ─── Observer (ui_core) ──────────────────────────────────────────
    if not headless:
        from game_core.ai import MockAdapter
        console = Console.get()
        ai_adapter = MockAdapter()
        if no_layout or not is_autoplay:
            display = ConsoleDisplay(console, ai_adapter=ai_adapter)
        else:
            from ui_core.layout import TerminalLayout
            layout = TerminalLayout()
            display = ConsoleDisplay(console, layout=layout, ai_adapter=ai_adapter)
        display._game_mode = "autoplay" if is_autoplay else "player"
        engine.register_observer(display)

    # ─── Run ──────────────────────────────────────────────────────────
    result = engine.run()
    print(f"Simulation complete. Results: {result}")


if __name__ == "__main__":
    main()
