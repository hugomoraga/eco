from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import Circle, Echo, World, NPC


def process_circle_tick(circle: Circle, world: World, rng) -> list[str]:
    """Process a single world tick for a circle. Returns list of activities."""
    activities = []

    if circle.status.value == "dissolved":
        return activities

    from game_core.domain.entities import CircleStatus

    if circle.member_count == 0:
        circle.dormant_turns += 1
        if circle.dormant_turns >= 10:
            circle.status = CircleStatus.DISSOLVED
            activities.append(f"{circle.name} dissolved (0 members for 10 turns)")
        else:
            circle.status = CircleStatus.DORMANT
        return activities

    if circle.can_grow() and rng.random() < 0.15:
        activity = attract_echo_to_circle(circle, world)
        if activity:
            activities.append(activity)

    if circle.should_decay() and rng.random() < 0.03:
        activity = remove_lowest_resonance_member(circle, world)
        if activity:
            activities.append(activity)

    if circle.should_splinter() and rng.random() < 0.1:
        activity = splinter_circle(circle, world, rng)
        if activity:
            activities.append(activity)

    return activities


def attract_echo_to_circle(circle: Circle, world: World) -> str | None:
    """Try to attract an echo to the circle."""
    from game_core.domain.entities import EssenceRegistry

    candidates = [
        e for e in world.echoes
        if e.id not in circle.member_ids
    ]

    if not candidates:
        return None

    best_candidate = None
    best_affinity = -1

    for echo in candidates:
        affinity = EssenceRegistry.get_essence_affinity(circle.essence, echo.essence)
        if affinity > best_affinity and affinity > 0.3:
            best_affinity = affinity
            best_candidate = echo

    if best_candidate:
        circle.add_member(best_candidate.id)
        best_candidate.circles.append(circle.id)
        from game_core.domain.entities import CircleEvent
        circle.history.append(CircleEvent(
            type="join",
            turn=world.clock.world_tick,
            echo_id=best_candidate.id,
            details=f"{best_candidate.name or 'Echo'} joined {circle.name}",
        ))
        return f"{best_candidate.name or 'An echo'} joined {circle.name} (influence: {circle.influence:.0f})"

    return None


def remove_lowest_resonance_member(circle: Circle, world: World) -> str | None:
    """Remove the member with lowest resonance from circle."""
    if not circle.member_ids:
        return None

    members = [world.get_echo(eid) for eid in circle.member_ids]
    members = [m for m in members if m]

    if not members:
        return None

    lowest = min(members, key=lambda e: e.get_attribute("resonance").value if e.get_attribute("resonance") else 50.0)

    circle.remove_member(lowest.id)
    if hasattr(lowest, 'circles') and circle.id in lowest.circles:
        lowest.circles.remove(circle.id)

    from game_core.domain.entities import CircleEvent
    circle.history.append(CircleEvent(
        type="decay",
        turn=world.clock.world_tick,
        echo_id=lowest.id,
        details=f"{lowest.name or 'Echo'} left {circle.name}",
    ))

    return f"{lowest.name or 'An echo'} left {circle.name} (low resonance)"


def splinter_circle(circle: Circle, world: World, rng) -> str | None:
    """Split circle into two when it has 6+ members."""
    if circle.member_count < 6:
        return None

    from game_core.circle.name_generator import generate_circle_name_with_fallback

    kept_members = circle.member_ids[:3]
    new_members = circle.member_ids[3:6] if len(circle.member_ids) > 3 else circle.member_ids[3:]

    new_name = generate_circle_name_with_fallback(circle.essence, world.circles)

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

    from game_core.domain.entities import CircleEvent
    circle.history.append(CircleEvent(
        type="splinter",
        turn=world.clock.world_tick,
        details=f"Circle splintered into {new_name}",
    ))

    new_circle.history.append(CircleEvent(
        type="founded",
        turn=world.clock.world_tick,
        details=f"Splintered from {circle.name}",
    ))

    world.circles.append(new_circle)

    return f"{circle.name} splintered → {new_name} ({len(new_members)} members)"


def spawn_npc_in_circle(circle: Circle, world: World, rng) -> str | None:
    """Spawn NPC in circle if conditions are met."""
    if circle.member_count < 3:
        return None

    if rng.random() > 0.2:
        return None

    from game_core.domain.npc_generator import NPCGenerator
    from game_core.ai import MockAdapter

    npc_gen = NPCGenerator(MockAdapter(), seed=rng.randint(0, 99999))
    npc = npc_gen.generate({"essence": circle.essence, "context": "circle_growth"})

    circle.npcs.append(npc.id)
    circle.add_member(npc.id)

    from game_core.domain.entities import CircleEvent
    circle.history.append(CircleEvent(
        type="npc_spawn",
        turn=world.clock.world_tick,
        npc_id=npc.id,
        details=f"NPC {npc.name} spawned in {circle.name}",
    ))

    return npc.id