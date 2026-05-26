"""Log panel widget."""

from textual.widgets import RichLog
from textual.events import Click


class LogPanel(RichLog):
    def __init__(self, **kwargs):
        super().__init__(id="log-section", auto_scroll=True, markup=True, **kwargs)

    def on_mount(self) -> None:
        self.border_title = "EVENTS (click to copy)"

    def on_click(self, event: Click) -> None:
        app = self.app
        if hasattr(app, '_log_text') and app._log_text:
            app.copy_to_clipboard(app._log_text)