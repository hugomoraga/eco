"""
host.py — Host (DEPRECATED, use PlayerPerson)
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class Host(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    person_id: str
    echo_id: str
    will: float = 50.0
    presence: float = 50.0
    action_history: list[str] = Field(default_factory=list)
    last_action_turn: dict[str, int] = Field(default_factory=dict)
    active_circle_id: str | None = None
    actions_this_turn: int = 0
    is_active: bool = True

    def record_action(self, action: str, turn: int) -> None:
        self.action_history.append(action)
        self.last_action_turn[action] = turn
        self.actions_this_turn += 1

    def reset_turn_actions(self) -> None:
        self.actions_this_turn = 0
