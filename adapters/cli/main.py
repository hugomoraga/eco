"""
main.py — ECO entry point.

Single entry point that:
1. Parses CLI args
2. Resolves config (args override config file)
3. Launches in appropriate mode (TUI or CLI)
"""

from __future__ import annotations

import argparse
import os

from adapters.cli.config import GameConfig
from adapters.cli.launcher import Launcher


def create_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="ECO - Memetic Simulation Engine")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--turns", type=int, help="Max turns")
    parser.add_argument(
        "--autoplay",
        action="store_true",
        help="Use AutoPlayer (automatic decisions). Default: HumanPlayer",
    )
    parser.add_argument(
        "--autoplay-mode",
        type=str,
        choices=["manual", "suggest", "autoplay", "director", "replay"],
        help="Autoplay mode",
    )
    parser.add_argument(
        "--autoplay-style",
        type=str,
        choices=["preservationist", "revolutionary", "manipulator", "mystic", "technocrat"],
        help="Autoplayer style",
    )
    parser.add_argument("--run-dir", type=str, help="Run directory for logs")
    parser.add_argument(
        "--ai-adapter", type=str, choices=["mock", "openai", "minimax"], help="AI adapter to use"
    )
    parser.add_argument("--lang", type=str, choices=["es", "en"], help="Language")
    parser.add_argument(
        "--civ",
        type=str,
        choices=["default", "technocracy", "theocracy", "anarchist_utopia", "dark_ages"],
        default="default",
        help="Civilization template to use",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--headless", action="store_true", help="No console output")
    parser.add_argument("--no-layout", action="store_true", help="Disable adaptive layout")
    parser.add_argument("--tui", action="store_true", help="Use Textual TUI")
    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.lang:
        os.environ["ECO_LANG"] = args.lang

    config = GameConfig.from_args(args)
    launcher = Launcher()
    launcher.launch(config)


if __name__ == "__main__":
    main()
