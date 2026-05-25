from rich.style import Style

CYAN = "#00D4FF"
YELLOW = "#FFD700"
GREEN = "#00FF88"
RED = "#FF4444"
MAGENTA = "#FF00FF"
GRAY = "#666666"
WHITE = "#FFFFFF"

STYLES = {
    "header": Style(color=CYAN, bold=True),
    "title": Style(color=YELLOW, bold=True),
    "success": Style(color=GREEN),
    "warning": Style(color=YELLOW),
    "error": Style(color=RED, bold=True),
    "dim": Style(color=GRAY, dim=True),
    "info": Style(color=MAGENTA),
    "metric_positive": Style(color=GREEN, bold=True),
    "metric_negative": Style(color=RED, bold=True),
    "action": Style(color=CYAN),
    "prompt": Style(color=WHITE, bold=True),
    "echo": Style(color=GREEN, italic=True),
    "circle": Style(color=YELLOW),
    "faction": Style(color=MAGENTA),
    "turn": Style(color=CYAN, bold=True),
    "event": Style(color=YELLOW, bold=True),
    "result_success": Style(color=GREEN, bold=True),
    "result_failure": Style(color=RED, bold=True),
}


def s(name: str) -> Style:
    return STYLES.get(name, Style.null())
