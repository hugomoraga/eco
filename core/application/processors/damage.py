"""Damage system for NPC-to-player and player-to-NPC damage."""

from __future__ import annotations

from dataclasses import dataclass

from adapters.autoplayer.actions import ACTION_DAMAGE_MAP


@dataclass
class DamageResult:
    damage: float
    is_critical: bool
    target_name: str
    narrative: str


def calculate_damage(
    action_name: str,
    attacker_influence: float,
    defender_influence: float = 0,
    defender_circle_count: int = 0,
) -> tuple[float, bool]:
    """
    Calculate damage based on action and attacker stats.

    Returns: (damage, is_critical)

    Algorithm:
    1. Base damage from ACTION_DAMAGE_MAP
    2. Mod +30% per 100 influence of attacker
    3. 10% critical chance if influence > 50
    4. Defense reduction: -10% per allied circle (max -30%)
    """
    base_damage = ACTION_DAMAGE_MAP.get(action_name, 0.0)
    if base_damage == 0:
        return 0.0, False

    influence_mod = (attacker_influence / 100) * 0.3
    final_damage = base_damage * (1 + influence_mod)

    is_critical = attacker_influence > 50 and _roll_critical()
    if is_critical:
        final_damage *= 2

    if defender_circle_count > 0:
        defense_reduction = min(0.3, defender_circle_count * 0.1)
        final_damage *= 1 - defense_reduction

    if defender_influence > 0:
        defense_bonus = (defender_influence / 100) * 0.2
        final_damage *= 1 - defense_bonus

    return min(final_damage, 100), is_critical


def _roll_critical() -> bool:
    """Roll for critical hit."""
    import random

    return random.random() < 0.1


def get_damage_narrative(action_name: str, is_critical: bool) -> str:
    """Get a narrative template for damage based on action."""
    narratives = {
        "sabotage": "sabotaged infrastructure",
        "spread_rumor": "spread damaging rumors",
        "negotiate": "exploited in negotiations",
        "ritualize": "drained through ritual",
        "ritual": "overwhelmed by ritual energy",
        "talk": "verbally attacked",
    }
    base = narratives.get(action_name, "damaged")
    if is_critical:
        return f"critically {base}"
    return base


def can_deal_damage(action_name: str) -> bool:
    """Check if an action can deal damage."""
    return action_name in ACTION_DAMAGE_MAP


def apply_damage_to_npc(npc, damage: float) -> bool:
    """
    Apply damage to an NPC.

    Returns True if the NPC died (vitality <= 0).
    """
    npc.vitality = max(0, npc.vitality - damage)
    return npc.vitality <= 0


def should_deal_damage_to_player(action_name: str) -> bool:
    """Determine if this action can target the player (Echo)."""
    target_actions = {"sabotage", "spread_rumor"}
    return action_name in target_actions
