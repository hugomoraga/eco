"""
Ideas factory — creates Ideas entities for Echo and Circle use.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.domain import Ideas

if TYPE_CHECKING:
    from core.application.processors.random import SeededRandom


# ----------------------------------------------------------------------
# Templates — essence → list of (category, name, weight)
# ----------------------------------------------------------------------
TAG_TEMPLATES: dict[str, list[tuple[str, str, float]]] = {
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


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def create_ideas_for_essence(
    rng: SeededRandom,
    essence: str,
    count: int = 2,
) -> list[Ideas]:
    """
    Creates ``count`` Ideas sampled from ``essence``'s template pool.

    Returns an empty list if the essence has no templates or ``count`` is 0.
    """
    templates = TAG_TEMPLATES.get(essence, [])
    if not templates:
        return []

    selected = rng.sample(templates, min(count, len(templates)))
    return [_make_idea(category, name, {essence: weight}) for category, name, weight in selected]


def create_random_idea(
    rng: SeededRandom,
) -> Ideas:
    """
    Creates a single random Ideas drawn from any essence at random.
    """
    all_templates: list[tuple[str, str, float, str]] = [
        (category, name, weight, essence)
        for essence, templates in TAG_TEMPLATES.items()
        for category, name, weight in templates
    ]

    if not all_templates:
        return Ideas(
            id=str(uuid.uuid4()),
            category="concept",
            name="Unknown",
            essence_weights={},
        )

    category, name, weight, essence = rng.choice(all_templates)
    return _make_idea(category, name, {essence: weight})


# ----------------------------------------------------------------------
# Internal helper
# ----------------------------------------------------------------------


def _make_idea(category: str, name: str, weights: dict[str, float]) -> Ideas:
    return Ideas(
        id=str(uuid.uuid4()),
        category=category,
        name=name,
        essence_weights=weights,
    )
