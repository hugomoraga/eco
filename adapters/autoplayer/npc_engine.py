"""
adapter_core.autoplayer.npc_engine - NPC AI decision making.

This module contains the AI logic for individual NPC decisions.
NPCs use archetype-based scoring to select actions.
Moved here from core.autoplayer as part of hexagonal architecture refactor.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.application.processors.random import SeededRandom
from adapters.autoplayer.actions import ARCHETYPE_WEIGHTS, NPC_ACTIONS
from adapters.autoplayer.types import ActionResult
from infra.logging import get_logger

if TYPE_CHECKING:
    from core.domain import Person, World

log = get_logger(__name__)


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

        action_history = getattr(npc, 'action_history', None)
        if action_history:
            repeats = action_history.count(action_name)
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

        log.debug("npc_decision", npc_id=npc.id, npc_name=npc.name or f"NPC-{npc.id[:8]}", archetype=archetype,
                   action_scores=action_scores, selected_action=best_action, selected_score=best_score)

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


class NPCActionExecutor:
    """Executes NPC decisions on the world state.

    NPCs affect the world through their actions - modifying pressure,
    legitimacy, resources, and potentially damaging the player.
    """

    def __init__(self, seed: int = 42):
        self.rng = SeededRandom.get_instance(seed)
        self.engine = NPCEngine(seed=seed)

    def execute_action(
        self,
        npc: Person,
        action_name: str,
        world: World,
        world_tick: int = 0,
    ) -> ActionResult:
        """Execute an NPC action and return the result."""
        npc_name = npc.name or f"NPC-{npc.id[:8]}"

        handler = getattr(self, f"_execute_{action_name}", None)
        if handler is None:
            return ActionResult(
                npc_id=npc.id,
                npc_name=npc_name,
                action=action_name,
                success=False,
                message=f"Unknown action: {action_name}",
            )

        return handler(npc, world, world_tick)

    def _apply_world_changes(
        self,
        npc: Person,
        world: World,
        pressure_delta: float,
        legitimacy_delta: float,
        resources_delta: float = 0.0,
        damage_to_player: float = 0.0,
        circles_affected: int = 0,
        factions_affected: int = 0,
        message: str = "",
        success: bool = True,
        target_id: str | None = None,
    ) -> ActionResult:
        """Apply world state changes and return result."""
        old_pressure = world.pressure
        old_legitimacy = world.legitimacy
        old_resources = world.resources_global

        world.pressure = max(0, min(100, world.pressure + pressure_delta))
        world.legitimacy = max(0, min(100, world.legitimacy + legitimacy_delta))
        world.resources_global = max(0, world.resources_global + resources_delta)

        actual_pressure_change = world.pressure - old_pressure
        actual_legitimacy_change = world.legitimacy - old_legitimacy
        actual_resources_change = world.resources_global - old_resources

        log.info("npc_action_executed",
                 npc_id=npc.id,
                 npc_name=npc.name or f"NPC-{npc.id[:8]}",
                 action=getattr(self, 'current_action', 'unknown'),
                 success=success,
                 message=message,
                 pressure_change=actual_pressure_change,
                 legitimacy_change=actual_legitimacy_change,
                 resources_change=actual_resources_change)

        return ActionResult(
            action=getattr(self, 'current_action', 'unknown'),
            success=success,
            message=message,
            pressure_change=actual_pressure_change,
            legitimacy_change=actual_legitimacy_change,
            resources_change=actual_resources_change,
            damage_to_player=damage_to_player,
            circles_affected=circles_affected,
            factions_affected=factions_affected,
            target_id=target_id,
        )

    def _execute_propagate_idea(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC propagates ideas to circles/factions."""
        self.current_action = "propagate_idea"

        targets = list(world.circles) + list(world.factions)
        if not targets:
            return ActionResult(
                action="propagate_idea",
                success=False,
                message="No targets to propagate ideas",
            )

        target = self.rng.choice(targets)
        circles_hit = 0
        factions_hit = 0

        if hasattr(target, 'member_ids'):
            circles_hit = 1
        elif hasattr(target, 'members'):
            factions_hit = 1

        pressure_delta = 1.0
        legitimacy_delta = -0.5

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            message=f"Propagated ideas to {target.name if hasattr(target, 'name') else 'targets'}",
            circles_affected=circles_hit,
            factions_affected=factions_hit,
            target_id=target.id if hasattr(target, 'id') else None,
        )

    def _execute_write_manifesto(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC writes a manifesto, affecting world metrics."""
        self.current_action = "write_manifesto"

        pressure_delta = 3.0
        legitimacy_delta = -1.0

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            message=f"Wrote manifesto: {npc.name or 'NPC'} articulates their vision",
        )

    def _execute_sabotage(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC sabotages, damaging player vitality."""
        self.current_action = "sabotage"

        player = world.get_active_player_person()
        damage = self.rng.uniform(5, 15) if player else 0

        if player:
            player.take_damage(damage)

        pressure_delta = 8.0
        legitimacy_delta = -5.0
        resources_delta = -5.0

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            resources_delta=resources_delta,
            damage_to_player=damage,
            message=f"Sabotage attempt by {npc.name or 'Unknown NPC'}",
            target_id=player.id if player else None,
        )

    def _execute_ritualize(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC performs ritualize action."""
        self.current_action = "ritualize"

        circles_available = [c for c in world.circles if c.status.value == "active"]
        circles_hit = 0

        if circles_available:
            target = self.rng.choice(circles_available)
            circles_hit = 1

        pressure_delta = 5.0
        legitimacy_delta = -2.0

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            circles_affected=circles_hit,
            message=f"Performed rituals" + (f" in {target.name}" if circles_hit else ""),
            target_id=target.id if circles_hit else None,
        )

    def _execute_talk(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC talks, minor social pressure effect."""
        self.current_action = "talk"

        pressure_delta = 1.0
        legitimacy_delta = -0.5

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            message=f"{npc.name or 'NPC'} engaged in conversation",
        )

    def _execute_spread_rumor(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC spreads rumors, damaging player."""
        self.current_action = "spread_rumor"

        player = world.get_active_player_person()
        damage = self.rng.uniform(3, 10) if player else 0

        if player:
            player.take_damage(damage)

        pressure_delta = 4.0
        legitimacy_delta = -2.0

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            damage_to_player=damage,
            message=f"Rumors spread by {npc.name or 'Unknown NPC'}",
            target_id=player.id if player else None,
        )

    def _execute_recruit_follower(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC recruits followers to circles."""
        self.current_action = "recruit_follower"

        circles_available = [c for c in world.circles if c.status.value == "active"]
        if not circles_available:
            return ActionResult(
                action="recruit_follower",
                success=False,
                message="No circles available for recruitment",
            )

        target = self.rng.choice(circles_available)
        pressure_delta = 2.0
        legitimacy_delta = -1.0

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            circles_affected=1,
            message=f"Recruited followers to {target.name}",
            target_id=target.id,
        )

    def _execute_negotiate(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC negotiates, gaining resources."""
        self.current_action = "negotiate"

        resources_delta = self.rng.uniform(2, 8)
        legitimacy_delta = 1.0

        return self._apply_world_changes(
            npc, world,
            pressure_delta=0,
            legitimacy_delta=legitimacy_delta,
            resources_delta=resources_delta,
            message=f"{npc.name or 'NPC'} negotiated successfully",
        )

    def _execute_ritual(self, npc: Person, world: World, world_tick: int) -> NPCActionResult:
        """NPC performs a ritual."""
        self.current_action = "ritual"

        pressure_delta = -3.0
        legitimacy_delta = 2.0
        resources_delta = 5.0

        return self._apply_world_changes(
            npc, world,
            pressure_delta=pressure_delta,
            legitimacy_delta=legitimacy_delta,
            resources_delta=resources_delta,
            message=f"{npc.name or 'NPC'} conducted a ritual ceremony",
        )


def process_npc_turn(
    npc: Person,
    world: World,
    engine: NPCEngine,
    executor: NPCActionExecutor,
    world_tick: int = 0,
) -> ActionResult | None:
    """Process a single NPC's turn - decide and execute action.

    Returns the action result if an action was taken, None if no action.
    """
    available_actions = NPC_ACTIONS
    decision = engine.select_action_for_npc(npc, world, available_actions)

    if decision.score < 30:
        return None

    return executor.execute_action(npc, decision.action, world, world_tick)
