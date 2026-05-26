"""Log panel widget."""

from textual.widgets import Log


class LogPanel(Log):
    def __init__(self, **kwargs):
        super().__init__("", id="log-section", **kwargs)