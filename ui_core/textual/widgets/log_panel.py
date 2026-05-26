"""Log panel widget."""

from textual.widgets import Log


class LogPanel(Log):
    def __init__(self, **kwargs):
        super().__init__("", id="log-section", border_title="LOG", border_subtitle="activity", **kwargs)

    def write(self, message: str) -> None:
        super().write(message, auto_scroll=True)