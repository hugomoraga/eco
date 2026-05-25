from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import Circle


ADJECTIVES_POOL = [
    "First", "Burning", "Silent", "Wandering", "Echoing",
    "Hidden", "Crimson", "Silver", "Ancient", "New",
    "Radiant", "Shadowed", "Vigilant", "Free", "Bound",
]

NOUNS_POOL = [
    "Echo", "Garden", "Flame", "Voice", "Root",
    "Threshold", "Memory", "Path", "Mirror", "Stone",
    "Signal", "Tide", "Vision", "Command", "Synergy",
]

ESSENCE_TEMPLATES = {
    "anarchism": [
        "Circle of the Free",
        "Circle of Autonomy",
        "Circle of the Syndicate",
        "Circle of No Masters",
        "Circle of the Liberated",
        "Circle of the Horizontal",
    ],
    "collectivism": [
        "Circle of the Commons",
        "Circle of the Collective",
        "Circle of Solidarity",
        "Circle of United Voices",
        "Circle of the Many",
        "Circle of Together",
    ],
    "technocracy": [
        "Circle of the Protocol",
        "Circle of the Network",
        "Circle of Systems",
        "Circle of the Engineers",
        "Circle of the Efficient",
        "Circle of the Optimized",
    ],
    "absurdism": [
        "Circle of the Laughing Void",
        "Circle of Paradox",
        "Circle of the Unreasonable",
        "Circle of the Absurd",
        "Circle of the Inconsistent",
        "Circle of the Silly",
    ],
    "thelema": [
        "Circle of Will",
        "Circle of the Star",
        "Circle of Destiny",
        "Circle of the Initiated",
        "Circle of Magick",
        "Circle of True Will",
    ],
    "ecology": [
        "Circle of the Living Earth",
        "Circle of Balance",
        "Circle of Cycles",
        "Circle of the Root Network",
        "Circle of Sustainability",
        "Circle of the Green",
    ],
}


def generate_unique_circle_name(
    essence: str, existing_circles: list[Circle]
) -> str:
    """Generate a name unique among existing circles."""
    templates = ESSENCE_TEMPLATES.get(essence, [])
    used_names = {c.name for c in existing_circles if c.name}

    for name in templates:
        if name not in used_names:
            return name

    import random
    for _ in range(100):
        adj = random.choice(ADJECTIVES_POOL)
        noun = random.choice(NOUNS_POOL)
        name = f"Circle of the {adj} {noun}"
        if name not in used_names:
            return name

    return f"Circle of the {essence.title()}"


def generate_circle_name_with_fallback(
    essence: str, existing_circles: list[Circle], use_template_chance: float = 0.7
) -> str:
    """Generate circle name with template or fallback."""
    import random

    templates = ESSENCE_TEMPLATES.get(essence, [])

    if templates and random.random() < use_template_chance:
        used_names = {c.name for c in existing_circles if c.name}
        available = [t for t in templates if t not in used_names]
        if available:
            return random.choice(available)

    return generate_unique_circle_name(essence, existing_circles)