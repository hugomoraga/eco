from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from adapters.i18n import t

from .styles import CYAN, s


class Components:
    @staticmethod
    def turn_header(turn: int) -> Text:
        turn_label = t("ui:turn", default="TURN")
        return Text.assemble((f"═══ {turn_label} {turn:03d} ═══", s("header")))

    @staticmethod
    def world_metrics_table(metrics: dict) -> Table:
        table = Table(title="Estado del Mundo", border_style=CYAN)
        table.add_column("Metrica", style="cyan")
        table.add_column("Valor", style="magenta")
        table.add_column("D", style="")

        for key, value in metrics.items():
            table.add_row(key, f"{value:.2f}", "")

        return table

    @staticmethod
    def event_banner(event_type: str, title: str, summary: str = "") -> Panel:
        emoji_map = {
            "crisis": "⚠",
            "opportunity": "✨",
            "echo_created": "🌱",
            "circle_founded": "⭕",
            "faction_formed": "🔱",
            "sabotage": "💥",
            "ritual": "🔮",
        }
        emoji = emoji_map.get(event_type, "📢")
        content = f"[bold]{emoji} {title}[/bold]"
        if summary:
            content += f"\n[dim]{summary}[/dim]"

        border = {"crisis": "red", "opportunity": "green"}.get(event_type, "yellow")
        return Panel(content, border_style=border)

    @staticmethod
    def action_result(action: str, result: str, success: bool = True) -> Text:
        icon = "✓" if success else "✗"
        color = "success" if success else "error"
        return Text.assemble(
            (f"{icon} ", s(color)),
            (action, s("action")),
            (f": {result}", ""),
        )

    @staticmethod
    def metrics_delta_table(old_metrics: dict, new_metrics: dict) -> Table:
        table = Table(title="Cambios", border_style=CYAN, show_header=False)
        table.add_column("Metrica", style="cyan")
        table.add_column("Anterior", style="dim")
        table.add_column("Nuevo", style="magenta")
        table.add_column("D", style="")

        for key, new_val in new_metrics.items():
            old_val = old_metrics.get(key, new_val)
            delta = new_val - old_val

            if abs(delta) < 0.01:
                continue

            sign = "+" if delta >= 0 else ""
            delta_str = f"{sign}{delta:.2f}"
            delta_style = "green" if delta >= 0 else "red"

            table.add_row(
                key,
                f"{old_val:.2f}",
                f"{new_val:.2f}",
                Text(delta_str, style=s(delta_style)),
            )

        return table

    @staticmethod
    def action_detail(key: str, value: str | int | float) -> Text:
        if isinstance(value, (int, float)):
            sign = "+" if value >= 0 else ""
            color = "green" if value >= 0 else "red"
            return Text.assemble(
                (f"  -> {key}: ", "dim"),
                (f"{sign}{value}", s(color)),
            )
        return Text.assemble(
            (f"  -> {key}: ", "dim"),
            (str(value), ""),
        )

    @staticmethod
    def status_line(
        turn: int,
        world_tick: int,
        echoes: int,
        circles: int,
        factions: int,
        influence: int,
        persons: int = 0,
    ) -> Text:
        return Text.assemble(
            (f"[Turn {turn:2d}]", s("turn")),
            (" WT=", "dim"),
            (f"{world_tick}", ""),
            (" | Echoes=", "dim"),
            (f"{echoes}", s("echo")),
            (" | Circles=", "dim"),
            (f"{circles}", s("circle")),
            (" | Factions=", "dim"),
            (f"{factions}", s("faction")),
            (" | Persons=", "dim"),
            (f"{persons}", s("info")),
            (" | Influence=", "dim"),
            (f"{influence}", s("info")),
        )
