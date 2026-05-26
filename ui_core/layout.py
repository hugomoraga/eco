from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Any

from rich.console import Console as RichConsole
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text

from .styles import s, CYAN, YELLOW, GREEN


TURNS_PER_WORLD_TICK = 10


@dataclass
class LayoutConfig:
    min_terminal_width: int = 100
    min_terminal_height: int = 30


@dataclass
class EchoInfo:
    name: str = "Unknown"
    phase: str = "unknown"
    clarity: float = 0.0
    essences: list[str] = field(default_factory=list)
    action_history: list[str] = field(default_factory=list)


@dataclass
class WorldInfo:
    civ_name: str = "Unknown"
    stability: float = 50.0
    pressure: float = 30.0
    legitimacy: float = 60.0
    population: int = 0
    echoes: int = 0
    circles: int = 0
    factions: int = 0


class TerminalLayout:
    def __init__(
        self,
        config: LayoutConfig | None = None,
    ):
        self.config = config or LayoutConfig()
        self._turn: int = 0
        self._world_tick: int = 0
        self._echo_info = EchoInfo()
        self._world_info = WorldInfo()
        self._metrics_table: Table | None = None
        self._log_lines: list[str] = []
        self._live: Live | None = None
        self._console: RichConsole | None = None
        self._available_actions: list[str] = []
        self._game_mode: str = "player"

    def set_echo_info(self, name: str, phase: str, clarity: float, essences: list[str]) -> None:
        self._echo_info.name = name
        self._echo_info.phase = phase
        self._echo_info.clarity = clarity
        self._echo_info.essences = essences

    def set_world_info(
        self,
        civ_name: str,
        stability: float,
        pressure: float,
        legitimacy: float,
        population: int,
        echoes: int,
        circles: int,
        factions: int,
    ) -> None:
        self._world_info.civ_name = civ_name
        self._world_info.stability = stability
        self._world_info.pressure = pressure
        self._world_info.legitimacy = legitimacy
        self._world_info.population = population
        self._world_info.echoes = echoes
        self._world_info.circles = circles
        self._world_info.factions = factions

    def set_available_actions(self, actions: list[str]) -> None:
        self._available_actions = actions
        if self._live:
            self._live.update(self._build_layout())

    def set_game_mode(self, mode: str) -> None:
        self._game_mode = mode
        if self._live:
            self._live.update(self._build_layout())

    def _get_terminal_size(self) -> tuple[int, int]:
        try:
            width, height = os.get_terminal_size()
            return max(width, self.config.min_terminal_width), max(height, self.config.min_terminal_height)
        except OSError:
            return self.config.min_terminal_width, self.config.min_terminal_height

    def _build_progress_bar(self) -> Text:
        progress_in_tick = self._turn % TURNS_PER_WORLD_TICK
        pct = progress_in_tick / TURNS_PER_WORLD_TICK
        bar_len = 20
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        return Text.assemble(
            ("Progress: [", "dim"),
            (bar, CYAN),
            (f"] {progress_in_tick}/{TURNS_PER_WORLD_TICK}", "dim"),
        )

    def _build_top_bar(self) -> Text:
        stab_color = "green" if self._world_info.stability > 60 else "yellow" if self._world_info.stability > 30 else "red"
        press_color = "green" if self._world_info.pressure < 40 else "yellow" if self._world_info.pressure < 60 else "red"

        return Text.assemble(
            ("╔══════════════════╗ ", "dim"),
            ("ECO", s("header")),
            (" ║ T", "dim"),
            (f"{self._turn:03d}", s("turn")),
            (" ║ WT ", "dim"),
            (f"{self._world_tick:02d}", ""),
            (" ║ ", "dim"),
            ("Stab ", "dim"),
            (f"{self._world_info.stability:.0f}", stab_color),
            (" ║ ", "dim"),
            ("Press ", "dim"),
            (f"{self._world_info.pressure:.0f}", press_color),
            (" ║ ", "dim"),
            ("Pop ", "dim"),
            (f"{self._world_info.population:,}", ""),
            (" ╚══════════════════╝", "dim"),
        )

    def _build_echo_panel(self) -> Panel:
        echo = self._echo_info
        lines = [
            Text.assemble(("⚡ ", "dim"), (echo.name, s("echo"))),
            Text.assemble(("   Phase: ", "dim"), (echo.phase, "")),
            Text.assemble(("   Clarity: ", "dim"), (f"{echo.clarity:.0f}", "")),
        ]
        if echo.essences:
            lines.append(Text.assemble(("   Essences: ", "dim"), (", ".join(echo.essences[:3]), "")))

        if self._available_actions:
            lines.append(Text.assemble(("\n   [bold]Actions:[/bold]", s("title"))))
            for i, action in enumerate(self._available_actions[:8], 1):
                lines.append(Text.assemble((f"   {i}. ", "dim"), (action, "")))

        if echo.action_history:
            lines.append(Text.assemble(("\n   Last actions:", s("title"))))
            for action in echo.action_history[-5:]:
                lines.append(Text.assemble(("   → ", "dim"), (action, "")))

        return Panel(
            "\n".join(str(l) for l in lines),
            title="[cyan]⚡ Your Echo[/cyan]",
            border_style="cyan",
            width=48,
        )

    def _build_metrics_panel(self) -> Panel:
        if self._metrics_table:
            return Panel(
                self._metrics_table,
                title="[yellow]📊 World State[/yellow]",
                border_style="yellow",
            )
        return Panel(
            "[dim]Awaiting data...[/dim]",
            title="[yellow]📊 World State[/yellow]",
            border_style="yellow",
        )

    def _build_log_panel(self) -> Panel:
        log_content = "\n".join(self._log_lines[-20:]) if self._log_lines else "[dim]No activity yet[/dim]"
        return Panel(
            log_content,
            title="[green]📜 Activity[/green]",
            border_style="green",
        )

    def _build_layout(self) -> Any:
        from rich.layout import Layout

        term_width, term_height = self._get_terminal_size()

        layout = Layout()

        layout.split_column(
            Layout(name="top_bar", size=3),
            Layout(name="progress", size=3),
            Layout(name="main"),
            Layout(name="bottom", size=3),
        )

        layout["top_bar"].update(Panel(self._build_top_bar(), border_style="cyan"))
        layout["progress"].update(Panel(self._build_progress_bar(), border_style="dim"))

        layout["main"].split_row(
            Layout(name="left", size=50),
            Layout(name="right"),
        )

        layout["left"].split_column(
            Layout(name="echo", size=14),
            Layout(name="civ"),
        )

        layout["echo"].update(self._build_echo_panel())

        civ_text = Text.assemble(
            ("🏛 ", "dim"),
            (self._world_info.civ_name, s("title")),
            "\n",
            ("─" * 20, "dim"), "\n",
            ("   Echoes: ", "dim"), (f"{self._world_info.echoes}", ""), "\n",
            ("   Circles: ", "dim"), (f"{self._world_info.circles}", ""), "\n",
            ("   Factions: ", "dim"), (f"{self._world_info.factions}", ""),
        )
        layout["civ"].update(Panel(civ_text, title="[magenta]🏛 Civilization[/magenta]", border_style="magenta"))

        layout["right"].split_column(
            Layout(name="metrics", size=term_height // 3),
            Layout(name="log"),
        )

        layout["metrics"].update(self._build_metrics_panel())
        layout["log"].update(self._build_log_panel())

        mode_label = {
            "autoplay": "Autoplay Active",
            "hybrid": "Hybrid Mode",
            "player": "Your Turn",
        }.get(self._game_mode, "ECO")

        from game_core.i18n import t
        turn_label = t("ui:turn", default="Turn ")
        footer_text = Text.assemble(
            ("ECO │ ", "dim"),
            (turn_label, "dim"),
            (f"{self._turn}", s("turn")),
            (" │ World Tick ", "dim"),
            (f"{self._world_tick}", ""),
            (" │ ", "dim"),
            (mode_label, "green" if self._game_mode == "player" else "dim"),
        )
        layout["bottom"].update(Panel(footer_text, border_style="cyan"))

        return layout

    def start_live(self, turn: int = 0, world_tick: int = 0) -> None:
        self._turn = turn
        self._world_tick = world_tick
        self._console = RichConsole()
        self._live = Live(
            self._build_layout(),
            console=self._console,
            refresh_per_second=8,
            vertical_overflow="crop",
            transient=False,
        )
        self._live.start()

    def update(
        self,
        turn: int | None = None,
        world_tick: int | None = None,
        echo_info: EchoInfo | None = None,
        world_info: WorldInfo | None = None,
        metrics: Table | None = None,
        log: str | Text | None = None,
    ) -> None:
        if turn is not None:
            self._turn = turn
        if world_tick is not None:
            self._world_tick = world_tick
        if echo_info is not None:
            self._echo_info = echo_info
        if world_info is not None:
            self._world_info = world_info
        if metrics is not None:
            self._metrics_table = metrics
        if log is not None:
            if isinstance(log, str):
                self._log_lines.append(log)
            else:
                self._log_lines.append(str(log))

        if self._live:
            self._live.update(self._build_layout())

    def update_turn(self, turn: int, world_tick: int) -> None:
        self._turn = turn
        self._world_tick = world_tick
        if self._live:
            self._live.update(self._build_layout())

    def stop_live(self) -> None:
        if self._live:
            self._live.stop()
            self._live = None
            self._console = None