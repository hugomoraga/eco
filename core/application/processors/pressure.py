from __future__ import annotations

from typing import ClassVar

from core.domain import EssenceRegistry


class DerivePressureCalculator:
    THRESHOLDS: ClassVar[dict] = {
        "transformation": 75,
        "cisma": 60,
        "radicalization": 50,
        "institutionalization": 40,
        "collapse": 85,
        "reform": 45,
    }

    @classmethod
    def calculate(
        cls,
        material_pressure: float,
        social_pressure: float,
        institutional_pressure: float,
        temporal_pressure: float,
        lineage: list[str],
        dominant_essence: str | None = None,
    ) -> float:
        if not lineage and not dominant_essence:
            return 0.0

        compatibility_modifier = cls._calculate_compatibility_modifier(lineage)
        mutation_risk_bonus = cls._calculate_mutation_risk_bonus(dominant_essence or (lineage[0] if lineage else "anarchism"))

        pressure = (
            (material_pressure * 0.25)
            + (social_pressure * 0.25)
            + (institutional_pressure * 0.25)
            + (temporal_pressure * 0.25)
            - compatibility_modifier
            + mutation_risk_bonus
        )

        return max(0.0, min(100.0, pressure))

    @classmethod
    def _calculate_compatibility_modifier(cls, lineage: list[str]) -> float:
        if len(lineage) < 2:
            return 0.0

        total_affinity = 0.0
        count = 0

        for i in range(len(lineage) - 1):
            affinity = EssenceRegistry.get_affinity(lineage[i], lineage[i + 1])
            total_affinity += affinity
            count += 1

        if count == 0:
            return 0.0

        avg_affinity = total_affinity / count

        if avg_affinity > 15:
            return -20
        elif avg_affinity > 5:
            return -10
        elif avg_affinity < -15:
            return 20
        elif avg_affinity < -5:
            return 10
        else:
            return 0.0

    @classmethod
    def _calculate_mutation_risk_bonus(cls, essence: str) -> float:
        drift_risk = EssenceRegistry.get_modifier(essence, "drift_risk")
        if drift_risk:
            return min(drift_risk * 0.8, 20.0)
        return 0.0

    @classmethod
    def get_threshold_result(cls, pressure: float) -> list[str]:
        results = []
        for event, threshold in cls.THRESHOLDS.items():
            if pressure >= threshold:
                results.append(event)
        return results


class EconomyPressure:
    @classmethod
    def calculate_material_pressure(cls, world_resources: dict[str, float]) -> float:
        thresholds = [
            ("food", 30, 25),
            ("infrastructure", 35, 20),
            ("energy", 20, 30),
            ("knowledge", 25, 15),
        ]

        pressure = 0.0
        for resource, danger_threshold, critical_value in thresholds:
            value = world_resources.get(resource, 50)
            if value < danger_threshold:
                pressure += 20
                if value < critical_value:
                    pressure += 10

        return min(pressure, 100)

    @classmethod
    def calculate_social_pressure(cls, world: World) -> float:
        inequality = getattr(world, "inequality", 50)
        stability = getattr(world, "stability", 50)

        pressure = 0.0

        if inequality > 70:
            pressure += 15
        elif inequality > 50:
            pressure += 5

        if stability < 35:
            pressure += 20
        elif stability < 50:
            pressure += 10

        return min(pressure, 100)
