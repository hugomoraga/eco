"""
Run: python -m adapters.tui.textual
"""

from adapters.tui.textual.app import EcoTextualApp
from adapters.tui.textual.theme import THEMES
import argparse

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="ECO Textual UI")
    p.add_argument("--max-turns", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--theme", default="galaxy", choices=list(THEMES.keys()))
    args = p.parse_args()

    cli = [__import__("sys").executable, "-m", "core.cli",
           "--max-turns", str(args.max_turns), "--seed", str(args.seed)]

    EcoTextualApp(cli_args=cli, theme_name=args.theme).run()