"""
NPC factory — creates NPC entities.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from game_core.domain.entities import Person
from game_core.domain.npc import NPC
from game_core.systems.random import SeededRandom

if TYPE_CHECKING:
    from game_core.ai.base import AIAdapter


def create_npc(
    adapter: AIAdapter,
    context: dict,
    *,
    seed: int = 42,
    influence: int | None = None,
    loyalty: float | None = None,
) -> Person:
    """
    Creates a single NPC Person using the AI adapter.

    Falls back to deterministic generation if the adapter fails
    or returns no data.

    Returns:
        Person: the created NPC (with type="npc"), backed by the ``NPC`` domain model.
    """
    rng = SeededRandom.get_instance(seed)
    response = adapter.generate_npc(context)

    if response.success and response.data:
        return _build_npc(response.data, rng)
    else:
        return _fallback_npc(rng, context.get("essence", "anarchism"))


def create_npcs(
    adapter: AIAdapter,
    context: dict,
    count: int,
    *,
    seed: int = 42,
) -> list[Person]:
    """Creates ``count`` NPCs using the same context."""
    return [create_npc(adapter, context, seed=seed + i) for i in range(count)]


# ----------------------------------------------------------------------
# Internals
# ----------------------------------------------------------------------


def _build_npc(data: dict, rng) -> Person:
    name = data.get("name", f"NPC_{uuid.uuid4().hex[:8]}")
    role = data.get("role", "unknown")
    archetype = data.get("archetype", "neutral")
    essence = data.get("essence", "anarchism")

    return Person(
        id=str(uuid.uuid4()),
        name=name,
        essence=essence,
        role=role,
        archetype=archetype,
        type="npc",
        influence=rng.randint(5, 30),
        loyalty=50.0,
    )


def _fallback_npc(rng, essence: str) -> Person:
    essences_fallback = ["anarchism", "technocracy", "absurdism", "thelema", "ecology"]
    archetypes = ["scientist", "propagator", "cult_leader", "reformer", "dissident"]

    if essence not in essences_fallback:
        essence = rng.choice(essences_fallback)

    archetype = rng.choice(archetypes)

    names = {
        "scientist": ["Dra. Selen", "Prof. Kanto", "Ing. Lumen"],
        "propagator": ["Kárax", "Hermana Vacio", "Broto"],
        "cult_leader": ["El Guía", "La Voz", "El Sin Nombre"],
        "reformer": ["Maestro Orin", "Doctora Tess", "Capi Venn"],
        "dissident": ["El Olvidado", "La Sombra", "Sin Voz"],
    }

    name = rng.choice(names.get(archetype, ["NPC"]))

    return Person(
        id=str(uuid.uuid4()),
        name=name,
        essence=essence,
        role=archetype,
        archetype=archetype,
        type="npc",
        influence=rng.randint(5, 30),
        loyalty=50.0,
    )


# ----------------------------------------------------------------------
# Deprecated class — kept for backward compatibility until callers migrate
# ----------------------------------------------------------------------
import warnings as _warnings


class NPCGenerator:
    """Deprecated. Use ``create_npc`` or ``create_npcs`` instead."""

    def __init__(self, adapter: AIAdapter, seed: int = 42):
        _warnings.warn(
            "NPCGenerator is deprecated — use game_core.factory.create_npc()",
            DeprecationWarning,
            stacklevel=2,
        )
        self.adapter = adapter
        self.seed = seed

    def generate(self, context: dict) -> Person:
        return create_npc(self.adapter, context, seed=self.seed)

    def generate_batch(self, context: dict, count: int) -> list[Person]:
        return create_npcs(self.adapter, context, count, seed=self.seed)
