"""Echo panel widget."""

from textual.widgets import Static

from adapters.tui.textual.colors import CYAN, DIM, GREEN, MAGENTA, RED, YELLOW

ACTION_ICONS = {
    "found_circle": "🔵",
    "write_manifesto": "📜",
    "propagate_idea": "📣",
    "talk": "💬",
    "sabotage": "💥",
    "ritualize": "🔮",
    "join_circle": "➕",
    "leave_circle": "➖",
    "spread_rumor": "🌫️",
    "recruit_follower": "👤",
    "negotiate": "🤝",
    "ritual": "🙏",
}


def _icon_for_action(action: str) -> str:
    return ACTION_ICONS.get(action, "•")


def _make_history_display(history: list[str], max_show: int = 12) -> str:
    if not history:
        return "---"
    shown = history[-max_show:]
    icons = [_icon_for_action(a) for a in shown]
    return "".join(icons)


def _make_history_labels(history: list[str], max_show: int = 12) -> str:
    if not history:
        return ""
    shown = history[-max_show:]
    return " ".join(shown)


def make_echo_content(
    name: str,
    phase: str,
    clarity: float,
    essences: list[str],
    history: list[str],
    influence: float = 0.0,
    vitality: float = 100.0,
) -> str:
    ess = ", ".join(essences[:3]) or "---"
    hist_icons = _make_history_display(history)
    hist_labels = _make_history_labels(history)

    influence_bar = _make_bar(influence, 8, YELLOW)
    vitality_bar = _make_bar(
        vitality, 8, GREEN if vitality > 50 else YELLOW if vitality > 25 else RED
    )
    vitality_color = GREEN if vitality > 50 else YELLOW if vitality > 25 else RED

    return (
        f"[bold]Name:[/bold] [{GREEN}]{name}[/{GREEN}]\n"
        f"[bold]Phase:[/bold] [{DIM}]{phase}[/{DIM}]\n"
        f"[bold]Clarity:[/bold] [{CYAN}]{clarity:.0f}[/{CYAN}]\n"
        f"[bold]Essence:[/bold] [{MAGENTA}]{ess}[/{MAGENTA}]\n"
        f"[bold]Health:[/bold] {vitality_bar} [{vitality_color}]{vitality:.0f}[/{vitality_color}]\n"
        f"[bold]Influence:[/bold] {influence_bar} [{YELLOW}]{influence:.0f}[/{YELLOW}]\n"
        f"[bold]History:[/bold] [{DIM}]{hist_icons}[/{DIM}]\n"
        f"[dim]{hist_labels}[/dim]"
    )


def _make_bar(value: float, width: int, color: str) -> str:
    filled = int((value / 100) * width)
    filled = max(0, min(width, filled))
    return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * (width - filled)}[/dim]"


class EchoPanel(Static):
    def __init__(self, **kwargs):
        super().__init__("", id="echo-section", **kwargs)

    def on_mount(self) -> None:
        self.border_title = "ECHO"

    def update_state(
        self,
        name: str,
        phase: str,
        clarity: float,
        essences: list[str],
        history: list[str],
        influence: float = 0.0,
        vitality: float = 100.0,
    ) -> None:
        self.update(make_echo_content(name, phase, clarity, essences, history, influence, vitality))
