"""NPC Engine - AutoplayEngine for individual NPCs with archetype-based weights."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from game_core.systems.random import SeededRandom

if TYPE_CHECKING:
    from game_core.domain.entities import Person, World


ARCHETYPE_WEIGHTS: ClassVar[dict[str, dict[str, float]]] = {
    "leader": {
        "doctrinal_clarity": 0.05,
        "memetic_spread": 0.05,
        "institutional_control": 0.20,
        "ideological_stability": 0.05,
        "survival_probability": 0.05,
        "material_security": 0.10,
        "adaptability": -0.05,
        "narrative_risk": 0.05,
        "historical_impact": 0.15,
    },
    "mystic": {
        "doctrinal_clarity": 0.10,
        "memetic_spread": 0.20,
        "institutional_control": -0.05,
        "ideological_stability": 0.15,
        "survival_probability": 0.05,
        "material_security": -0.05,
        "adaptability": 0.10,
        "narrative_risk": 0.05,
        "historical_impact": 0.10,
    },
    "warrior": {
        "doctrinal_clarity": 0.05,
        "memetic_spread": 0.00,
        "institutional_control": 0.10,
        "ideological_stability": 0.05,
        "survival_probability": 0.25,
        "material_security": 0.20,
        "adaptability": 0.00,
        "narrative_risk": 0.10,
        "historical_impact": -0.05,
    },
    "scientist": {
        "doctrinal_clarity": 0.20,
        "memetic_spread": 0.05,
        "institutional_control": 0.05,
        "ideological_stability": 0.10,
        "survival_probability": 0.05,
        "material_security": 0.10,
        "adaptability": 0.25,
        "narrative_risk": -0.10,
        "historical_impact": 0.05,
    },
    "propagator": {
        "doctrinal_clarity": 0.00,
        "memetic_spread": 0.30,
        "institutional_control": 0.00,
        "ideological_stability": 0.05,
        "survival_probability": 0.05,
        "material_security": 0.00,
        "adaptability": 0.10,
        "narrative_risk": 0.10,
        "historical_impact": 0.15,
    },
    "cult_leader": {
        "doctrinal_clarity": 0.15,
        "memetic_spread": 0.10,
        "institutional_control": 0.25,
        "ideological_stability": 0.10,
        "survival_probability": 0.05,
        "material_security": 0.05,
        "adaptability": 0.05,
        "narrative_risk": 0.05,
        "historical_impact": 0.10,
    },
    "reformer": {
        "doctrinal_clarity": 0.05,
        "memetic_spread": 0.15,
        "institutional_control": -0.10,
        "ideological_stability": 0.15,
        "survival_probability": 0.05,
        "material_security": 0.05,
        "adaptability": 0.20,
        "narrative_risk": 0.05,
        "historical_impact": 0.15,
    },
    "dissident": {
        "doctrinal_clarity": -0.05,
        "memetic_spread": 0.15,
        "institutional_control": -0.15,
        "ideological_stability": 0.05,
        "survival_probability": 0.20,
        "material_security": 0.05,
        "adaptability": 0.15,
        "narrative_risk": 0.20,
        "historical_impact": 0.10,
    },
}


def get_archetype_for_npc(npc: Person) -> str:
    """Get the archetype string from a Person's archetype field."""
    if not npc.archetype:
        return "leader"
    return npc.archetype.split(",")[0].strip().lower()


class NPCDecision:
    def __init__(
        self,
        npc_id: str,
        npc_name: str,
        action: str,
        score: float,
        reason: str = "",
        damage_dealt: float = 0.0,
        target_id: str | None = None,
    ):
        self.npc_id = npc_id
        self.npc_name = npc_name
        self.action = action
        self.score = score
        self.reason = reason
        self.damage_dealt = damage_dealt
        self.target_id = target_id

    def to_dict(self) -> dict:
        return {
            "npc_id": self.npc_id,
            "npc_name": self.npc_name,
            "action": self.action,
            "score": self.score,
            "reason": self.reason,
            "damage_dealt": self.damage_dealt,
            "target_id": self.target_id,
        }


class NPCEngine:
    def __init__(self, seed: int = 42):
        self.rng = SeededRandom.get_instance(seed)

    def evaluate_npc_state(self, npc: Person, world: World) -> dict[str, float]:
        """Evaluate NPC's current state - simpler than player echo evaluation."""
        metrics = {}

        loyalty = npc.loyalty
        metrics["loyalty_score"] = loyalty

        influence = npc.influence
        metrics["social_influence"] = min(influence, 100)

        vitality = npc.vitality
        metrics["vitality_score"] = vitality

        coherence = npc.coherence
        metrics["coherence_score"] = coherence

        if npc.essence_profile:
            dominant_essences = npc.essence_profile.dominant_essences(min_value=20)
            metrics["essence_clarity"] = min(len(dominant_essences) * 30, 100)
        else:
            metrics["essence_clarity"] = 30

        metrics["survival_probability"] = vitality
        metrics["social_presence"] = influence

        return metrics

    def score_action_for_npc(
        self,
        action_name: str,
        npc: Person,
        world: World,
        archetype: str,
    ) -> float:
        """Score an action for a specific NPC based on archetype."""
        base_score = 50.0

        archetype_mods = ARCHETYPE_WEIGHTS.get(archetype, ARCHETYPE_WEIGHTS["leader"])

        if action_name == "found_circle":
            base_score += archetype_mods.get("institutional_control", 0) * 50
            base_score += archetype_mods.get("memetic_spread", 0) * 30

        elif action_name == "propagate_idea":
            base_score += archetype_mods.get("memetic_spread", 0) * 60

        elif action_name == "spread_rumor":
            base_score += archetype_mods.get("memetic_spread", 0) * 40
            base_score += archetype_mods.get("narrative_risk", 0) * 20

        elif action_name == "ritualize":
            base_score += archetype_mods.get("doctrinal_clarity", 0) * 50
            base_score += archetype_mods.get("ideological_stability", 0) * 30

        elif action_name == "ritual":
            base_score += archetype_mods.get("doctrinal_clarity", 0) * 40
            base_score += archetype_mods.get("historical_impact", 0) * 30
            base_score -= 20

        elif action_name == "write_manifesto":
            base_score += archetype_mods.get("doctrinal_clarity", 0) * 40
            base_score += archetype_mods.get("historical_impact", 0) * 40

        elif action_name == "sabotage":
            base_score += archetype_mods.get("survival_probability", 0) * 30
            base_score += archetype_mods.get("narrative_risk", 0) * 30
            base_score -= 10

        elif action_name == "recruit_follower":
            base_score += archetype_mods.get("institutional_control", 0) * 50
            base_score += archetype_mods.get("social_influence", 0) * 20

        elif action_name == "negotiate":
            base_score += archetype_mods.get("material_security", 0) * 40
            base_score += archetype_mods.get("adaptability", 0) * 30

        elif action_name == "talk":
            base_score += archetype_mods.get("social_influence", 0) * 30
            base_score += 20

        elif action_name == "join_circle":
            base_score += archetype_mods.get("institutional_control", 0) * 30
            base_score += archetype_mods.get("survival_probability", 0) * 20

        elif action_name == "leave_circle":
            base_score += archetype_mods.get("survival_probability", 0) * 40
            base_score -= 20

        if npc.action_history:
            repeats = npc.action_history.count(action_name)
            base_score *= max(0.5, 1.0 - (repeats * 0.1))

        return max(0, min(100, base_score))

    def select_action_for_npc(
        self,
        npc: Person,
        world: World,
        available_actions: list[str],
    ) -> NPCDecision:
        """Select the best action for an NPC."""
        archetype = get_archetype_for_npc(npc)
        action_scores = {}

        for action in available_actions:
            action_scores[action] = self.score_action_for_npc(action, npc, world, archetype)

        best_action = max(action_scores, key=lambda a: (action_scores[a], self.rng.random()))
        best_score = action_scores[best_action]

        return NPCDecision(
            npc_id=npc.id,
            npc_name=npc.name or f"NPC-{npc.id[:8]}",
            action=best_action,
            score=best_score,
            reason=f"Selected based on {archetype} archetype",
        )


def get_top_npcs(world: World, count: int = 5) -> list:
    """Get the top NPCs by influence."""
    npcs = [p for p in world.persons if p.type == "npc" and p.influence > 0]
    npcs.sort(key=lambda p: p.influence, reverse=True)
    return npcs[:count]


def get_random_npcs(world: World, count: int = 4, exclude_ids: list[str] = None) -> list:
    """Get random NPCs, optionally excluding some IDs."""
    rng = SeededRandom.get_instance()
    npcs = [p for p in world.persons if p.type == "npc" and p.id not in (exclude_ids or [])]
    rng.shuffle(npcs)
    return npcs[:count]