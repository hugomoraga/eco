from typing import Any

from rich.console import Console as RichConsole
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class Console:
    _instance: "Console | None" = None

    def __init__(self):
        self._console = RichConsole()
        self._live: Live | None = None

    @classmethod
    def get(cls) -> "Console":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def print(self, *args: Any, **kwargs: Any) -> None:
        self._console.print(*args, **kwargs)

    def print_panel(
        self,
        content: str | Text,
        title: str = "",
        border_style: str = "green",
    ) -> None:
        self._console.print(
            Panel(content, title=title, border_style=border_style)
        )

    def print_table(
        self,
        title: str,
        rows: list[list[str]],
        columns: list[str],
    ) -> None:
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        self._console.print(table)

    def print_divider(self, char: str = "─", color: str = "cyan") -> None:
        self._console.print(f"[{color}]{char * 60}[/{color}]")

    def clear(self) -> None:
        self._console.clear()

    def start_live(self, renderable: Any) -> None:
        self._live = Live(
            renderable, console=self._console, refresh_per_second=4
        )
        self._live.start()

    def update_live(self, renderable: Any) -> None:
        if self._live:
            self._live.update(renderable)

    def stop_live(self) -> None:
        if self._live:
            self._live.stop()
            self._live = None

    def rule(self, title: str = "", style: str = "cyan") -> None:
        self._console.rule(title, style=style)
