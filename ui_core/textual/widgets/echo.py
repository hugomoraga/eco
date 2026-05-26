"""Echo panel widget."""

from textual.widgets import Static
from ui_core.textual.colors import CYAN, MAGENTA, DIM, GREEN


def make_echo_content(name: str, phase: str, clarity: float, essences: list[str], history: list[str]) -> str:
    ess = ", ".join(essences[:3]) or "---"
    hist = " ".join(history[-4:]) or "---"

    return (
        f"Name: [{GREEN}]{name}[/{GREEN}]\n"
        f"Phase: [{DIM}]{phase}[/{DIM}]\n"
        f"Clarity: [{CYAN}]{clarity:.0f}[/{CYAN}]\n"
        f"Essence: [{MAGENTA}]{ess}[/{MAGENTA}]\n"
        f"History: [{DIM}]{hist}[/{DIM}]"
    )


class EchoPanel(Static):
    def __init__(self, **kwargs):
        super().__init__("", id="echo-section", **kwargs)

    def on_mount(self) -> None:
        self.border_title = "ECHO"

    def update_state(self, name: str, phase: str, clarity: float, essences: list[str], history: list[str]) -> None:
        self.update(make_echo_content(name, phase, clarity, essences, history))