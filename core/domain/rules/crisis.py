from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class CrisisType(Enum):
    FOOD_SHORTAGE = "food_shortage"
    COMMUNICATION_FAILURE = "communication_failure"
    PROTEST = "protest"
    DISEASE = "disease"
    REPRESSION = "repression"
    PROSPERITY = "prosperity"
    SHORTAGE = "shortage"


@dataclass
class CrisisEffect:
    legitimacy_change: float
    pressure_change: float
    resources_change: float
    vitality_change: float


@dataclass
class Crisis:
    crisis_type: CrisisType
    title: str
    description: str
    narrative: str
    effects: CrisisEffect
    turns_remaining: int = 3


CRISIS_DATA: dict[CrisisType, dict] = {
    CrisisType.FOOD_SHORTAGE: {
        "title": "Escasez de alimentos",
        "description": "Los mercados están vacíos. El pueblo tiene hambre.",
        "narrative": "Los mercados están vacíos. El hambre azota los barrios más pobres.",
        "effects": {
            "legitimacy_change": -5.0,
            "pressure_change": 10.0,
            "resources_change": -10.0,
            "vitality_change": -5.0,
        },
    },
    CrisisType.COMMUNICATION_FAILURE: {
        "title": "Falla en las comunicaciones",
        "description": "La red de información ha dejado de funcionar.",
        "narrative": "Los mensajeros no llegan. El silencio se extiende por la ciudad.",
        "effects": {
            "legitimacy_change": -3.0,
            "pressure_change": 5.0,
            "resources_change": 0.0,
            "vitality_change": 0.0,
        },
    },
    CrisisType.PROTEST: {
        "title": "Manifestaciones en las calles",
        "description": "El pueblo sale a las calles exigiendo cambios.",
        "narrative": "Manifestantes inundan las calles. El pueblo exige respuestas.",
        "effects": {
            "legitimacy_change": 5.0,
            "pressure_change": 15.0,
            "resources_change": -5.0,
            "vitality_change": -3.0,
        },
    },
    CrisisType.DISEASE: {
        "title": "Brote de enfermedad",
        "description": "Una plaga azota la ciudad.",
        "narrative": "La enfermedad se extiende. Los hospitales están desbordados.",
        "effects": {
            "legitimacy_change": -8.0,
            "pressure_change": 8.0,
            "resources_change": -15.0,
            "vitality_change": -15.0,
        },
    },
    CrisisType.REPRESSION: {
        "title": "Represión del régimen",
        "description": "El régimen envía tropas a los distritos.",
        "narrative": "Tropas del viejo régimen patrullan las calles. La represión ha comenzado.",
        "effects": {
            "legitimacy_change": -10.0,
            "pressure_change": 20.0,
            "resources_change": -5.0,
            "vitality_change": -8.0,
        },
    },
    CrisisType.PROSPERITY: {
        "title": "Prosperidad inesperada",
        "description": "Buena cosecha y comercio fluido.",
        "narrative": "Una buena cosecha trae esperanza. El comercio fluye con fuerza.",
        "effects": {
            "legitimacy_change": 8.0,
            "pressure_change": -5.0,
            "resources_change": 15.0,
            "vitality_change": 5.0,
        },
    },
    CrisisType.SHORTAGE: {
        "title": "Escasez de recursos",
        "description": "Los suministros básicos escasean.",
        "narrative": "Los suministros básicos escasean en los mercados.",
        "effects": {
            "legitimacy_change": -5.0,
            "pressure_change": 8.0,
            "resources_change": -12.0,
            "vitality_change": -3.0,
        },
    },
}


def get_random_crisis(seed: int | None = None) -> Crisis:
    rng = random.Random(seed)
    crisis_type = rng.choice(list(CRISIS_DATA.keys()))
    return create_crisis(crisis_type)


def create_crisis(crisis_type: CrisisType, turns: int = 3) -> Crisis:
    data = CRISIS_DATA[crisis_type]
    return Crisis(
        crisis_type=crisis_type,
        title=data["title"],
        description=data["description"],
        narrative=data["narrative"],
        effects=CrisisEffect(**data["effects"]),
        turns_remaining=turns,
    )


def should_trigger_crisis(world_state: dict, check_interval: int = 3, tick: int = 0) -> bool:
    if tick % check_interval != 0:
        return False

    legitimacy = world_state.get("legitimacy", 50)
    pressure = world_state.get("pressure", 30)
    resources = world_state.get("resources_global", 50)

    if legitimacy < 30 or pressure > 80 or resources < 20:
        return True

    return random.Random(tick).random() < 0.3


def format_crisis_narrative(crisis: Crisis) -> str:
    return f"""◆ {crisis.title}
  {crisis.narrative}
  ({_format_effects(crisis.effects)})"""


def _format_effects(effects: CrisisEffect) -> str:
    parts = []
    if effects.legitimacy_change != 0:
        sign = "+" if effects.legitimacy_change > 0 else ""
        parts.append(f"legitimacy {sign}{int(effects.legitimacy_change)}")
    if effects.pressure_change != 0:
        sign = "+" if effects.pressure_change > 0 else ""
        parts.append(f"presión {sign}{int(effects.pressure_change)}")
    if effects.resources_change != 0:
        sign = "+" if effects.resources_change > 0 else ""
        parts.append(f"recursos {sign}{int(effects.resources_change)}")
    return ", ".join(parts)
