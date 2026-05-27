"""
essence_system.py — Essence mechanics for mutation, compatibility, and faction suggestion.

Implements spec-47 mechanics:
- Essence mutation based on actions
- Circle formation compatibility
- Faction suggestion based on essence profile
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.domain.entities.ideas import EssenceProfile, EssenceScore

if TYPE_CHECKING:
    from core.domain.entities.person import Person
    from core.domain.entities.host import Host
    from core.domain.entities.echo import Echo
    from core.domain.entities.circle import Circle
    from core.domain.entities.faction import Faction


ACTION_ESSENCE_MODIFIERS: dict[str, dict[str, float]] = {
    "write_manifesto": {"thelema": 5, "individualism": 3, "monoteism": -2, "collectivism": -2},
    "donate_resources": {"socialism": 5, "collectivism": 4, "capitalism": -3, "individualism": -2},
    "destroy_institution": {"anarchism": 7, "communism": 4, "feudalism": -5, "technocracy": -3},
    "perform_ritual": {"mysticism": 5, "spirituality": 3, "rationalism": -2, "atheism": -2},
    "propagate_idea": {"thelema": 3, "individualism": 2, "socialism": 2, "monoteism": -1},
    "sabotage": {"anarchism": 5, "extremism": 4, "pragmatism": -2, "moderation": -3},
    "negotiate": {"pragmatism": 4, "moderation": 3, "extremism": -2, "dogmatism": -2},
    "spread_rumor": {"pragmatism": 3, "absurdism": 2, "rationalism": -1, "stoicism": -1},
    "recruit_follower": {"socialism": 3, "collectivism": 3, "individualism": -2, "anarchism": -1},
    "ritualize": {"mysticism": 4, "polytheism": 3, "atheism": -2, "rationalism": -2},
    "join_circle": {"collectivism": 2, "socialism": 2, "individualism": -1},
    "leave_circle": {"individualism": 3, "anarchism": 2, "collectivism": -2},
    "found_circle": {"leadership": 5, "socialism": 3, "anarchism": -2},
    "talk": {"pragmatism": 2, "humanism": 2, "rationalism": 1, "extremism": -1},
}


MIN_DOMINANT_THRESHOLD = 20.0
MIN_UNDERLYING_FOR_DOMINANT = 30.0
MAX_DOMINANT_COUNT = 3
CRYSTALLIZATION_THRESHOLD = 80.0


@dataclass
class EssenceMutation:
    essence: str
    delta: float


class EssenceSystem:
    """
    Core essence mechanics.

    Usage:
        system = EssenceSystem()

        # Mutate essence based on action
        new_profile = system.mutate(entity.essence_profile, "write_manifesto")

        # Check if person is compatible with host for circle
        if system.compatible(person, host):
            circle.add_member(person)

        # Suggest faction based on essence
        faction = system.suggest_faction(entity)
    """

    def mutate(self, profile: EssenceProfile, action: str) -> EssenceProfile:
        """
        Apply action-based essence mutation to a profile.

        Rules (spec-47.4.2):
        - Only dominant can increase
        - If dominant > 80, can crystallize (consume another)
        - Underlying >= 30 can become dominant if space available
        - Dominant < 20 moves to underlying
        - Maximum 1 mutation per tick per entity

        Args:
            profile: Current essence profile
            action: Action name from ACTION_ESSENCE_MODIFIERS

        Returns:
            New EssenceProfile with mutations applied
        """
        modifiers = ACTION_ESSENCE_MODIFIERS.get(action, {})
        if not modifiers:
            return profile

        new_dominant = [s.model_copy() for s in profile.dominant]
        new_underlying = [s.model_copy() for s in profile.underlying]

        for essence, delta in modifiers.items():
            if delta <= 0:
                self._decrease_essence(new_dominant, new_underlying, essence, abs(delta))
            else:
                self._increase_essence(new_dominant, new_underlying, essence, delta)

        self._normalize_profile(new_dominant, new_underlying)
        self._apply_threshold_rules(new_dominant, new_underlying)

        return EssenceProfile(dominant=new_dominant, underlying=new_underlying)

    def _decrease_essence(
        self, dominant: list[EssenceScore], underlying: list[EssenceScore], essence: str, amount: float
    ) -> None:
        for s in dominant:
            if s.essence == essence:
                s.value = max(0, s.value - amount)
                if s.value < MIN_DOMINANT_THRESHOLD:
                    self._move_to_underlying(dominant, underlying, essence)
                return

        for s in underlying:
            if s.essence == essence:
                s.value = max(0, s.value - amount)
                return

    def _increase_essence(
        self, dominant: list[EssenceScore], underlying: list[EssenceScore], essence: str, amount: float
    ) -> None:
        for s in dominant:
            if s.essence == essence:
                s.value = min(100, s.value + amount)
                if s.value > CRYSTALLIZATION_THRESHOLD and len(dominant) > 1:
                    self._crystallize(dominant, underlying, essence)
                return

        for s in underlying:
            if s.essence == essence:
                s.value = min(100, s.value + amount)
                if s.value >= MIN_UNDERLYING_FOR_DOMINANT and len(dominant) < MAX_DOMINANT_COUNT:
                    self._move_to_dominant(dominant, underlying, essence)
                return

        if len(dominant) < MAX_DOMINANT_COUNT:
            dominant.append(EssenceScore(essence=essence, value=amount))
        else:
            for s in underlying:
                if s.essence == essence:
                    s.value = min(100, s.value + amount)
                    return
            underlying.append(EssenceScore(essence=essence, value=amount))

    def _move_to_underlying(self, dominant: list[EssenceScore], underlying: list[EssenceScore], essence: str) -> None:
        for i, s in enumerate(dominant):
            if s.essence == essence:
                dominant.pop(i)
                underlying.append(EssenceScore(essence=essence, value=s.value))
                break

    def _move_to_dominant(self, dominant: list[EssenceScore], underlying: list[EssenceScore], essence: str) -> None:
        for i, s in enumerate(underlying):
            if s.essence == essence:
                underlying.pop(i)
                dominant.append(s)
                break

    def _crystallize(self, dominant: list[EssenceScore], underlying: list[EssenceScore], essence: str) -> None:
        weakest = min(dominant, key=lambda s: s.value)
        if weakest.essence != essence:
            self._move_to_underlying(dominant, underlying, weakest.essence)
            for s in dominant:
                if s.essence == essence:
                    s.value = CRYSTALLIZATION_THRESHOLD
                    break

    def _normalize_profile(self, dominant: list[EssenceScore], underlying: list[EssenceScore]) -> None:
        total = sum(s.value for s in dominant)
        if total > 100:
            factor = 100.0 / total
            for s in dominant:
                s.value *= factor

    def _apply_threshold_rules(self, dominant: list[EssenceScore], underlying: list[EssenceScore]) -> None:
        for s in dominant[:]:
            if s.value < MIN_DOMINANT_THRESHOLD:
                self._move_to_underlying(dominant, underlying, s.essence)

        for s in underlying[:]:
            if s.value >= MIN_UNDERLYING_FOR_DOMINANT and len(dominant) < MAX_DOMINANT_COUNT:
                self._move_to_dominant(dominant, underlying, s.essence)

    def compatible(self, person: EssenceProfile, host: EssenceProfile, min_affinity: float = 60.0) -> bool:
        """
        Check if person is compatible with host for circle formation.

        Spec-47.5.2:
        - Person needs affinity >= 60 with host to be invited

        Args:
            person: Person's essence profile
            host: Host's essence profile (circle founder)
            min_affinity: Minimum affinity score to be compatible

        Returns:
            True if compatible for circle formation
        """
        from core.domain.registries.essence_registry import EssenceRegistry

        person_dom = {e.essence: e.value for e in person.dominant}
        host_dom = {e.essence: e.value for e in host.dominant}

        total_affinity = 0.0
        total_weight = 0.0

        for p_ess, p_val in person_dom.items():
            best_match = 0.0
            for h_ess, h_val in host_dom.items():
                if p_ess == h_ess:
                    best_match = 100.0
                    break
                affinity = EssenceRegistry.get_affinity(p_ess, h_ess)
                best_match = max(best_match, affinity)
            total_affinity += best_match * p_val
            total_weight += p_val

        if total_weight == 0:
            return True

        weighted_affinity = total_affinity / total_weight
        return weighted_affinity >= min_affinity

    def suggest_faction(self, entity: EssenceProfile) -> str | None:
        """
        Suggest a faction based on essence profile.

        Spec-47.5.3:
        - Similar essences → allied factions
        - HIGH_TENSION/INCOMPATIBLE → adversarial factions

        Returns faction key or None if no clear match.
        """
        from core.domain.registries.essence_registry import EssenceRegistry

        if not entity.dominant:
            return None

        dominant_essences = [e.essence for e in entity.dominant]

        faction_scores: dict[str, float] = {
            "traditionalists": 0.0,
            "revolutionaries": 0.0,
            "moderates": 0.0,
            "extremists": 0.0,
            "technocrats": 0.0,
            "mystics": 0.0,
        }

        essence_to_faction: dict[str, list[str]] = {
            "feudalism": ["traditionalists"],
            "monotheism": ["traditionalists"],
            "stoicism": ["traditionalists"],
            "anarchism": ["revolutionaries", "extremists"],
            "communism": ["revolutionaries"],
            "socialism": ["revolutionaries", "moderates"],
            "capitalism": ["moderates", "technocrats"],
            "technocracy": ["technocrats"],
            "pragmatism": ["moderates"],
            "mysticism": ["mystics"],
            "polytheism": ["mystics"],
            "animism": ["mystics"],
            "absurdism": ["extremists"],
            "nihilism": ["extremists"],
            "thelema": ["extremists"],
            "rationalism": ["technocrats", "moderates"],
            "humanism": ["moderates"],
        }

        for essence in dominant_essences:
            factions = essence_to_faction.get(essence, [])
            value = next((e.value for e in entity.dominant if e.essence == essence), 0)
            for faction in factions:
                faction_scores[faction] += value

        if not any(faction_scores.values()):
            return None

        return max(faction_scores, key=faction_scores.get)

    def alignment(self, person: EssenceProfile, civ_dominant: list[EssenceScore]) -> float:
        """
        Calculate alignment score between person and civilization.

        Spec-47.5.1:
        - >= 70: aligned → loyalty bonus
        - <= 40: disident → resistance
        - 40-70: neutral

        Args:
            person: Person's essence profile
            civ_dominant: Civilization's dominant essences

        Returns:
            Alignment score 0-100
        """
        from core.domain.registries.essence_registry import EssenceRegistry

        score = 0.0
        total_weight = 0.0

        for pd in person.dominant:
            best_match = 0.0
            for cd in civ_dominant:
                if pd.essence == cd.essence:
                    best_match = 100.0
                    break
                affinity = EssenceRegistry.get_affinity(pd.essence, cd.essence)
                best_match = max(best_match, affinity)
            score += best_match * pd.value
            total_weight += pd.value

        if total_weight == 0:
            return 50.0

        return min(100.0, max(0.0, score / total_weight))
