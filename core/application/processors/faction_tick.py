from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from core.application.processors.random import SeededRandom

if TYPE_CHECKING:
    from core.domain import Faction, World


class FactionTickSystem:
    POSSIBLE_ACTIONS: ClassVar[list[str]] = [
        "recruit_npc",
        "spread_doctrine",
        "support_infrastructure",
        "radicalize_members",
    ]

    def __init__(self, seed: int = 42):
        self.rng = SeededRandom.get_instance(seed)

    def tick(self, world: World) -> list[dict]:
        results = []

        for faction in world.factions:
            result = self._evaluate_faction(faction, world)
            if result:
                results.append(result)

        return results

    def _evaluate_faction(self, faction: Faction, world: World) -> dict | None:
        goal = faction.goals[0] if faction.goals else "maintain_influence"

        scores = {}
        for action in self.POSSIBLE_ACTIONS:
            score = self._calculate_score(faction, action, goal, world)
            scores[action] = score

        best_action = max(scores, key=scores.get)
        best_score = scores[best_action]

        if best_score < 30:
            return None

        effect = self._apply_action(faction, best_action, world)

        return {
            "faction_id": faction.id,
            "faction_name": faction.name,
            "action": best_action,
            "score": best_score,
            "goal": goal,
            "effect": effect,
        }

    def _calculate_score(self, faction: Faction, action: str, goal: str, world: World) -> float:
        from core.application.processors.pressure import DerivePressureCalculator, EconomyPressure

        goal_alignment = 50.0
        available_resources = self._resource_score(faction)
        local_influence = min(faction.influence, 100)
        ideological_pressure = self._ideological_pressure(faction, world)
        behavior_modifier = self._behavior_modifier(faction, action)
        risk = self._action_risk(action)

        base_score = (
            (goal_alignment * 0.3)
            + (available_resources * 0.2)
            + (local_influence * 0.2)
            + (ideological_pressure * 0.2)
            + (behavior_modifier)
            - risk
        )

        lineage = [i.to_semantic_key() for i in faction.ideas] if hasattr(faction, "ideas") else []
        dominant_essence = getattr(faction, "essence", None)

        material = EconomyPressure.calculate_material_pressure(world.resources)
        social = EconomyPressure.calculate_social_pressure(world)
        total_pressure = DerivePressureCalculator.calculate(
            material, social, 40.0, 40.0, lineage, dominant_essence
        )

        pressure_modifier = 1.0 + (total_pressure / 100.0)
        adjusted_score = base_score * pressure_modifier

        return max(0, adjusted_score)

    def _resource_score(self, faction: Faction) -> float:
        total = sum(faction.resources.values())
        return min(total / 3, 100)

    def _ideological_pressure(self, faction: Faction, world: World) -> float:
        if not faction.ideas:
            return 30.0
        # TODO: migrate to world.get_player_echo() once all callers support it
        echo = world.get_active_echo()
        if not echo:
            return 30.0

        faction_keys = {i.to_semantic_key() for i in faction.ideas}
        echo_keys = {t.to_semantic_key() for t in echo.known_tags}
        overlap = len(faction_keys & echo_keys)
        return 30.0 + (overlap * 20.0)

    def _behavior_modifier(self, faction: Faction, action: str) -> float:
        aggression = getattr(faction, "aggression", 50)
        secrecy = getattr(faction, "secrecy", 30)
        adaptability = getattr(faction, "adaptability", 50)

        modifier = 0.0

        if action == "recruit_npc":
            modifier += 5 if aggression > 60 else 0
        elif action == "spread_doctrine":
            modifier += 5 if secrecy < 40 else 0
        elif action == "support_infrastructure":
            modifier -= 5 if aggression > 70 else 0
        elif action == "radicalize_members":
            modifier += 10 if aggression > 70 else 0

        modifier += (adaptability - 50) / 10

        return modifier

    def _action_risk(self, action: str) -> float:
        risks = {
            "recruit_npc": 20,
            "spread_doctrine": 15,
            "support_infrastructure": 25,
            "radicalize_members": 40,
        }
        return risks.get(action, 30)

    def _apply_action(self, faction: Faction, action: str, world: World) -> dict:
        effect = {"changes": []}

        if action == "recruit_npc":
            faction.members += 1
            faction.influence += 2
            effect["changes"].append("members: +1, influence: +2")

        elif action == "spread_doctrine":
            faction.influence += 5
            for res_key in faction.resources:
                faction.resources[res_key] = max(0, faction.resources[res_key] - 5)
            effect["changes"].append("influence: +5, resources: -5")

        elif action == "support_infrastructure":
            if "infrastructure" in faction.resources:
                faction.resources["infrastructure"] += 10
                effect["changes"].append("infrastructure: +10")

        elif action == "radicalize_members":
            faction.radicalization = min(100, faction.radicalization + 10)
            effect["changes"].append("radicalization: +10")

        return effect
