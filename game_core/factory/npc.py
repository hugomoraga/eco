"""
NPC factory — creates NPC entities.
"""
from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING

import yaml

from game_core.domain.entities import EssenceProfile, EssenceScore, Person
from game_core.domain.npc import NPC
from game_core.systems.random import SeededRandom

if TYPE_CHECKING:
    from game_core.ai.base import AIAdapter

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "world", "persons")


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


def _parse_essence_profile(essence_data: dict) -> EssenceProfile:
    """Parse essence data from YAML into EssenceProfile."""
    dominant = []
    underlying = []

    for item in essence_data.get("dominant", []):
        dominant.append(EssenceScore(essence=item["essence"], value=float(item["value"])))

    for item in essence_data.get("underlying", []):
        underlying.append(EssenceScore(essence=item["essence"], value=float(item["value"])))

    return EssenceProfile(dominant=dominant, underlying=underlying)


def load_npcs_from_datasets(seed: int = 42, max_per_dataset: int = 5) -> list[Person]:
    """
    Load NPCs from YAML datasets in data/world/persons/.

    Args:
        seed: Random seed for shuffle
        max_per_dataset: Maximum NPCs to load per YAML file (to avoid overcrowding)

    Returns:
        List of Person entities with type="npc"
    """
    rng = SeededRandom.get_instance(seed)
    persons = []

    dataset_dir = DATASET_PATH

    if not os.path.exists(dataset_dir):
        return persons

    yaml_files = [f for f in os.listdir(dataset_dir) if f.endswith(".yaml")]

    for yaml_file in yaml_files:
        filepath = os.path.join(dataset_dir, yaml_file)
        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)
        except Exception:
            continue

        if not data or "persons" not in data:
            continue

        persons_list = data["persons"]
        rng.shuffle(persons_list)

        for person_data in persons_list[:max_per_dataset]:
            archetype_tags = person_data.get("archetype_tags", [])
            primary_archetype = archetype_tags[0] if archetype_tags else "neutral"

            essence_data = person_data.get("essence", {})
            essence_profile = _parse_essence_profile(essence_data)

            dominant_essences = essence_profile.dominant_essences(min_value=10)
            dominant_essence = dominant_essences[0] if dominant_essences else "anarchism"

            person = Person(
                id=str(uuid.uuid4()),
                name=person_data.get("name", f"NPC-{uuid.uuid4().hex[:6]}"),
                role=primary_archetype,
                archetype=primary_archetype,
                type="npc",
                essence_profile=essence_profile,
                influence=float(person_data.get("influence", rng.randint(10, 40))),
                loyalty=float(person_data.get("loyalty", 50.0)),
                vitality=100.0,
                coherence=50.0,
            )
            persons.append(person)

    return persons


def spawn_npcs_to_world(world, seed: int = 42, max_per_dataset: int = 5) -> list[Person]:
    """
    Load NPCs from datasets and add them to world.persons.

    Returns the list of spawned NPCs.
    """
    npcs = load_npcs_from_datasets(seed=seed, max_per_dataset=max_per_dataset)

    if not hasattr(world, "persons"):
        world.persons = []

    for npc in npcs:
        if npc not in world.persons:
            world.persons.append(npc)

    return npcs


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
