"""CSS styles for EcoTextualApp."""

SCREEN_BG = "#0a0a12"
PANEL_BG = "#0f0f1f"
ACCENT = "cyan"

CSS = """
Screen { background: """ + SCREEN_BG + """; }

#header-bar {
    height: 3;
    background: """ + PANEL_BG + """;
    border-bottom: heavy cyan;
}

#main-area {
    width: 100%;
    height: 1fr;
}

#left-col {
    width: 35%;
}

#echo-section {
    height: 14;
    border: round """ + ACCENT + """ 40%;
    border-title-color: """ + ACCENT + """;
    border-title-align: right;
}

#civ-section {
    border: round magenta 40%;
    border-title-color: magenta;
    border-title-align: right;
}

#right-col {
    width: 65%;
}

#metrics-section {
    height: 14;
    border: round yellow 40%;
    border-title-color: yellow;
    border-title-align: right;
}

#log-section {
    border: round green 40%;
    border-title-color: green;
    border-title-align: right;
}

#action-bar {
    height: 4;
    background: """ + PANEL_BG + """;
    border-top: heavy yellow;
}

#actions-display {
    width: 100%;
}

Footer { dock: bottom; }
"""

COLORS = {
    "cyan": "cyan",
    "magenta": "magenta",
    "yellow": "yellow",
    "green": "green",
    "red": "red",
    "white": "white",
    "dim": "dim",
}

ACTIONS = ["found_circle", "join_circle", "leave_circle", "propagate_idea",
           "write_manifesto", "sabotage", "ritualize", "talk"]