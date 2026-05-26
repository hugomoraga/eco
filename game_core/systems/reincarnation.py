"""Reincarnation system - Echo death and rebirth logic."""

from __future__ import annotations

from dataclasses import dataclass

from game_core.domain.entities import Echo, Host, Person, World


@dataclass
class ReincarnationResult:
    old_echo_name: str
    new_echo_name: str
    new_host_name: str
    preserved: list[str]
    narrative: str


def find_reincarnation_host(echo: Echo, world: World) -> Person | None:
    """
    Find the best compatible person for an echo to reincarnate into.

    Algorithm:
    1. Filter candidates from same circles as echo
    2. If no candidates, search in allied circles
    3. If still none, search any person in the civ
    4. Score by essence similarity
    5. Return highest scoring candidate
    """
    candidates = _get_candidates(echo, world)
    if not candidates:
        return None

    scored = []
    for person in candidates:
        score = _calculate_affinity(echo, person)
        scored.append((score, person))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None


def _get_candidates(echo: Echo, world: World) -> list[Person]:
    """Get candidate persons for reincarnation, filtered by circle membership."""
    if not echo.circles:
        return [p for p in world.persons if p.type == "npc" and p.vitality > 0]

    echo_circle_ids = set(echo.circles)

    same_circle = []
    any_person = []

    for p in world.persons:
        if p.type != "npc" or p.vitality <= 0:
            continue

        if hasattr(p, 'circles') and p.circles:
            person_circles = set(p.circles)
            if echo_circle_ids & person_circles:
                same_circle.append(p)
                continue

        any_person.append(p)

    return same_circle if same_circle else any_person


def _calculate_affinity(echo: Echo, person: Person) -> float:
    """Calculate affinity score between echo and person."""
    score = 0.0

    if person.essence_profile and echo.essence_profile:
        echo_dom = set(e.essence for e in echo.essence_profile.dominant)
        person_dom = set(e.essence for e in person.essence_profile.dominant)

        overlap = echo_dom & person_dom
        score += len(overlap) * 30

        score += (100 - abs(
            echo.essence_profile.dominant[0].value if echo.essence_profile.dominant else 50
            - person.essence_profile.dominant[0].value if person.essence_profile.dominant else 50
        )) * 0.2

    score += person.loyalty * 0.1
    score += person.influence * 0.05

    return min(score, 100)


def preserve_echo_legacy(echo: Echo) -> dict:
    """Extract what gets preserved when an echo dies."""
    return {
        "essence_profile": echo.essence_profile.model_copy(),
        "known_tags": [t.model_copy() for t in echo.known_tags],
        "genealogical_lineage": list(echo.genealogical_lineage),
        "essence": echo.dominant_essence or echo.essence,
    }


def transform_legacy(legacy: dict, old_echo: Echo) -> dict:
    """
    Transform the legacy when reincarnating.

    The lineage evolves - the previous essence is appended.
    The essence may partially mutate (50% preserved, 50% influenced by new host).
    """
    lineage = legacy["genealogical_lineage"]
    lineage.append(legacy["essence"])

    return {
        "essence_profile": legacy["essence_profile"],
        "known_tags": legacy["known_tags"],
        "genealogical_lineage": lineage,
        "essence": legacy["essence"],
    }


def reincarnate_echo(
    echo: Echo,
    world: World,
    preserved_legacy: dict,
    transformed_legacy: dict,
) -> tuple[Person, Host] | tuple[None, None]:
    """
    Reincarnate an echo into a new person.

    Returns: (new_person, new_host) or (None, None) if no compatible person found.
    """
    new_person = find_reincarnation_host(echo, world)
    if not new_person:
        return None, None

    old_person_id = None
    for p in world.persons:
        if hasattr(p, 'echo_id') and p.echo_id == echo.id and p.type == "player":
            old_person_id = p.id
            break

    if old_person_id:
        old_person = world.get_person(old_person_id)
        if old_person:
            old_person.type = "npc"
            old_person.vitality = 100.0

    new_person.type = "player"
    new_person.echo_id = echo.id

    for attr in ["essence_profile", "known_tags", "genealogical_lineage"]:
        if hasattr(echo, attr):
            setattr(echo, attr, transformed_legacy.get(attr, getattr(echo, attr)))

    echo.reincarnation_count += 1

    host = Host(person_id=new_person.id, echo_id=echo.id)
    if not hasattr(world, 'hosts'):
        world.hosts = []
    world.hosts.append(host)

    return new_person, host


def is_in_transition(world: World) -> bool:
    """Check if the world is in a transition turn (player cannot act)."""
    if not hasattr(world, 'transition_turn'):
        return False
    return world.transition_turn > 0


def start_transition_turn(world: World) -> None:
    """Start a transition turn after echo death."""
    world.transition_turn = world.clock.action_tick + 1


def end_transition_turn(world: World) -> None:
    """End the transition turn."""
    world.transition_turn = 0