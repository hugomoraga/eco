"""
npc_processor.py — NPC turn processing.
"""

from __future__ import annotations


def process_npc_turns(
    world, seed: int, turn: int, npc_executor, ai_adapter, notify, log, log_event
) -> None:
    """
    Process NPC turns at start of each turn (before player action).
    """
    from adapters.autoplayer.npc_engine import NPCEngine, process_npc_turn

    try:
        npcs = [p for p in world.persons if p.type == "npc"]
        if not npcs:
            return

        engine = NPCEngine(seed=seed)

        top_n = 5
        sorted_npcs = sorted(npcs, key=lambda p: p.influence, reverse=True)
        top_npcs = sorted_npcs[:top_n]
        rest_npcs = sorted_npcs[top_n:]

        npc_actions_log = []
        for npc in npcs:
            result = process_npc_turn(
                npc=npc,
                world=world,
                engine=engine,
                executor=npc_executor,
                world_tick=world.clock.world_tick,
            )
            if result:
                npc_actions_log.append(
                    {
                        "npc_id": npc.id,
                        "npc_name": npc.name,
                        "action": result.action,
                        "success": result.success,
                        "message": result.message,
                        "pressure_change": result.pressure_change,
                        "legitimacy_change": result.legitimacy_change,
                        "influence": npc.influence,
                    }
                )

        if npc_actions_log:
            total_pressure = sum(a["pressure_change"] for a in npc_actions_log)
            total_legitimacy = sum(a["legitimacy_change"] for a in npc_actions_log)

            top_actions = sorted(npc_actions_log, key=lambda a: a["influence"], reverse=True)[
                :top_n
            ]
            for action in top_actions:
                notify(
                    "on_npc_action", turn, action["npc_name"], action["action"], action["message"]
                )
                log_event("npc_action", action)

            if rest_npcs:
                rest_count = len(rest_npcs)
                log_event(
                    "npc_batch",
                    {
                        "count": rest_count,
                        "total_pressure_change": total_pressure,
                        "total_legitimacy_change": total_legitimacy,
                    },
                )
    except Exception as e:
        log.error(
            "process_npc_turns_failed",
            turn=turn,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
