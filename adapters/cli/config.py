"""
config.py — Game configuration from args + config file.

Handles the pattern: CLI args override config file values.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from core.ports.player import Player
from adapters.config.config import get_config


@dataclass
class GameConfig:
    """All game settings in one place."""
    seed: int
    max_turns: int
    player: Player | None
    ai_adapter_type: str
    run_dir: Path
    civ_id: str
    verbose: bool
    headless: bool
    no_layout: bool
    autoplay: bool
    autoplay_mode: str
    autoplay_style: str
    display_mode: Literal["console", "layout", "tui"]

    @classmethod
    def from_args(cls, args) -> "GameConfig":
        """Build config by overriding config file values with CLI args."""
        cfg = get_config()

        seed = args.seed if args.seed is not None else cfg.simulation.seed
        max_turns = args.turns if args.turns is not None else cfg.simulation.max_turns
        run_dir = Path(args.run_dir) if args.run_dir else (Path(cfg.run_dir) if cfg.run_dir else None)
        ai_adapter_type = args.ai_adapter or cfg.ai.adapter
        civ_id = args.civ
        verbose = args.verbose or cfg.verbose
        headless = args.headless
        no_layout = args.no_layout
        autoplay = args.autoplay
        autoplay_mode = args.autoplay_mode or cfg.autoplay.default_mode
        autoplay_style = args.autoplay_style or cfg.autoplay.default_style
        display_mode = "tui" if args.tui else ("layout" if autoplay and not no_layout else "console")

        from core.application.players.human import HumanPlayer
        from core.application.players.auto import AutoPlayer

        if headless:
            player = None
        elif args.tui:
            player = HumanPlayer()
        elif autoplay:
            player = AutoPlayer(seed=seed, mode=autoplay_mode, style_id=autoplay_style)
        else:
            player = HumanPlayer()

        return cls(
            seed=seed,
            max_turns=max_turns,
            player=player,
            ai_adapter_type=ai_adapter_type,
            run_dir=run_dir,
            civ_id=civ_id,
            verbose=verbose,
            headless=headless,
            no_layout=no_layout,
            autoplay=autoplay,
            autoplay_mode=autoplay_mode,
            autoplay_style=autoplay_style,
            display_mode=display_mode,
        )
