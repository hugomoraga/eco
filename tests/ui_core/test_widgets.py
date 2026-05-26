"""Tests for ui_core.textual.widgets."""
from __future__ import annotations

from ui_core.textual.widgets.header import HeaderBar, make_header
from ui_core.textual.widgets.echo import EchoPanel, make_echo_content
from ui_core.textual.widgets.civ import CivPanel, make_civ_content
from ui_core.textual.widgets.metrics import MetricsPanel, make_metrics_content
from ui_core.textual.widgets.actions import ActionsBar, make_actions_text
from ui_core.textual.widgets.log_panel import LogPanel
from ui_core.textual.styles import ACTIONS, COLORS, SCREEN_BG, PANEL_BG
from ui_core.textual.colors import CYAN, MAGENTA, YELLOW, GREEN, RED, WHITE, DIM


class TestColors:
    def test_colors_defined(self):
        assert CYAN == "cyan"
        assert MAGENTA == "magenta"
        assert YELLOW == "yellow"
        assert GREEN == "green"
        assert RED == "red"
        assert WHITE == "white"
        assert DIM == "dim"


class TestStyles:
    def test_actions_defined(self):
        assert len(ACTIONS) == 8
        assert "found_circle" in ACTIONS
        assert "join_circle" in ACTIONS

    def test_colors_dict(self):
        assert COLORS["cyan"] == "cyan"
        assert COLORS["magenta"] == "magenta"

    def test_screen_bg(self):
        assert SCREEN_BG == "#0a0a12"

    def test_panel_bg(self):
        assert PANEL_BG == "#0f0f1f"


class TestMakeHeader:
    def test_make_header_default(self):
        result = make_header(turn=1, world_tick=10, stability=50.0, pressure=50.0, population=100)
        assert "ECO" in result
        assert "001" in result
        assert "100" in result

    def test_make_header_high_stability(self):
        result = make_header(turn=1, world_tick=10, stability=70.0, pressure=30.0, population=100)
        assert "green" in result.lower() or "GREEN" in result

    def test_make_header_low_stability(self):
        result = make_header(turn=1, world_tick=10, stability=20.0, pressure=30.0, population=100)
        assert "red" in result.lower() or "RED" in result


class TestHeaderBar:
    def test_header_bar_init(self):
        bar = HeaderBar()
        assert bar.id == "header-bar"

    def test_header_bar_update_state(self):
        bar = HeaderBar()
        bar.update_state(turn=5, world_tick=20, stability=60.0, pressure=40.0, population=500)
        content = bar.renderable if hasattr(bar, 'renderable') else str(bar._nodes)
        assert content is not None


class TestMakeEchoContent:
    def test_make_echo_content(self):
        result = make_echo_content(
            name="TestEcho",
            phase="seeker",
            clarity=75.0,
            essences=["anarchism", "freedom"],
            history=["born", "joined"]
        )
        assert "TestEcho" in result
        assert "seeker" in result
        assert "75" in result


class TestEchoPanel:
    def test_echo_panel_init(self):
        panel = EchoPanel()
        assert panel.id == "echo-section"

    def test_echo_panel_update_state(self):
        panel = EchoPanel()
        panel.update_state(
            name="TestEcho",
            phase="seeker",
            clarity=75.0,
            essences=["anarchism"],
            history=["born"]
        )


class TestMakeCivContent:
    def test_make_civ_content(self):
        result = make_civ_content(
            name="TestCiv",
            echoes=10,
            circles=3,
            factions=2,
            population=1000
        )
        assert "TestCiv" in result
        assert "10" in result
        assert "3" in result
        assert "1,000" in result


class TestCivPanel:
    def test_civ_panel_init(self):
        panel = CivPanel()
        assert panel.id == "civ-section"

    def test_civ_panel_update_state(self):
        panel = CivPanel()
        panel.update_state(name="TestCiv", echoes=5, circles=2, factions=1, population=500)


class TestMakeMetricsContent:
    def test_make_metrics_content(self):
        result = make_metrics_content(
            pressure=50.0,
            legitimacy=60.0,
            resources=70.0,
            stability=55.0
        )
        assert "50" in result
        assert "60" in result
        assert "70" in result
        assert "55" in result


class TestMetricsPanel:
    def test_metrics_panel_init(self):
        panel = MetricsPanel()
        assert panel.id == "metrics-section"

    def test_metrics_panel_update_state(self):
        panel = MetricsPanel()
        panel.update_state(pressure=40.0, legitimacy=60.0, resources=80.0, stability=50.0)


class TestMakeActionsText:
    def test_make_actions_text(self):
        result = make_actions_text()
        assert "1" in result
        assert "8" in result
        assert "found_circle" in result
        assert "talk" in result


class TestActionsBar:
    def test_actions_bar_init(self):
        bar = ActionsBar()
        assert bar.id == "actions-display"

    def test_actions_bar_content(self):
        bar = ActionsBar()
        content = bar.renderable if hasattr(bar, 'renderable') else str(bar._nodes)


class TestLogPanel:
    def test_log_panel_init(self):
        panel = LogPanel()
        assert panel.id == "log-section"
        assert panel.auto_scroll is True
        assert panel.markup is True
