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

from game_core.systems.simulation import SimulationEngine
from game_core.utils.config import get_config
from ui_core.console import Console
from ui_core.display import ConsoleDisplay


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

    # ─── Input source (player_core) ──────────────────────────────────
    if headless:
        input_source = None
    else:
        from player_core.modes.autoplay import AutoplayInputSource
        input_source = AutoplayInputSource()

    # ─── Simulation engine ────────────────────────────────────────────
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

    # ─── Observer (ui_core) ──────────────────────────────────────────
    if not headless:
        console = Console.get()
        engine.register_observer(ConsoleDisplay(console))

    # ─── Run ──────────────────────────────────────────────────────────
    result = engine.run()
    print(f"Simulation complete. Results: {result}")


if __name__ == "__main__":
    main()
