"""
game_core.shared.actions - Shared action constants and metadata.

This module is the single source of truth for all action-related data:
- Action names
- Action damage values
- NPC archetype weights
- Other action metadata

All engines (Human, AI, NPC) should import from here.
"""
from __future__ import annotations

from typing import ClassVar


# ─── All Available Actions ──────────────────────────────────────────────────

ALL_AVAILABLE_ACTIONS = [
    "found_circle",
    "join_circle",
    "leave_circle",
    "propagate_idea",
    "write_manifesto",
    "sabotage",
    "ritualize",
    "talk",
    "spread_rumor",
    "recruit_follower",
    "negotiate",
    "ritual",
]

ECHO_ACTIONS = [
    "found_circle",
    "join_circle",
    "leave_circle",
    "propagate_idea",
    "write_manifesto",
    "sabotage",
    "ritualize",
    "talk",
    "spread_rumor",
    "recruit_follower",
    "negotiate",
    "ritual",
]

NPC_ACTIONS = [
    "propagate_idea",
    "write_manifesto",
    "sabotage",
    "ritualize",
    "talk",
    "spread_rumor",
    "recruit_follower",
    "negotiate",
    "ritual",
]


# ─── Action Damage Map ────────────────────────────────────────────────────────

ACTION_DAMAGE_MAP: ClassVar[dict[str, float]] = {
    "propagate_idea": 3.0,
    "sabotage": 20.0,
    "ritualize": 5.0,
    "talk": 2.0,
    "spread_rumor": 8.0,
    "ritual": 12.0,
}


# ─── NPC Archetype Weights ────────────────────────────────────────────────────

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
