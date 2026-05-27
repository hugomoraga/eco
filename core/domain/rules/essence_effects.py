from __future__ import annotations

from typing import ClassVar

from core.domain import EssenceRegistry


class EssenceEffects:
    ESSENCE_THRESHOLD: ClassVar[float] = 50.0

    @classmethod
    def apply_to_echo(cls, echo) -> dict[str, float]:
        lineage = echo.genealogical_lineage or [echo.essence]
        effects = {}

        for essence_name in lineage:
            modifiers = EssenceRegistry.get_modifiers(essence_name)
            for key, value in modifiers.items():
                effects[key] = effects.get(key, 0) + value * 0.3

        return effects

    @classmethod
    def calculate_drift_risk(cls, echo) -> float:
        lineage = echo.genealogical_lineage or [echo.essence]
        if len(lineage) < 2:
            return 0.0

        drift_risk = 0.0
        for essence_name in lineage:
            essence_drift = EssenceRegistry.get_modifier(essence_name, "drift_risk")
            if essence_drift:
                drift_risk += essence_drift

        return drift_risk / len(lineage)

    @classmethod
    def get_essence_affinity(cls, essence1: str, essence2: str) -> float:
        return EssenceRegistry.get_affinity(essence1, essence2)

    @classmethod
    def check_crystallization(cls, echo) -> bool:
        lineage = echo.genealogical_lineage or [echo.essence]
        if len(lineage) < 3:
            return False

        essence_counts = {}
        for e in lineage:
            essence_counts[e] = essence_counts.get(e, 0) + 1

        max_count = max(essence_counts.values())
        return max_count / len(lineage) > 0.7
