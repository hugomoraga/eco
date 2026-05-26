from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ArchetypeActionPreferences:
    preferred_actions: list[str]


@dataclass
class ArchetypeGoalWeights:
    accumulate: float
    progress: float
    survive: float
    maintain: float


@dataclass
class ArchetypeStats:
    loyalty: float
    influence: float
    vitality: float


@dataclass
class Archetype:
    id: str
    display_name: str
    description: str
    intro_texts: list[str]
    color: str
    goal_weights: ArchetypeGoalWeights
    action_preferences: ArchetypeActionPreferences
    base_stats: ArchetypeStats


class ArchetypeRegistry:
    _instance: ArchetypeRegistry | None = None
    _archetypes: dict[str, Archetype] = {}
    _loaded: bool = False

    def __new__(cls) -> ArchetypeRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> ArchetypeRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_from_yaml(self, yaml_path: str | Path | None = None) -> None:
        if self._loaded:
            return

        if yaml_path is None:
            yaml_path = Path(__file__).parent.parent.parent / "data" / "archetypes.yaml"

        yaml_path = Path(yaml_path)

        if not yaml_path.exists():
            self._load_defaults()
            return

        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        archetypes_data = data.get("archetypes", {})
        for arch_id, arch_data in archetypes_data.items():
            self._archetypes[arch_id] = Archetype(
                id=arch_id,
                display_name=arch_data.get("display_name", arch_id),
                description=arch_data.get("description", ""),
                intro_texts=arch_data.get("intro_texts", []),
                color=arch_data.get("color", "white"),
                goal_weights=ArchetypeGoalWeights(
                    accumulate=arch_data.get("goal_weights", {}).get("accumulate", 0.25),
                    progress=arch_data.get("goal_weights", {}).get("progress", 0.25),
                    survive=arch_data.get("goal_weights", {}).get("survive", 0.25),
                    maintain=arch_data.get("goal_weights", {}).get("maintain", 0.25),
                ),
                action_preferences=ArchetypeActionPreferences(
                    preferred_actions=arch_data.get("action_preferences", ["conversar"]),
                ),
                base_stats=ArchetypeStats(
                    loyalty=arch_data.get("base_stats", {}).get("loyalty", 50.0),
                    influence=arch_data.get("base_stats", {}).get("influence", 10.0),
                    vitality=arch_data.get("base_stats", {}).get("vitality", 100.0),
                ),
            )

        self._loaded = True

    def _load_defaults(self) -> None:
        self._archetypes = {
            "artisan": Archetype(
                id="artisan",
                display_name="Artesano",
                description="Constructor, maker",
                intro_texts=["Eres la voz de los artesanos."],
                color="cyan",
                goal_weights=ArchetypeGoalWeights(accumulate=0.4, progress=0.4, survive=0.2, maintain=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["organizar", "reclutar", "conversar"]),
                base_stats=ArchetypeStats(loyalty=55.0, influence=10.0, vitality=100.0),
            ),
            "merchant": Archetype(
                id="merchant",
                display_name="Mercader",
                description="Comerciante",
                intro_texts=["De las transacciones surge el poder."],
                color="yellow",
                goal_weights=ArchetypeGoalWeights(accumulate=0.6, maintain=0.3, survive=0.1, progress=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["negociar", "propagar", "conversar"]),
                base_stats=ArchetypeStats(loyalty=50.0, influence=15.0, vitality=100.0),
            ),
            "warrior": Archetype(
                id="warrior",
                display_name="Guerrero",
                description="Luchador",
                intro_texts=["La fuerza bruta abre caminos."],
                color="red",
                goal_weights=ArchetypeGoalWeights(maintain=0.5, progress=0.4, survive=0.1, accumulate=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["sabotar", "predicar", "organizar"]),
                base_stats=ArchetypeStats(loyalty=45.0, influence=12.0, vitality=120.0),
            ),
            "leader": Archetype(
                id="leader",
                display_name="Líder",
                description="Guía",
                intro_texts=["Los demás te siguen."],
                color="magenta",
                goal_weights=ArchetypeGoalWeights(progress=0.5, accumulate=0.3, survive=0.2, maintain=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["predicar", "organizar", "reclutar"]),
                base_stats=ArchetypeStats(loyalty=60.0, influence=20.0, vitality=100.0),
            ),
            "scholar": Archetype(
                id="scholar",
                display_name="Erudito",
                description="Sabio",
                intro_texts=["El conocimiento es poder."],
                color="blue",
                goal_weights=ArchetypeGoalWeights(progress=0.4, accumulate=0.4, maintain=0.2, survive=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["propagar", "conversar", "predicar"]),
                base_stats=ArchetypeStats(loyalty=65.0, influence=12.0, vitality=80.0),
            ),
            "artist": Archetype(
                id="artist",
                display_name="Artista",
                description="Creador",
                intro_texts=["El arte desafía."],
                color="green",
                goal_weights=ArchetypeGoalWeights(progress=0.5, accumulate=0.3, survive=0.2, maintain=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["predicar", "propagar", "conversar"]),
                base_stats=ArchetypeStats(loyalty=55.0, influence=14.0, vitality=90.0),
            ),
            "mystic": Archetype(
                id="mystic",
                display_name="Místico",
                description="Visionario",
                intro_texts=["Ves lo que otros no pueden."],
                color="purple",
                goal_weights=ArchetypeGoalWeights(maintain=0.5, progress=0.3, survive=0.2, accumulate=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["predicar", "organizar", "conversar"]),
                base_stats=ArchetypeStats(loyalty=70.0, influence=16.0, vitality=85.0),
            ),
            "wanderer": Archetype(
                id="wanderer",
                display_name="Caminante",
                description="Viajero",
                intro_texts=["Llegas de donde nadie te espera."],
                color="white",
                goal_weights=ArchetypeGoalWeights(survive=0.6, progress=0.3, maintain=0.1, accumulate=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["propagar", "conversar", "reclutar"]),
                base_stats=ArchetypeStats(loyalty=40.0, influence=8.0, vitality=100.0),
            ),
            "neutral": Archetype(
                id="neutral",
                display_name="Neutral",
                description="Sin arquetipo",
                intro_texts=["El cambio viene."],
                color="dim",
                goal_weights=ArchetypeGoalWeights(survive=0.5, progress=0.3, accumulate=0.2, maintain=0.0),
                action_preferences=ArchetypeActionPreferences(preferred_actions=["conversar", "propagar", "reclutar"]),
                base_stats=ArchetypeStats(loyalty=50.0, influence=10.0, vitality=100.0),
            ),
        }
        self._loaded = True

    def get(self, archetype_id: str) -> Archetype:
        if not self._loaded:
            self.load_from_yaml()
        return self._archetypes.get(archetype_id, self._archetypes["neutral"])

    def get_intro_text(self, archetype_id: str, seed: int | None = None) -> str:
        archetype = self.get(archetype_id)
        if not archetype.intro_texts:
            return archetype.description
        rng = random.Random(seed)
        return rng.choice(archetype.intro_texts)

    def get_preferred_action(self, archetype_id: str, seed: int | None = None) -> str:
        archetype = self.get(archetype_id)
        rng = random.Random(seed)
        return rng.choice(archetype.action_preferences.preferred_actions)

    def get_goal_weights(self, archetype_id: str) -> ArchetypeGoalWeights:
        return self.get(archetype_id).goal_weights

    def all_archetypes(self) -> list[Archetype]:
        if not self._loaded:
            self.load_from_yaml()
        return list(self._archetypes.values())


def get_archetype(archetype_id: str) -> Archetype:
    return ArchetypeRegistry.get_instance().get(archetype_id)


def get_intro_text(archetype_id: str, seed: int | None = None) -> str:
    return ArchetypeRegistry.get_instance().get_intro_text(archetype_id, seed)


def get_preferred_action(archetype_id: str, seed: int | None = None) -> str:
    return ArchetypeRegistry.get_instance().get_preferred_action(archetype_id, seed)


def get_goal_weights(archetype_id: str) -> ArchetypeGoalWeights:
    return ArchetypeRegistry.get_instance().get_goal_weights(archetype_id)
