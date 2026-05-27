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
        from core.application.processors.simulation_engine import SimulationEngine
        from adapters.ai import MockAdapter
        from adapters.tui.console import Console
        from adapters.tui.display import ConsoleDisplay

        engine = SimulationEngine(
            seed=config.seed,
            max_turns=config.max_turns,
            player=config.player,
            run_dir=str(config.run_dir) if config.run_dir else None,
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
