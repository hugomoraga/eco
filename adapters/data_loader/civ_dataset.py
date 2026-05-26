"""
CivDataset — loads civilization templates from data/civs/*.yaml
"""
from __future__ import annotations

import yaml
from pathlib import Path

from core.domain.entities import Civ, EssenceProfile, EssenceScore


def load_civ_dataset(civs_dir: str = "data/civs") -> list[Civ]:
    """
    Load all civilization YAML files from civs_dir.
    Returns a list of Civ objects with EssenceProfile built from the YAML dominant/underlying.
    """
    civs = []
    path = Path(civs_dir)
    for yaml_file in sorted(path.glob("*.yaml")):
        with open(yaml_file) as f:
            raw = yaml.safe_load(f)

        if not raw or raw.get("meta", {}).get("id") == "archetype":
            continue  # skip person archetype files

        civ = _yaml_to_civ(raw)
        if civ:
            civs.append(civ)

    return civs


def _yaml_to_civ(raw: dict) -> Civ | None:
    meta = raw.get("meta", {})
    civ_data = raw.get("civ", {})
    essence_data = raw.get("essence", {})

    dominant = []
    for e in essence_data.get("dominant", []):
        dominant.append(EssenceScore(essence=e.get("essence", ""), value=float(e.get("value", 0))))

    underlying = []
    for e in essence_data.get("underlying", []):
        underlying.append(EssenceScore(essence=e.get("essence", ""), value=float(e.get("value", 0))))

    essence_profile = EssenceProfile(dominant=dominant, underlying=underlying)

    host_data = raw.get("host", {})

    return Civ(
        meta_id=meta.get("id", ""),
        name=meta.get("name", ""),
        description=meta.get("description", ""),
        difficulty=meta.get("difficulty", "normal"),
        essence_profile=essence_profile,
        population=civ_data.get("population", 10000),
        stability=civ_data.get("stability", 50.0),
        pressure=civ_data.get("pressure", 30.0),
        legitimacy=civ_data.get("legitimacy", 60.0),
        resources_global=civ_data.get("resources_global", 70.0),
        crisis_threshold=civ_data.get("crisis_threshold", 75.0),
        collapse_threshold=civ_data.get("collapse_threshold", 15.0),
        resources=civ_data.get("resources", {
            "food": 80, "infrastructure": 60, "energy": 50, "knowledge": 50, "legitimacy": 60,
        }),
    )


def get_civ_by_meta_id(meta_id: str, civs_dir: str = "data/civs") -> Civ | None:
    """Load a single Civ by its meta.id."""
    all_civs = load_civ_dataset(civs_dir)
    for c in all_civs:
        if c.meta_id == meta_id:
            return c
    return None