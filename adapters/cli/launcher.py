"""
launcher.py — Launch the game in different modes (TUI, CLI, headless).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapters.cli.config import GameConfig


class Launcher:
    """Launches the game in different modes."""

    def launch_tui(self, config: "GameConfig") -> None:
        """Launch Textual TUI mode."""
        from adapters.tui.textual.app import EcoTextualApp

        EcoTextualApp(
            max_turns=config.max_turns,
            seed=config.seed,
        ).run()

    def launch_cli(self, config: "GameConfig") -> None:
        """Launch CLI mode with console display."""
        from datetime import datetime
        from pathlib import Path

        from infra.logging import init_logger
        from core.application.processors.simulation_engine import SimulationEngine
        from infra.ai import MockAdapter
        from adapters.tui.console import Console
        from adapters.tui.display import ConsoleDisplay

        if config.run_dir is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_root = Path(__file__).parent.parent.parent
            while project_root != project_root.parent and not (project_root / "pyproject.toml").exists():
                project_root = project_root.parent
            run_dir = project_root / "runs" / f"run_{run_id}"
            run_dir.mkdir(parents=True, exist_ok=True)
        else:
            run_dir = Path(config.run_dir)

        init_logger(run_dir)

        engine = SimulationEngine(
            seed=config.seed,
            max_turns=config.max_turns,
            player=config.player,
            run_dir=str(run_dir),
            ai_adapter_type=config.ai_adapter_type,
            verbose=config.verbose,
            civ_id=config.civ_id,
        )

        if not config.headless:
            console = Console.get()
            ai_adapter = MockAdapter()

            if config.display_mode == "layout":
                from adapters.tui.layout import TerminalLayout
                layout = TerminalLayout()
                display = ConsoleDisplay(console, layout=layout, ai_adapter=ai_adapter)
            else:
                display = ConsoleDisplay(console, ai_adapter=ai_adapter)

            display._game_mode = "autoplay" if config.autoplay else "player"
            engine.register_observer(display)

        result = engine.run()
        print(f"Simulation complete. Results: {result}")

    def launch(self, config: "GameConfig") -> None:
        """Launch in the appropriate mode based on config."""
        if config.display_mode == "tui":
            self.launch_tui(config)
        else:
            self.launch_cli(config)
