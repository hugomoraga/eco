"""
Entry point for ECO Textual UI.
Run with: python -m ui_core.textual
"""

from adapters.tui.textual.app import EcoTextualApp


if __name__ == "__main__":
    app = EcoTextualApp()
    app.run()