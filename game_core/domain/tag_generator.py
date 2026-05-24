from __future__ import annotations

import uuid
from typing import ClassVar

from game_core.domain.entities import IdeologicalTag, EssenceRegistry
from game_core.engine.random import SeededRandom


class TagGenerator:
    TEMPLATES: ClassVar[dict[str, list[tuple[str, str, float]]]] = {
        "anarchism": [
            ("concept", "Voluntad Sin Amo", 0.8),
            ("concept", "Autonomia Radial", 0.7),
            ("concept", "Consenso Horizontal", 0.9),
            ("practice", "Accion Directa", 0.7),
            ("practice", "Desobediencia Civil", 0.6),
            ("symbol", "Circulo Vacio", 0.5),
            ("symbol", "A", 0.4),
        ],
        "technocracy": [
            ("concept", "Meritocracia Tecnica", 0.8),
            ("concept", "Optimizacion Sistematica", 0.9),
            ("concept", "Gobierno Algoritmico", 0.7),
            ("practice", "Protocolo Estandar", 0.6),
            ("practice", "Auditoria Continua", 0.7),
            ("symbol", "Engranaje", 0.5),
            ("symbol", "Dato", 0.4),
        ],
        "absurdism": [
            ("concept", "Caos Productivo", 0.7),
            ("concept", "Nada Tiene Sentido", 0.8),
            ("concept", "Libertad en el Vacío", 0.9),
            ("practice", "Risa Rituals", 0.6),
            ("practice", "Ironia Politica", 0.7),
            ("symbol", "Caras Sonrientes", 0.5),
            ("symbol", "Signo de Pregunta", 0.4),
        ],
        "thelema": [
            ("concept", "Haz Tu Voluntad", 0.9),
            ("concept", "Verdad Individual", 0.8),
            ("concept", "Gran Bestia", 0.7),
            ("practice", "Autodeificacion", 0.6),
            ("practice", "Magia Ritual", 0.7),
            ("symbol", "Ojo Abierto", 0.5),
            ("symbol", "666", 0.4),
        ],
        "ecology": [
            ("concept", "Equilibrio Natural", 0.8),
            ("concept", "Sistema Cerrado", 0.7),
            ("concept", "Crecimiento Sostenible", 0.9),
            ("practice", "Autonomia Local", 0.6),
            ("practice", "Banco de Semillas", 0.5),
            ("symbol", "Hoja", 0.5),
            ("symbol", "Circulo de Vida", 0.4),
        ],
    }

    def __init__(self, seed: int = 42):
        self.rng = SeededRandom.get_instance(seed)

    def generate_for_essence(self, essence: str, count: int = 2) -> list[IdeologicalTag]:
        templates = self.TEMPLATES.get(essence, [])
        if not templates:
            return []

        selected = self.rng.sample(templates, min(count, len(templates)))
        tags = []

        for category, name, weight in selected:
            tag = IdeologicalTag(
                id=str(uuid.uuid4()),
                category=category,
                name=name,
                essence_weights={essence: weight},
            )
            tags.append(tag)

        return tags

    def generate_random(self, essence: str, count: int = 1) -> list[IdeologicalTag]:
        all_templates = []
        for ess, templates in self.TEMPLATES.items():
            for category, name, weight in templates:
                if ess == essence:
                    all_templates.append((category, name, weight, ess))

        if not all_templates:
            return []

        selected = self.rng.sample(all_templates, min(count, len(all_templates)))
        tags = []

        for category, name, weight, ess in selected:
            tag = IdeologicalTag(
                id=str(uuid.uuid4()),
                category=category,
                name=name,
                essence_weights={ess: weight},
            )
            tags.append(tag)

        return tags