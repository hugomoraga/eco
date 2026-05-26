"""
Echo factory — creates Echo entities.
"""
from __future__ import annotations

from core.domain.entities import Echo, EchoAttribute, EchoPhase, EssenceProfile, EssenceScore
from core.systems.random import SeededRandom


def create_echo(
    name: str,
    essence: str,
    seed: int = 42,
    phase: EchoPhase = EchoPhase.ACTIVE,
    attributes: list[EchoAttribute] | None = None,
) -> Echo:
    """Create an Echo with default attributes if not provided."""
    rng = SeededRandom.get_instance(seed)

    if attributes is None:
        attributes = [
            EchoAttribute(label="clarity", value=rng.randint(50, 80)),
            EchoAttribute(label="resonance", value=rng.randint(40, 70)),
            EchoAttribute(label="presence", value=rng.randint(30, 60)),
            EchoAttribute(label="memory", value=rng.randint(20, 50)),
            EchoAttribute(label="will", value=rng.randint(50, 90)),
            EchoAttribute(label="shadow", value=rng.randint(10, 40)),
        ]

    # Build EssenceProfile (spec-47)
    dominant = [EssenceScore(essence=essence, value=50.0)]
    essence_profile = EssenceProfile(dominant=dominant, underlying=[])

    echo = Echo(
        name=name,
        essence=essence,
        essence_profile=essence_profile,
        phase=phase,
        attributes=attributes,
    )
    echo.genealogical_lineage = [essence]

    return echo
