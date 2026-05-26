"""
goal_processor.py — Goal initialization and evaluation.
"""

from __future__ import annotations


def initialize_goals(npcs: list, max_turns: int, seed: int, notify, log) -> tuple:
    """
    Initialize player and NPC goals.
    Returns (player_goal, npc_goals).
    """
    from core.factories.goal_factory import GoalFactory

    player_goal = GoalFactory.create_player_goals(n_options=1, turn_limit=max_turns)[0]
    notify("on_goal_assigned", "player", player_goal.description)

    npc_goals = []
    top_npcs = sorted(npcs, key=lambda p: p.influence, reverse=True)[:3]
    for npc in top_npcs:
        goal = GoalFactory.create_npc_goal(npc, turn_limit=max_turns, seed=seed)
        npc_goals.append(goal)
        notify("on_goal_assigned", npc.name, goal.description)
        log.debug("npc_goal_assigned", npc_name=npc.name, goal=goal.description)

    return player_goal, npc_goals


def evaluate_goals(player_goal, npc_goals, world, turn: int, notify) -> dict:
    """
    Evaluate all goals and return progress.
    """
    results = {}
    if player_goal:
        progress = player_goal.evaluate(world, turn)
        results["player"] = {"goal": player_goal.description, "progress": progress}
        notify("on_goal_progress", "player", progress, player_goal.progress_bar(world, turn))

    for goal in npc_goals:
        progress = goal.evaluate(world, turn)
        results[goal.owner_name] = {"goal": goal.description, "progress": progress}

    return results
