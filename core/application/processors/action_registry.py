"""
action_registry.py — Registry of all game actions.
Eliminates duplication between run() and execute_action().
"""

from core.application.actions.circle_actions import FoundCircle, JoinCircle, LeaveCircle
from core.application.actions.manifesto_actions import WriteManifesto
from core.application.actions.social_actions import (
    Negotiate,
    PropagateIdea,
    RecruitFollower,
    Ritual,
    Ritualize,
    Sabotage,
    SpreadRumor,
    Talk,
)


ACTION_CLASSES: dict[str, type] = {
    "found_circle": FoundCircle,
    "join_circle": JoinCircle,
    "leave_circle": LeaveCircle,
    "propagate_idea": PropagateIdea,
    "write_manifesto": WriteManifesto,
    "sabotage": Sabotage,
    "ritualize": Ritualize,
    "talk": Talk,
    "spread_rumor": SpreadRumor,
    "recruit_follower": RecruitFollower,
    "negotiate": Negotiate,
    "ritual": Ritual,
}


def get_action(action_name: str) -> type | None:
    """Get action class by name."""
    return ACTION_CLASSES.get(action_name)


def get_available_actions() -> list[str]:
    """Get list of available action names."""
    return list(ACTION_CLASSES.keys())
