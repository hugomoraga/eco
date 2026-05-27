"""
game_core.shared.types - Shared types between game_core and adapter_core.

These are pure data types/enums that don't depend on game_core internals.
Moved here to break circular dependencies in hexagonal architecture.
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, Field


class ActionResult(BaseModel):
    """Unified action result used by Human, AI, and NPC engines."""

    action: str = ""
    success: bool
    message: str
    state_delta: dict = Field(default_factory=dict)
    new_entities: list[str] = Field(default_factory=list)
    consumed_resources: dict[str, float] = Field(default_factory=dict)
    tags_created: list[str] = Field(default_factory=list)
    social_cost: float = 0.0
    pressure_change: float = 0.0
    legitimacy_change: float = 0.0
    resources_change: float = 0.0
    damage_to_player: float = 0.0
    circles_affected: int = 0
    factions_affected: int = 0
    target_id: str | None = None


class AutoplayMode(StrEnum):
    MANUAL = "manual"
    SUGGEST = "suggest"
    AUTOPLAY = "autoplay"
    DIRECTOR = "director"
    REPLAY = "replay"


class Goal(BaseModel):
    id: str
    priority: float = Field(ge=0, le=100)
    strategy: list[str] = Field(default_factory=list)
    target_id: str | None = None


class PlayerStyle(BaseModel):
    id: str
    name: str
    prioritize_weights: dict[str, float] = Field(default_factory=dict)
    action_bias: dict[str, float] = Field(default_factory=dict)


class AutoplayDecision(BaseModel):
    turn: int
    selected_action: str
    target: str | None = None
    score: float
    reason: str = ""
    alternatives: list[dict] = Field(default_factory=list)


class AdaptiveRule(BaseModel):
    id: str
    condition: dict
    action: dict


PLAYER_STYLES: ClassVar[dict[str, PlayerStyle]] = {
    "preservationist": PlayerStyle(
        id="preservationist",
        name="Preservationist",
        prioritize_weights={"clarity": 30, "stability": 20, "continuity": 15},
        action_bias={},
    ),
    "revolutionary": PlayerStyle(
        id="revolutionary",
        name="Revolutionary",
        prioritize_weights={"spread": 30, "destabilization": 20, "radicalization": 15},
        action_bias={},
    ),
    "manipulator": PlayerStyle(
        id="manipulator",
        name="Manipulator",
        prioritize_weights={"shadow": 30, "infiltration": 25, "institutional_capture": 15},
        action_bias={},
    ),
    "mystic": PlayerStyle(
        id="mystic",
        name="Mystic",
        prioritize_weights={"symbolism": 25, "rituals": 25, "cultural_influence": 20},
        action_bias={},
    ),
    "technocrat": PlayerStyle(
        id="technocrat",
        name="Technocrat",
        prioritize_weights={"infrastructure": 25, "coordination": 25, "stability": 20},
        action_bias={},
    ),
}


ADAPTIVE_RULES: list[AdaptiveRule] = [
    AdaptiveRule(
        id="survive_repression",
        condition={"repression_level": "> 60", "influence": "< 40"},
        action={"prioritize_survival": "+= 20"},
    ),
    AdaptiveRule(
        id="repair_doctrine",
        condition={"doctrine_fragmenting": True, "clarity": "< 50"},
        action={"prioritize_doctrinal_repair": "+= 15"},
    ),
    AdaptiveRule(
        id="stabilize_collapse",
        condition={"civilization_health": "< 40"},
        action={"prioritize_stability": "+= 25"},
    ),
    AdaptiveRule(
        id="defend_faction",
        condition={"faction_pressure": "> 70"},
        action={"prioritize_defense": "+= 10"},
    ),
    AdaptiveRule(
        id="exploit_instability",
        condition={"unrest": "> 70", "opposing_faction_strength": "< 50"},
        action={"prioritize_expansion": "+= 15"},
    ),
    AdaptiveRule(
        id="preserve_legacy",
        condition={"host_age": "> 55"},
        action={"prioritize_memory": "+= 20", "increase_transfer_preparation": True},
    ),
]
