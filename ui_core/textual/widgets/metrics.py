"""Metrics panel widget."""

from textual.widgets import Static
from ui_core.textual.colors import YELLOW, GREEN, CYAN, DIM, RED


def make_metrics_content(pressure: float, legitimacy: float, resources: float, stability: float) -> str:
    stab_c = GREEN if stability > 60 else YELLOW if stability > 30 else RED
    return (
        f"Pressure: [{YELLOW}]{pressure:.1f}[/{YELLOW}]\n"
        f"Legitimacy: [{GREEN}]{legitimacy:.1f}[/{GREEN}]\n"
        f"Resources: [{CYAN}]{resources:.1f}[/{CYAN}]\n"
        f"Stability: [{stab_c}]{stability:.1f}[/{stab_c}]"
    )


class MetricsPanel(Static):
    def __init__(self, **kwargs):
        super().__init__("", id="metrics-section", **kwargs)

    def on_mount(self) -> None:
        self.border_title = "METRICS"

    def update_state(self, pressure: float, legitimacy: float, resources: float, stability: float) -> None:
        self.update(make_metrics_content(pressure, legitimacy, resources, stability))