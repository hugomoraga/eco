"""Civ panel widget."""

from textual.widgets import Static
from ui_core.textual.colors import MAGENTA, CYAN, YELLOW, DIM, GREEN


def make_civ_content(name: str, echoes: int, circles: int, factions: int, population: int) -> str:
    return (
        f"Name: [{GREEN}]{name}[/{GREEN}]\n"
        f"Echoes: [{CYAN}]{echoes}[/{CYAN}]"
        f"  Circles: [{YELLOW}]{circles}[/{YELLOW}]"
        f"  Factions: [{MAGENTA}]{factions}[/{MAGENTA}]\n"
        f"Pop: [{DIM}]{population:,}[/{DIM}]"
    )


class CivPanel(Static):
    def __init__(self, **kwargs):
        super().__init__("", id="civ-section", **kwargs)

    def on_mount(self) -> None:
        self.border_title = "CIV"

    def update_state(self, name: str, echoes: int, circles: int, factions: int, population: int) -> None:
        self.update(make_civ_content(name, echoes, circles, factions, population))