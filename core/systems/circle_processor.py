"""
circle_processor.py — Circle activity processing.
"""

from __future__ import annotations


def process_circle_activities(world, rng, seed: int, turn: int, ai_adapter, notify, log, log_event) -> None:
    """
    Process circle activities at turn start (spec-28).
    """
    from core.factories import create_npc
    from core.factories import process_circle_tick

    for circle in world.circles:
        activities = process_circle_tick(circle, world, rng)
        for activity in activities:
            notify("on_circle_activity", turn, circle.name, activity)

        if circle.member_count >= 3:
            if len(getattr(circle, 'npcs', [])) < circle.member_count:
                log.debug("npc_creation", turn=turn, circle=circle.name, essence=circle.essence)
                npc = create_npc(ai_adapter, {"essence": circle.essence, "context": "circle_growth"}, seed=seed)
                log.info("npc_created", turn=turn, circle=circle.name, npc_name=npc.name, npc_id=npc.id)
                if not hasattr(circle, 'npcs'):
                    circle.npcs = []
                circle.npcs.append(npc.id)
                if not hasattr(world, 'persons'):
                    world.persons = []
                if npc not in world.persons:
                    world.persons.append(npc)
                notify("on_npc_created", turn, npc.name, npc.role)
                log_event("npc_created", {
                    "npc_id": npc.id,
                    "npc_name": npc.name,
                    "circle_id": circle.id,
                })
