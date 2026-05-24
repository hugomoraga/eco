from __future__ import annotations

import uuid

from game_core.ai.base import AIAdapter
from game_core.domain.npc import NPC
from game_core.engine.random import SeededRandom


class NPCGenerator:
    def __init__(self, adapter: AIAdapter, seed: int = 42):
        self.adapter = adapter
        self.rng = SeededRandom.get_instance(seed)

    def generate(self, context: dict) -> NPC:
        response = self.adapter.generate_npc(context)

        if response.success and response.data:
            return self._create_npc(response.data, context)
        else:
            return self._generate_fallback(context)

    def _create_npc(self, data: dict, context: dict) -> NPC:
        name = data.get("name", f"NPC_{uuid.uuid4().hex[:8]}")
        role = data.get("role", "unknown")
        archetype = data.get("archetype", "neutral")
        essence = data.get("essence", "anarchism")

        npc = NPC(
            id=str(uuid.uuid4()),
            name=name,
            essence=essence,
            role=role,
            archetype=archetype,
            influence=self.rng.randint(5, 30),
            loyalty=50.0,
        )

        return npc

    def _generate_fallback(self, context: dict) -> NPC:
        essences = ["anarchism", "technocracy", "absurdism", "thelema", "ecology"]
        archetypes = ["scientist", "propagator", "cult_leader", "reformer", "dissident"]

        essence = self.rng.choice(essences)
        archetype = self.rng.choice(archetypes)

        names = {
            "scientist": ["Dra. Selen", "Prof. Kanto", "Ing. Lumen"],
            "propagator": ["Kárax", "Hermana Vacio", "Broto"],
            "cult_leader": ["El Guía", "La Voz", "El Sin Nombre"],
            "reformer": ["Maestro Orin", "Doctora Tess", "Capi Venn"],
            "dissident": ["El Olvidado", "La Sombra", "Sin Voz"],
        }

        name = self.rng.choice(names.get(archetype, ["NPC"]))

        return NPC(
            id=str(uuid.uuid4()),
            name=name,
            essence=essence,
            role=archetype,
            archetype=archetype,
            influence=self.rng.randint(5, 30),
            loyalty=50.0,
        )

    def generate_batch(self, context: dict, count: int) -> list[NPC]:
        return [self.generate(context) for _ in range(count)]