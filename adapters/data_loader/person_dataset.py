"""
PersonDataset — loads archetype persons from data/world/persons/*.yaml
"""
from __future__ import annotations

import yaml
from pathlib import Path

from core.domain.entities import Person, EssenceProfile, EssenceScore


def load_person_dataset(persons_dir: str = "data/world/persons") -> list[Person]:
    """
    Load all person archetype YAML files from persons_dir.
    Returns Person objects with EssenceProfile built from YAML.
    """
    persons = []
    path = Path(persons_dir)
    for yaml_file in sorted(path.glob("*.yaml")):
        with open(yaml_file) as f:
            raw = yaml.safe_load(f)

        if not raw:
            continue

        # archetype files have `dataset: archetype` header
        dataset_tag = raw.get("dataset", "")
        if dataset_tag != "archetype":
            continue

        persons_data = raw.get("persons", [])
        for p_data in persons_data:
            person = _yaml_to_person(p_data)
            if person:
                persons.append(person)

    return persons


def _yaml_to_person(data: dict) -> Person | None:
    """Convert a single person entry from YAML to Person entity."""
    essence_data = data.get("essence", {})

    dominant = []
    for e in essence_data.get("dominant", []):
        dominant.append(EssenceScore(essence=e.get("essence", ""), value=float(e.get("value", 0))))

    underlying = []
    for e in essence_data.get("underlying", []):
        underlying.append(EssenceScore(essence=e.get("essence", ""), value=float(e.get("value", 0))))

    essence_profile = EssenceProfile(dominant=dominant, underlying=underlying)

    tags = data.get("tags", [])
    archetype_tags = data.get("archetype_tags", [])

    return Person(
        id=data.get("id", ""),
        name=data.get("name", ""),
        role=",".join(archetype_tags) if archetype_tags else "",
        archetype=",".join(archetype_tags) if archetype_tags else "neutral",
        type="npc",
        essence_profile=essence_profile,
        loyalty=float(data.get("loyalty", 50)),
        influence=20.0,
        vitality=100.0,
        coherence=50.0,
    )


def get_persons_by_archetype(archetype: str, persons_dir: str = "data/world/persons") -> list[Person]:
    """Get persons matching a specific archetype tag."""
    all_persons = load_person_dataset(persons_dir)
    return [p for p in all_persons if archetype in p.archetype.split(",")]


def get_random_persons(count: int, persons_dir: str = "data/world/persons", seed: int = 42) -> list[Person]:
    """Get a random sample of persons from the dataset."""
    import random
    all_persons = load_person_dataset(persons_dir)
    random.seed(seed)
    return random.sample(all_persons, min(count, len(all_persons)))