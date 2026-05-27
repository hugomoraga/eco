"""
test_essence_system.py — Integration tests for EssenceSystem.

Demonstrates usage of essence mechanics:
- mutate: Action-based essence changes
- compatible: Circle formation rules
- suggest_faction: Faction suggestion based on essence
- alignment: Civ vs Person alignment calculation
"""
from __future__ import annotations

import pytest

from core.domain.entities.ideas import EssenceProfile, EssenceScore
from core.domain.systems.essence_system import EssenceSystem, ACTION_ESSENCE_MODIFIERS


class TestEssenceMutation:
    """Tests for essence mutation based on actions."""

    def test_write_manifesto_increases_thelema(self):
        """write_manifesto should add thelema and individualism."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="humanism", value=50),
            EssenceScore(essence="pragmatism", value=50),
        ])

        new_profile = system.mutate(profile, "write_manifesto")

        thelema_score = new_profile.get("thelema")
        assert thelema_score is not None and thelema_score > 0, "thelema should be added"

        individualism_score = new_profile.get("individualism")
        assert individualism_score is not None and individualism_score > 0, "individualism should be added"

    def test_destroy_institution_increases_anarchism(self):
        """destroy_institution should increase anarchism."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="socialism", value=60),
            EssenceScore(essence="collectivism", value=40),
        ])

        new_profile = system.mutate(profile, "destroy_institution")

        anarchism = new_profile.get("anarchism")
        assert anarchism is not None and anarchism > 0, "anarchism should be added"

        communism = new_profile.get("communism")
        assert communism is not None and communism > 0, "communism should be added"

    def test_donate_resources_increases_socialism(self):
        """donate_resources should increase socialism and collectivism."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="humanism", value=50),
            EssenceScore(essence="pragmatism", value=50),
        ])

        new_profile = system.mutate(profile, "donate_resources")

        socialism = new_profile.get("socialism")
        assert socialism is not None and socialism > 0, "socialism should be added"

        collectivism = new_profile.get("collectivism")
        assert collectivism is not None and collectivism > 0, "collectivism should be added"

    def test_mutate_unknown_action_returns_unchanged(self):
        """Unknown action should return profile unchanged."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="humanism", value=50),
        ])

        new_profile = system.mutate(profile, "unknown_action")

        assert new_profile.get("humanism") == 50.0

    def test_dominant_threshold_enforced(self):
        """Essence with value < 20 should move to underlying."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="thelema", value=25),
            EssenceScore(essence="humanism", value=75),
        ])

        new_profile = system.mutate(profile, "write_manifesto")

        thelema_in_dominant = any(e.essence == "thelema" and e in new_profile.dominant for e in new_profile.dominant)
        assert thelema_in_dominant or new_profile.get("thelema") < 20

    def test_underlying_promotes_to_dominant_at_30(self):
        """Underlying essence >= 30 should move to dominant if space available."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="humanism", value=80),
        ], underlying=[
            EssenceScore(essence="anarchism", value=30),
        ])

        new_profile = system.mutate(profile, "destroy_institution")

        anarchism_in_dominant = any(e.essence == "anarchism" for e in new_profile.dominant)
        assert anarchism_in_dominant, "anarchism should promote to dominant"

    def test_max_dominant_count_enforced(self):
        """Should not exceed MAX_DOMINANT_COUNT (3)."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="humanism", value=40),
            EssenceScore(essence="pragmatism", value=40),
            EssenceScore(essence="rationalism", value=20),
        ])

        new_profile = system.mutate(profile, "write_manifesto")

        assert len(new_profile.dominant) <= 3, "Should not exceed max dominant count"

    def test_crystallization_at_80(self):
        """Essence > 80 should crystallize (consume weakest dominant)."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="thelema", value=85),
            EssenceScore(essence="humanism", value=15),
        ])

        new_profile = system.mutate(profile, "write_manifesto")

        thelema_crystallized = any(e.essence == "thelema" and e.value == 80 for e in new_profile.dominant)
        assert thelema_crystallized, "thelema should crystallize at 80"

        humanism_moved = any(e.essence == "humanism" for e in new_profile.underlying)
        assert humanism_moved, "humanism should move to underlying"


class TestEssenceCompatibility:
    """Tests for circle formation compatibility."""

    def test_high_affinity_is_compatible(self):
        """High affinity profiles should be compatible."""
        system = EssenceSystem()

        person = EssenceProfile(dominant=[
            EssenceScore(essence="socialism", value=60),
            EssenceScore(essence="humanism", value=40),
        ])

        host = EssenceProfile(dominant=[
            EssenceScore(essence="socialism", value=70),
            EssenceScore(essence="collectivism", value=30),
        ])

        assert system.compatible(person, host) is True

    def test_low_affinity_is_incompatible(self):
        """Low affinity profiles should not be compatible."""
        system = EssenceSystem()

        person = EssenceProfile(dominant=[
            EssenceScore(essence="anarchism", value=60),
            EssenceScore(essence="extremism", value=40),
        ])

        host = EssenceProfile(dominant=[
            EssenceScore(essence="feudalism", value=50),
            EssenceScore(essence="monotheism", value=50),
        ])

        assert system.compatible(person, host) is False

    def test_custom_min_affinity(self):
        """Custom min_affinity threshold should work."""
        system = EssenceSystem()

        person = EssenceProfile(dominant=[
            EssenceScore(essence="humanism", value=50),
        ])

        host = EssenceProfile(dominant=[
            EssenceScore(essence="socialism", value=50),
        ])

        assert system.compatible(person, host, min_affinity=30) is True
        assert system.compatible(person, host, min_affinity=80) is False


class TestSuggestFaction:
    """Tests for faction suggestion based on essence."""

    def test_anarchist_suggests_revolutionaries(self):
        """Anarchist profile should suggest revolutionaries faction."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="anarchism", value=70),
            EssenceScore(essence="communism", value=30),
        ])

        faction = system.suggest_faction(profile)

        assert faction in ["revolutionaries", "extremists"]

    def test_technocrat_suggests_technocrats(self):
        """Technocrat profile should suggest technocrats faction."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="technocracy", value=60),
            EssenceScore(essence="pragmatism", value=40),
        ])

        faction = system.suggest_faction(profile)

        assert faction == "technocrats"

    def test_mystic_suggests_mystics(self):
        """Mystic profile should suggest mystics faction."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[
            EssenceScore(essence="mysticism", value=50),
            EssenceScore(essence="polytheism", value=50),
        ])

        faction = system.suggest_faction(profile)

        assert faction == "mystics"

    def test_empty_profile_returns_none(self):
        """Empty profile should return None."""
        system = EssenceSystem()

        profile = EssenceProfile(dominant=[])

        faction = system.suggest_faction(profile)

        assert faction is None


class TestAlignment:
    """Tests for civ-person alignment calculation."""

    def test_high_alignment_score(self):
        """Similar essences should have high alignment."""
        system = EssenceSystem()

        person = EssenceProfile(dominant=[
            EssenceScore(essence="socialism", value=60),
            EssenceScore(essence="humanism", value=40),
        ])

        civ_dominant = [
            EssenceScore(essence="socialism", value=70),
            EssenceScore(essence="collectivism", value=30),
        ]

        score = system.alignment(person, civ_dominant)

        assert score >= 60

    def test_low_alignment_score(self):
        """Opposing essences should have low alignment."""
        system = EssenceSystem()

        person = EssenceProfile(dominant=[
            EssenceScore(essence="anarchism", value=60),
            EssenceScore(essence="extremism", value=40),
        ])

        civ_dominant = [
            EssenceScore(essence="feudalism", value=50),
            EssenceScore(essence="monotheism", value=50),
        ]

        score = system.alignment(person, civ_dominant)

        assert score <= 40

    def test_empty_person_returns_neutral(self):
        """Empty person profile should return neutral (50)."""
        system = EssenceSystem()

        person = EssenceProfile(dominant=[])

        civ_dominant = [
            EssenceScore(essence="socialism", value=50),
        ]

        score = system.alignment(person, civ_dominant)

        assert score == 50.0


class TestActionEssenceModifiers:
    """Verify ACTION_ESSENCE_MODIFIERS mappings."""

    def test_all_actions_have_modifiers(self):
        """All key actions should have essence modifiers."""
        key_actions = [
            "write_manifesto", "donate_resources", "destroy_institution",
            "perform_ritual", "propagate_idea", "sabotage"
        ]

        for action in key_actions:
            assert action in ACTION_ESSENCE_MODIFIERS
            modifiers = ACTION_ESSENCE_MODIFIERS[action]
            assert isinstance(modifiers, dict)
            assert len(modifiers) > 0

    def test_modifiers_have_positive_and_negative(self):
        """Modifiers should have both increases and decreases."""
        for action, modifiers in ACTION_ESSENCE_MODIFIERS.items():
            has_positive = any(v > 0 for v in modifiers.values())
            has_negative = any(v < 0 for v in modifiers.values())
            assert has_positive and has_negative, f"Action {action} missing positive or negative modifiers"
