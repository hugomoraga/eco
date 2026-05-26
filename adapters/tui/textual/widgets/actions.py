"""Actions bar widget."""

from textual.widgets import Static
from adapters.tui.textual.colors import CYAN
from adapters.tui.textual.styles import ACTIONS


def make_actions_text() -> str:
    parts = []
    for i, action in enumerate(ACTIONS, 1):
        parts.append(f"[{CYAN}]{i}[/{CYAN}] {action}")
    return "  ".join(parts)


class ActionsBar(Static):
    def __init__(self, **kwargs):
        super().__init__("", id="actions-display", **kwargs)