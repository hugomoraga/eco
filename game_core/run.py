from __future__ import annotations

import argparse

from game_core.config import get_config
from game_core.engine.simulation import SimulationEngine


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

    if lang != cfg.i18n_language:
        import os
        os.environ["ECO_LANG"] = lang

    engine = SimulationEngine(
        seed=seed,
        max_turns=max_turns,
        autoplay=autoplay,
        autoplay_mode=autoplay_mode,
        autoplay_style=autoplay_style,
        run_dir=run_dir,
        ai_adapter_type=ai_adapter_type,
    )
    result = engine.run()
    print(f"Simulation complete. Results: {result}")


if __name__ == "__main__":
    main()