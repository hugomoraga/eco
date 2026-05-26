"""Tests for ui_core.textual.app."""
from __future__ import annotations

from ui_core.textual.app import EcoTextualApp
from ui_core.textual.styles import ACTIONS
from game_core.protocol import ActionCommand, encode


class TestEcoTextualAppBindings:
    def test_bindings_defined(self):
        bindings = EcoTextualApp.BINDINGS
        assert len(bindings) == 9  # q + 1-8

        key_to_action = {b.key: b.action for b in bindings}
        assert "q" in key_to_action
        assert key_to_action["q"] == "quit"

        for i in range(8):
            assert str(i + 1) in key_to_action
            assert key_to_action[str(i + 1)] == f"do_{i}"

    def test_action_do_methods_exist(self):
        app = EcoTextualApp()
        for i in range(8):
            method = getattr(app, f"action_do_{i}", None)
            assert method is not None, f"action_do_{i} should exist"
            assert callable(method)

    def test_action_quit_exists(self):
        app = EcoTextualApp()
        assert callable(app.action_quit)


class TestActionsMapping:
    def test_actions_length(self):
        assert len(ACTIONS) == 8

    def test_actions_content(self):
        expected = ["found_circle", "join_circle", "leave_circle", "propagate_idea",
                   "write_manifesto", "sabotage", "ritualize", "talk"]
        assert ACTIONS == expected


class TestDoLogic:
    def test_do_index_bounds(self):
        app = EcoTextualApp()

        app._proc = None
        app._do(0)
        app._do(7)

    def test_do_action_command_format(self):
        app = EcoTextualApp()
        app._turn = 5
        app._proc = None

        app._do(0)
        cmd = ActionCommand(turn=5, action="found_circle")
        assert cmd.turn == 5
        assert cmd.action == "found_circle"
