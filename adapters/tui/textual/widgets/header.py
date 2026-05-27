"""Header bar widget."""

from textual.widgets import Static

from adapters.tui.textual.colors import CYAN, DIM, GREEN, RED, YELLOW


def make_header(
    turn: int, world_tick: int, stability: float, pressure: float, population: int
) -> str:
    stab_c = GREEN if stability > 60 else YELLOW if stability > 30 else RED
    press_c = GREEN if pressure < 40 else YELLOW if pressure < 60 else RED

    return (
        f"[{CYAN} bold]ECO[/{CYAN} bold]"
        f"  Turn:[{YELLOW}]{turn:03d}[/{YELLOW}]"
        f"  WT:[{DIM}]{world_tick}[/{DIM}]"
        f"  Stab:[{stab_c}]{stability:.0f}[/{stab_c}]"
        f"  Press:[{press_c}]{pressure:.0f}[/{press_c}]"
        f"  Pop:[{DIM}]{population:,}[/{DIM}]"
    )


class HeaderBar(Static):
    def __init__(self, **kwargs):
        super().__init__("", id="header-bar", **kwargs)

    def update_state(
        self, turn: int, world_tick: int, stability: float, pressure: float, population: int
    ) -> None:
        self.update(make_header(turn, world_tick, stability, pressure, population))
