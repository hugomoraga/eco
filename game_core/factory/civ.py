"""
CivFactory — creates Civ entities from dataset YAML files.
No circular imports with Echo/World.
"""
from __future__ import annotations

from game_core.data.civ_dataset import load_civ_dataset
from game_core.domain.entities import Civ


def create_civ(meta_id: str, civs_dir: str = "data/civs") -> Civ | None:
    """
    Create a single Civ by meta_id from the dataset.
    Returns None if not found.
    """
    all_civs = load_civ_dataset(civs_dir)
    for c in all_civs:
        if c.meta_id == meta_id:
            return c
    return None


def create_all_civs(civs_dir: str = "data/civs") -> list[Civ]:
    """Load all Civs from the dataset."""
    return load_civ_dataset(civs_dir)


def create_default_civ(civs_dir: str = "data/civs") -> Civ:
    """Return the default civ (meta_id='default') or first available."""
    all_civs = load_civ_dataset(civs_dir)
    for c in all_civs:
        if c.meta_id == "default":
            return c
    return all_civs[0] if all_civs else _fallback_civ()


def _fallback_civ() -> Civ:
    """Minimal fallback if no civs are found."""
    from game_core.domain.entities import EssenceProfile, EssenceScore
    dominant = [EssenceScore(essence="humanism", value=40), EssenceScore(essence="pragmatism", value=35)]
    return Civ(
        meta_id="fallback",
        name="Unknown Civilization",
        description="No civ data found.",
        essence_profile=EssenceProfile(dominant=dominant, underlying=[]),
    )