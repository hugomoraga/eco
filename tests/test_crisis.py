"""
Tests for game_core.domain.crisis module.
"""
from __future__ import annotations

import pytest
from core.domain.rules.crisis import (
    CrisisType,
    CrisisEffect,
    Crisis,
    get_random_crisis,
    create_crisis,
    should_trigger_crisis,
    format_crisis_narrative,
    CRISIS_DATA,
)


class TestCrisisType:
    def test_crisis_types_exist(self):
        assert CrisisType.FOOD_SHORTAGE.value == "food_shortage"
        assert CrisisType.COMMUNICATION_FAILURE.value == "communication_failure"
        assert CrisisType.PROTEST.value == "protest"
        assert CrisisType.DISEASE.value == "disease"
        assert CrisisType.REPRESSION.value == "repression"
        assert CrisisType.PROSPERITY.value == "prosperity"


class TestCrisis:
    def test_crisis_creation(self):
        crisis = create_crisis(CrisisType.FOOD_SHORTAGE)
        assert crisis.crisis_type == CrisisType.FOOD_SHORTAGE
        assert crisis.title == "Escasez de alimentos"
        assert isinstance(crisis.effects, CrisisEffect)

    def test_crisis_with_custom_turns(self):
        crisis = create_crisis(CrisisType.PROTEST, turns=5)
        assert crisis.turns_remaining == 5

    def test_crisis_effects(self):
        crisis = create_crisis(CrisisType.REPRESSION)
        effects = crisis.effects
        assert effects.legitimacy_change < 0
        assert effects.pressure_change > 0


class TestGetRandomCrisis:
    def test_get_random_crisis_returns_crisis(self):
        crisis = get_random_crisis(seed=42)
        assert isinstance(crisis, Crisis)
        assert crisis.crisis_type in list(CrisisType)

    def test_get_random_crisis_with_seed(self):
        crisis1 = get_random_crisis(seed=100)
        crisis2 = get_random_crisis(seed=100)
        assert crisis1.crisis_type == crisis2.crisis_type


class TestShouldTriggerCrisis:
    def test_does_not_trigger_on_check_interval(self):
        world_state = {"legitimacy": 50, "pressure": 30, "resources_global": 50}
        assert should_trigger_crisis(world_state, check_interval=3, tick=1) is False
        assert should_trigger_crisis(world_state, check_interval=3, tick=2) is False

    def test_triggers_on_low_legitimacy(self):
        world_state = {"legitimacy": 20, "pressure": 30, "resources_global": 50}
        result = should_trigger_crisis(world_state, check_interval=3, tick=3)
        assert result is True

    def test_triggers_on_high_pressure(self):
        world_state = {"legitimacy": 50, "pressure": 90, "resources_global": 50}
        result = should_trigger_crisis(world_state, check_interval=3, tick=6)
        assert result is True

    def test_triggers_on_low_resources(self):
        world_state = {"legitimacy": 50, "pressure": 30, "resources_global": 10}
        result = should_trigger_crisis(world_state, check_interval=3, tick=9)
        assert result is True


class TestFormatCrisisNarrative:
    def test_format_crisis_narrative(self):
        crisis = create_crisis(CrisisType.FOOD_SHORTAGE)
        output = format_crisis_narrative(crisis)
        assert "Escasez" in output
        assert "mercados" in output.lower()

    def test_format_crisis_includes_effects(self):
        crisis = create_crisis(CrisisType.PROSPERITY)
        output = format_crisis_narrative(crisis)
        assert "legitimacy" in output.lower() or "+" in output


class TestCrisisData:
    def test_all_crisis_types_have_data(self):
        for crisis_type in CrisisType:
            assert crisis_type in CRISIS_DATA
            data = CRISIS_DATA[crisis_type]
            assert "title" in data
            assert "description" in data
            assert "narrative" in data
            assert "effects" in data

    def test_crisis_effects_have_required_fields(self):
        for crisis_type, data in CRISIS_DATA.items():
            effects = data["effects"]
            assert "legitimacy_change" in effects
            assert "pressure_change" in effects
            assert "resources_change" in effects
            assert "vitality_change" in effects
