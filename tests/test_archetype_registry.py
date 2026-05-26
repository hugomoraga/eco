"""
Tests for game_core.domain.archetype_registry module.
"""
from __future__ import annotations

import pytest
from core.domain.registries.archetype_registry import (
    ArchetypeRegistry,
    Archetype,
    ArchetypeGoalWeights,
    ArchetypeActionPreferences,
    ArchetypeStats,
    get_archetype,
    get_intro_text,
    get_preferred_action,
    get_goal_weights,
)


class TestArchetypeRegistry:
    def test_singleton_pattern(self):
        reg1 = ArchetypeRegistry.get_instance()
        reg2 = ArchetypeRegistry.get_instance()
        assert reg1 is reg2

    def test_load_defaults(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        artisan = reg.get("artisan")
        assert artisan.id == "artisan"
        assert artisan.display_name == "Artesano"
        assert len(artisan.intro_texts) > 0

    def test_get_archetype(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        artisan = reg.get("artisan")
        assert isinstance(artisan, Archetype)
        assert artisan.id == "artisan"

    def test_get_unknown_archetype_returns_neutral(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        unknown = reg.get("unknown_archetype")
        neutral = reg.get("neutral")
        assert unknown.id == "neutral"
        assert unknown.display_name == neutral.display_name

    def test_get_intro_text(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        intro = reg.get_intro_text("artisan", seed=42)
        assert isinstance(intro, str)
        assert len(intro) > 0

    def test_get_preferred_action(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        action = reg.get_preferred_action("warrior", seed=42)
        assert isinstance(action, str)
        assert action in ["sabotar", "predicar", "organizar", "reclutar", "conversar"]

    def test_all_archetypes(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        archetypes = reg.all_archetypes()
        assert len(archetypes) >= 9
        archetype_ids = [a.id for a in archetypes]
        assert "artisan" in archetype_ids
        assert "warrior" in archetype_ids
        assert "leader" in archetype_ids


class TestArchetype:
    def test_archetype_fields(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        warrior = reg.get("warrior")
        assert warrior.id == "warrior"
        assert warrior.display_name == "Guerrero"
        assert warrior.color == "red"
        assert isinstance(warrior.goal_weights, ArchetypeGoalWeights)
        assert isinstance(warrior.action_preferences, ArchetypeActionPreferences)
        assert isinstance(warrior.base_stats, ArchetypeStats)


class TestArchetypeGoalWeights:
    def test_goal_weights_values(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        merchant = reg.get("merchant")
        gw = merchant.goal_weights
        assert gw.accumulate >= 0.0
        assert gw.progress >= 0.0
        assert gw.survive >= 0.0
        assert gw.maintain >= 0.0
        total = gw.accumulate + gw.progress + gw.survive + gw.maintain
        assert total > 0.0


class TestArchetypeActionPreferences:
    def test_action_preferences_not_empty(self):
        reg = ArchetypeRegistry.get_instance()
        reg._loaded = False
        reg._archetypes = {}
        reg.load_from_yaml("/nonexistent/path.yaml")

        artisan = reg.get("artisan")
        assert len(artisan.action_preferences.preferred_actions) > 0


class TestModuleFunctions:
    def test_get_archetype_function(self):
        arch = get_archetype("artisan")
        assert arch.id == "artisan"

    def test_get_intro_text_function(self):
        intro = get_intro_text("leader", seed=1)
        assert isinstance(intro, str)

    def test_get_preferred_action_function(self):
        action = get_preferred_action("merchant", seed=1)
        assert isinstance(action, str)

    def test_get_goal_weights_function(self):
        gw = get_goal_weights("scholar")
        assert isinstance(gw, ArchetypeGoalWeights)
