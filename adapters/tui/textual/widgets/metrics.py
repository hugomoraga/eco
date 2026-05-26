"""Metrics panel widget."""

from textual.widgets import Static
from adapters.tui.textual.colors import YELLOW, GREEN, CYAN, DIM, RED


MAX_BAR_WIDTH = 12


def _make_bar(value: float, max_val: float, width: int, color: str) -> str:
    ratio = max(0.0, min(1.0, value / max_val))
    filled = int(ratio * width)
    return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * (width - filled)}[/dim]"


def make_metrics_content(
    pressure: float,
    legitimacy: float,
    resources: float,
    stability: float,
    max_val: float = 100.0,
) -> str:
    pressure_bar = _make_bar(pressure, max_val, MAX_BAR_WIDTH, YELLOW)
    legit_bar = _make_bar(legitimacy, max_val, MAX_BAR_WIDTH, GREEN)
    resources_bar = _make_bar(resources, max_val, MAX_BAR_WIDTH, CYAN)
    stab_bar = _make_bar(stability, max_val, MAX_BAR_WIDTH, GREEN if stability > 60 else YELLOW if stability > 30 else RED)

    return (
        f"[bold]Pressure:[/bold] {pressure_bar} [{YELLOW}]{pressure:.0f}[/{YELLOW}]\n"
        f"[bold]Legitimacy:[/bold] {legit_bar} [{GREEN}]{legitimacy:.0f}[/{GREEN}]\n"
        f"[bold]Resources:[/bold] {resources_bar} [{CYAN}]{resources:.0f}[/{CYAN}]\n"
        f"[bold]Stability:[/bold] {stab_bar} [{GREEN if stability > 60 else YELLOW if stability > 30 else RED}]{stability:.0f}[/{GREEN if stability > 60 else YELLOW if stability > 30 else RED}]"
    )


class MetricsPanel(Static):
    def __init__(self, **kwargs):
        super().__init__("", id="metrics-section", **kwargs)

    def on_mount(self) -> None:
        self.border_title = "METRICS"

    def update_state(
        self,
        pressure: float,
        legitimacy: float,
        resources: float,
        stability: float,
        max_val: float = 100.0,
    ) -> None:
        self.update(make_metrics_content(pressure, legitimacy, resources, stability, max_val))