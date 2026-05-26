"""
Tests for adapters module - hexagonal architecture adapter layer.
"""
from __future__ import annotations

import pytest

from adapters.ai.base import GameAdapter
from adapters.ai.input_source.base import InputSource
from adapters.ai.input_source.autoplay import AutoplayInputSource
from adapters.ai.input_source.player import PlayerInputSource
from adapters.ai.input_source.hybrid import HybridInputSource
from adapters.ai.input_source.factory import (
    create_input_source,
    create_input_source_for_mode,
)
from adapters.ai import HumanGameAdapter, AIGameAdapter


class TestInputSourceBase:
    """Tests for InputSource abstract base class."""

    def test_autoplay_input_source_mode(self):
        """AutoplayInputSource should have autoplay mode."""
        source = AutoplayInputSource()
        assert source.mode == "autoplay"

    def test_autoplay_input_source_never_returns_action(self):
        """AutoplayInputSource should always return None."""
        source = AutoplayInputSource()
        result = source.get_action(1, None)
        assert result is None

    def test_autoplay_input_source_no_realtime_override(self):
        """AutoplayInputSource should not support realtime override."""
        source = AutoplayInputSource()
        assert source.supports_realtime_override() is False


class TestPlayerInputSource:
    """Tests for PlayerInputSource."""

    def test_player_input_source_mode(self):
        """PlayerInputSource should have player mode."""
        source = PlayerInputSource()
        assert source.mode == "player"

    def test_player_input_source_supports_realtime_override(self):
        """PlayerInputSource should support realtime override."""
        source = PlayerInputSource()
        assert source.supports_realtime_override() is True

    def test_player_input_source_inject_action(self):
        """PlayerInputSource should allow injecting actions."""
        source = PlayerInputSource()
        source.inject_action("found_circle")
        result = source.get_action(1, None)
        assert result == "found_circle"

    def test_player_input_source_inject_clears_after_use(self):
        """PlayerInputSource should clear injected action after use."""
        source = PlayerInputSource()
        source.inject_action("found_circle")
        first_result = source.get_action(1, None)
        assert first_result == "found_circle"
        # After use, pending action is cleared
        # We verify by checking internal state
        assert source._pending_action is None


class TestHybridInputSource:
    """Tests for HybridInputSource."""

    def test_hybrid_input_source_mode(self):
        """HybridInputSource should have hybrid mode."""
        source = HybridInputSource()
        assert source.mode == "hybrid"

    def test_hybrid_input_source_supports_realtime_override(self):
        """HybridInputSource should support realtime override."""
        source = HybridInputSource()
        assert source.supports_realtime_override() is True

    def test_hybrid_input_source_inject_action(self):
        """HybridInputSource should allow injecting actions."""
        source = HybridInputSource()
        source.inject_action("propagate_idea")
        result = source.get_action(1, None)
        assert result == "propagate_idea"


class TestCreateInputSource:
    """Tests for factory functions."""

    def test_create_input_source_autoplay(self):
        """create_input_source with autoplay=True should return AutoplayInputSource."""
        source = create_input_source(autoplay=True)
        assert isinstance(source, AutoplayInputSource)

    def test_create_input_source_for_mode_autoplay(self):
        """create_input_source_for_mode with autoplay should return AutoplayInputSource."""
        source = create_input_source_for_mode("autoplay")
        assert isinstance(source, AutoplayInputSource)

    def test_create_input_source_for_mode_player(self):
        """create_input_source_for_mode with player should return PlayerInputSource."""
        source = create_input_source_for_mode("player")
        assert isinstance(source, PlayerInputSource)

    def test_create_input_source_for_mode_hybrid(self):
        """create_input_source_for_mode with hybrid should return HybridInputSource."""
        source = create_input_source_for_mode("hybrid")
        assert isinstance(source, HybridInputSource)


class TestGameAdapterBase:
    """Tests for GameAdapter abstract base class."""

    def test_game_adapter_initial_state(self):
        """GameAdapter initial state should be correct."""
        class ConcreteAdapter(GameAdapter):
            def connect(self, engine): pass
            def on_world_state(self, turn, world_state): pass
            def on_event(self, event_type, data): pass
            def on_action_result(self, turn, action, success, message): pass
            def start(self): pass
            def stop(self): pass

        adapter = ConcreteAdapter()
        assert adapter._engine is None
        assert adapter._running is False
        assert adapter._input_source is None

    def test_game_adapter_input_source_property(self):
        """GameAdapter should expose input_source property."""
        class ConcreteAdapter(GameAdapter):
            def connect(self, engine): pass
            def on_world_state(self, turn, world_state): pass
            def on_event(self, event_type, data): pass
            def on_action_result(self, turn, action, success, message): pass
            def start(self): pass
            def stop(self): pass

        source = AutoplayInputSource()
        adapter = ConcreteAdapter(input_source=source)
        assert adapter.input_source is source

    def test_game_adapter_cannot_instantiate_directly(self):
        """GameAdapter cannot be instantiated directly (abstract)."""
        with pytest.raises(TypeError):
            GameAdapter()


class TestHumanGameAdapter:
    """Tests for HumanGameAdapter."""

    def test_human_game_adapter_creation(self):
        """HumanGameAdapter should be creatable."""
        adapter = HumanGameAdapter()
        assert isinstance(adapter, GameAdapter)

    def test_human_game_adapter_has_player_input_source(self):
        """HumanGameAdapter should have PlayerInputSource."""
        adapter = HumanGameAdapter()
        assert isinstance(adapter.input_source, PlayerInputSource)

    def test_human_game_adapter_cannot_start_without_engine(self):
        """HumanGameAdapter.start() should raise if not connected."""
        adapter = HumanGameAdapter()
        with pytest.raises(RuntimeError, match="not connected"):
            adapter.start()


class TestAIGameAdapter:
    """Tests for AIGameAdapter."""

    def test_ai_game_adapter_creation(self):
        """AIGameAdapter should be creatable."""
        adapter = AIGameAdapter()
        assert isinstance(adapter, GameAdapter)

    def test_ai_game_adapter_has_autoplay_input_source(self):
        """AIGameAdapter should have AutoplayInputSource."""
        adapter = AIGameAdapter()
        assert isinstance(adapter.input_source, AutoplayInputSource)

    def test_ai_game_adapter_cannot_start_without_engine(self):
        """AIGameAdapter.start() should raise if not connected."""
        adapter = AIGameAdapter()
        with pytest.raises(RuntimeError, match="not connected"):
            adapter.start()

    def test_ai_game_adapter_has_autoplayer_engine(self):
        """AIGameAdapter should have internal AutoplayerEngine."""
        from adapters.autoplayer import AutoplayerEngine

        adapter = AIGameAdapter()
        assert isinstance(adapter._autoplay_engine, AutoplayerEngine)

    def test_ai_game_adapter_default_style(self):
        """AIGameAdapter should use preservationist style by default."""
        adapter = AIGameAdapter()
        assert adapter._autoplay_engine.style.id == "preservationist"

    def test_ai_game_adapter_custom_style(self):
        """AIGameAdapter should accept custom style."""
        adapter = AIGameAdapter(style="revolutionary")
        assert adapter._autoplay_engine.style.id == "revolutionary"

    def test_ai_game_adapter_available_actions(self):
        """AIGameAdapter should have list of available actions."""
        adapter = AIGameAdapter()
        assert isinstance(adapter._available_actions, list)
        assert "found_circle" in adapter._available_actions
        assert "propagate_idea" in adapter._available_actions
        assert "write_manifesto" in adapter._available_actions
