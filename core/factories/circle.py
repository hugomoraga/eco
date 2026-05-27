"""
Circle factory — name generation and lifecycle management.

Replaces:
- game_core/circle/circle_manager.py
- game_core/circle/name_generator.py
"""
from __future__ import annotations

import random
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain import Circle, Echo, Ideas, World


# ─────────────────────────────────────────────────────────────────────────────
# Name Generation
# ─────────────────────────────────────────────────────────────────────────────

ADJECTIVES_POOL = [
    "First", "Burning", "Silent", "Wandering", "Echoing",
    "Hidden", "Crimson", "Silver", "Ancient", "New",
    "Radiant", "Shadowed", "Vigilant", "Free", "Bound",
]

NOUNS_POOL = [
    "Echo", "Garden", "Flame", "Voice", "Root",
    "Threshold", "Memory", "Path", "Mirror", "Stone",
    "Signal", "Tide", "Vision", "Command", "Synergy",
]

ESSENCE_TEMPLATES_EN = {
    "anarchism": [
        "Circle of the Free", "Circle of Autonomy", "Circle of the Syndicate",
        "Circle of No Masters", "Circle of the Liberated", "Circle of the Horizontal",
    ],
    "collectivism": [
        "Circle of the Commons", "Circle of the Collective", "Circle of Solidarity",
        "Circle of United Voices", "Circle of the Many", "Circle of Together",
    ],
    "technocracy": [
        "Circle of the Protocol", "Circle of the Network", "Circle of Systems",
        "Circle of the Engineers", "Circle of the Efficient", "Circle of the Optimized",
    ],
    "absurdism": [
        "Circle of the Laughing Void", "Circle of Paradox", "Circle of the Unreasonable",
        "Circle of the Absurd", "Circle of the Inconsistent", "Circle of the Silly",
    ],
    "thelema": [
        "Circle of Will", "Circle of the Star", "Circle of Destiny",
        "Circle of the Initiated", "Circle of Magick", "Circle of True Will",
    ],
    "ecology": [
        "Circle of the Living Earth", "Circle of Balance", "Circle of Cycles",
        "Circle of the Root Network", "Circle of Sustainability", "Circle of the Green",
    ],
}

ESSENCE_TEMPLATES_ES = {
    "anarchism": [
        "Círculo de los Libres", "Círculo de la Autonomía", "Círculo del Sindicalismo",
        "Círculo Sin Amos", "Círculo de los Liberados", "Círculo de lo Horizontal",
    ],
    "collectivism": [
        "Círculo de los Comunes", "Círculo de la Colectividad", "Círculo de la Solidaridad",
        "Círculo de Voces Unidas", "Círculo de los Muchos", "Círculo de la Unión",
    ],
    "technocracy": [
        "Círculo del Protocolo", "Círculo de la Red", "Círculo de los Sistemas",
        "Círculo de los Ingenieros", "Círculo de lo Eficiente", "Círculo de lo Optimizado",
    ],
    "absurdism": [
        "Círculo de la Nada Riente", "Círculo de la Paradoja", "Círculo de lo Irrazonable",
        "Círculo de lo Absurdo", "Círculo de lo Inconsistente", "Círculo de lo Ridículo",
    ],
    "thelema": [
        "Círculo de la Voluntad", "Círculo de la Estrella", "Círculo del Destino",
        "Círculo de los Iniciados", "Círculo de la Magia", "Círculo de la Voluntad Verdadera",
    ],
    "ecology": [
        "Círculo de la Tierra Viva", "Círculo del Equilibrio", "Círculo de los Ciclos",
        "Círculo de la Red de Raíces", "Círculo de la Sostenibilidad", "Círculo de lo Verde",
    ],
}

ADJECTIVES_POOL_ES = [
    "Primero", "Ardiente", "Silencioso", "Errante", "Resonante",
    "Oculto", "Carmesí", "Plateado", "Antiguo", "Nuevo",
    "Radiante", "Sombrío", "Vigilante", "Libre", "Atado",
]

NOUNS_POOL_ES = [
    "Eco", "Jardín", "Llama", "Voz", "Raíz",
    "Umbral", "Memoria", "Camino", "Espejo", "Piedra",
    "Señal", "Marea", "Visión", "Mando", "Sinergia",
]

ESSENCE_TEMPLATES = ESSENCE_TEMPLATES_EN


def _get_templates_for_lang(lang: str):
    if lang == "es":
        return ESSENCE_TEMPLATES_ES
    return ESSENCE_TEMPLATES_EN


def _get_pools_for_lang(lang: str):
    if lang == "es":
        return ADJECTIVES_POOL_ES, NOUNS_POOL_ES
    return ADJECTIVES_POOL, NOUNS_POOL


def _get_fallback_prefix(lang: str) -> str:
    if lang == "es":
        return "Círculo de "
    return "Circle of the "


def generate_unique_circle_name(essence: str, existing_circles: list[Circle]) -> str:
    """Generate a name unique among existing circles."""
    from adapters.i18n import get_lang
    lang = get_lang()
    templates = _get_templates_for_lang(lang).get(essence, [])
    used_names = {c.name for c in existing_circles if c.name}

    for name in templates:
        if name not in used_names:
            return name

    adj_pool, noun_pool = _get_pools_for_lang(lang)
    prefix = _get_fallback_prefix(lang)

    for _ in range(100):
        adj = random.choice(adj_pool)
        noun = random.choice(noun_pool)
        if lang == "es":
            name = f"{prefix}{adj} {noun}"
        else:
            name = f"{prefix}{adj} {noun}"
        if name not in used_names:
            return name

    return f"{prefix}{essence.title()}"


def generate_circle_name_with_fallback(
    essence: str, existing_circles: list[Circle], use_template_chance: float = 0.7
) -> str:
    """Generate circle name with template or fallback."""
    from adapters.i18n import get_lang
    lang = get_lang()
    templates = _get_templates_for_lang(lang).get(essence, [])

    if templates and random.random() < use_template_chance:
        used_names = {c.name for c in existing_circles if c.name}
        available = [t for t in templates if t not in used_names]
        if available:
            return random.choice(available)

    return generate_unique_circle_name(essence, existing_circles)


def create_circle(
    world: World,
    echo: Echo,
    essence: str | None = None,
    ideas: list[Ideas] | None = None,
    founding_tick: int = 0,
) -> Circle:
    """Create and register a new Circle in the world."""
    from core.domain import Circle, CircleEvent
    from core.domain.enums import CircleEventType

    name = generate_circle_name_with_fallback(essence or echo.essence, world.circles)
    essence = essence or echo.essence

    if ideas is None:
        ideas = echo.ideas if echo.ideas else echo.known_tags

    circle = Circle(
        name=name,
        echo_id=echo.id,
        essence=essence,
        founding_tick=founding_tick,
        ideas=ideas,
        member_ids=[echo.id],
        influence=15.0,
    )

    circle.history.append(CircleEvent(
        type=CircleEventType.FOUNDED,
        turn=founding_tick,
        echo_id=echo.id,
        details=f"Founded by {echo.name or 'First Echo'}",
    ))

    world.circles.append(circle)
    echo.circles.append(circle.id)
    echo.phase = echo.phase.ACTIVE

    return circle


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle
# ─────────────────────────────────────────────────────────────────────────────

def process_circle_tick(circle: Circle, world: World, rng) -> list[str]:
    """Process a single world tick for a circle. Returns list of activities."""
    activities = []

    if circle.status.value == "dissolved":
        return activities

    from core.domain import CircleStatus

    if circle.member_count == 0:
        circle.dormant_turns += 1
        if circle.dormant_turns >= 10:
            circle.status = CircleStatus.DISSOLVED
            activities.append(f"{circle.name} dissolved (0 members for 10 turns)")
        else:
            circle.status = CircleStatus.DORMANT
        return activities

    if circle.can_grow() and rng.random() < 0.15:
        activity = _attract_echo_to_circle(circle, world)
        if activity:
            activities.append(activity)

    if circle.should_decay() and rng.random() < 0.03:
        activity = _remove_lowest_resonance_member(circle, world)
        if activity:
            activities.append(activity)

    if circle.should_splinter() and rng.random() < 0.1:
        activity = _splinter_circle(circle, world, rng)
        if activity:
            activities.append(activity)

    return activities


def _attract_echo_to_circle(circle: Circle, world: World) -> str | None:
    """Try to attract an echo to the circle."""
    from core.domain import CircleEvent
    from core.domain.enums import CircleEventType
    from core.domain.rules.essence_effects import EssenceEffects

    candidates = [
        e for e in world.echoes
        if e.id not in circle.member_ids
    ]

    if not candidates:
        return None

    best_candidate = None
    best_affinity = -1

    for echo in candidates:
        affinity = EssenceEffects.get_essence_affinity(circle.essence, echo.essence)
        if affinity > best_affinity and affinity > 0.3:
            best_affinity = affinity
            best_candidate = echo

    if best_candidate:
        circle.add_member(best_candidate.id)
        best_candidate.circles.append(circle.id)
        circle.history.append(CircleEvent(
            type=CircleEventType.JOIN,
            turn=world.clock.world_tick,
            echo_id=best_candidate.id,
            details=f"{best_candidate.name or 'Echo'} joined {circle.name}",
        ))
        return f"{best_candidate.name or 'An echo'} joined {circle.name} (influence: {circle.influence:.0f})"

    return None


def _remove_lowest_resonance_member(circle: Circle, world: World) -> str | None:
    """Remove the member with lowest resonance from circle."""
    if not circle.member_ids:
        return None

    members = [world.get_echo(eid) for eid in circle.member_ids]
    members = [m for m in members if m]

    if not members:
        return None

    lowest = min(
        members,
        key=lambda e: e.get_attribute("resonance").value if e.get_attribute("resonance") else 50.0
    )

    circle.remove_member(lowest.id)
    if hasattr(lowest, 'circles') and circle.id in lowest.circles:
        lowest.circles.remove(circle.id)

    from core.domain import CircleEvent
    from core.domain.enums import CircleEventType
    circle.history.append(CircleEvent(
        type=CircleEventType.LEAVE,
        turn=world.clock.world_tick,
        echo_id=lowest.id,
        details=f"{lowest.name or 'Echo'} left {circle.name}",
    ))

    return f"{lowest.name or 'An echo'} left {circle.name} (low resonance)"


def _splinter_circle(circle: Circle, world: World, rng) -> str | None:
    """Split circle into two when it has 6+ members."""
    if circle.member_count < 6:
        return None

    kept_members = circle.member_ids[:3]
    new_members = circle.member_ids[3:6] if len(circle.member_ids) > 3 else circle.member_ids[3:]

    new_name = generate_circle_name_with_fallback(circle.essence, world.circles)

    from core.domain import CircleEvent
    from core.domain.enums import CircleEventType
    new_circle = type(circle)(
        id=str(uuid.uuid4()),
        name=new_name,
        essence=circle.essence,
        founding_tick=world.clock.world_tick,
        ideology_tags=list(circle.ideology_tags),
        member_ids=new_members,
        influence=circle.influence * 0.5,
        institutionalization_level=circle.institutionalization_level * 0.5,
        health=circle.health,
        status=circle.status,
    )

    for echo_id in new_members:
        echo = world.get_echo(echo_id)
        if echo and hasattr(echo, 'circles'):
            echo.circles.append(new_circle.id)

    circle.member_ids = kept_members
    circle.influence *= 0.7

    circle.history.append(CircleEvent(
        type=CircleEventType.SPLINTER,
        turn=world.clock.world_tick,
        details=f"Circle splintered into {new_name}",
    ))

    new_circle.history.append(CircleEvent(
        type=CircleEventType.FOUNDED,
        turn=world.clock.world_tick,
        details=f"Splintered from {circle.name}",
    ))

    world.circles.append(new_circle)

    return f"{circle.name} splintered → {new_name} ({len(new_members)} members)"


def _spawn_npc_in_circle(circle: Circle, world: World, rng) -> str | None:
    """Spawn NPC in circle if conditions are met."""
    if circle.member_count < 3:
        return None

    if rng.random() > 0.2:
        return None

    from adapters.ai import MockAdapter
    from core.factories.npc import create_npc

    npc = create_npc(MockAdapter(), {"essence": circle.essence, "context": "circle_growth"}, seed=rng.randint(0, 99999))

    circle.npcs.append(npc.id)
    circle.add_member(npc.id)

    from core.domain import CircleEvent
    from core.domain.enums import CircleEventType
    circle.history.append(CircleEvent(
        type=CircleEventType.NPC_SPAWN,
        turn=world.clock.world_tick,
        npc_id=npc.id,
        details=f"NPC {npc.name} spawned in {circle.name}",
    ))

    return npc.id
