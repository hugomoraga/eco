"""Actions bar widget with Select dropdown."""

from textual import on
from textual.containers import Horizontal
from textual.widgets import Select
from adapters.tui.textual.styles import ACTIONS


def make_actions_text() -> str:
    parts = []
    for i, action in enumerate(ACTIONS, 1):
        parts.append(f"[cyan]{i}[/cyan] {action}")
    return "  ".join(parts)


class ActionsBar(Horizontal):
    def __init__(self, **kwargs):
        super().__init__(id="actions-bar", **kwargs)

    def compose(self):
        options = [(action.replace("_", " ").title(), action) for action in ACTIONS]
        yield Select(options, id="action-select", allow_blank=True)

    @on(Select.Changed)
    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value and event.value != Select.BLANK:
            self.app._do_from_select(event.value)
            event.select.clear()