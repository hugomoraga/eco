from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain import World


class GoalType(Enum):
    PROGRESS = "progress"
    MAINTAIN = "maintain"
    ACCUMULATE = "accumulate"
    SURVIVE = "survive"


@dataclass
class GoalProgress:
    current: float
    target: float
    percentage: float


class Goal(ABC):
    def __init__(self, goal_id: str, owner_id: str, owner_name: str, turn_limit: int):
        self.goal_id = goal_id
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.turn_limit = turn_limit

    @property
    @abstractmethod
    def goal_type(self) -> GoalType: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def short_description(self) -> str: ...

    @property
    def is_player(self) -> bool:
        return self.owner_id == "player"

    @abstractmethod
    def evaluate(self, world: World, current_turn: int) -> float: ...

    def remaining_turns(self, current_turn: int) -> int:
        return max(0, self.turn_limit - current_turn)

    def progress(self, world: World, current_turn: int) -> GoalProgress:
        return GoalProgress(
            current=self._get_current(world),
            target=self._get_target(),
            percentage=self.evaluate(world, current_turn),
        )

    def progress_bar(self, world: World, current_turn: int, width: int = 10) -> str:
        pct = self.evaluate(world, current_turn)
        filled = int(pct * width)
        empty = width - filled
        return "█" * filled + "░" * empty

    @abstractmethod
    def _get_current(self, world: World) -> float: ...

    @abstractmethod
    def _get_target(self) -> float: ...

    def to_dict(self) -> dict:
        return {
            "goal_id": self.goal_id,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "goal_type": self.goal_type.value,
            "description": self.description,
            "short_description": self.short_description,
            "turn_limit": self.turn_limit,
        }


class ProgressGoal(Goal):
    """Reach a target value before turn limit. E.g., 'Fundar 5 círculos'."""

    def __init__(
        self,
        goal_id: str,
        owner_id: str,
        owner_name: str,
        turn_limit: int,
        metric: str,
        target: float,
        description: str,
    ):
        super().__init__(goal_id, owner_id, owner_name, turn_limit)
        self.metric = metric
        self.target = target
        self._description = description

    @property
    def goal_type(self) -> GoalType:
        return GoalType.PROGRESS

    @property
    def description(self) -> str:
        return self._description

    @property
    def short_description(self) -> str:
        current = self._get_current_from_world()
        return f"{self.metric}: {int(current)}/{int(self.target)}"

    def evaluate(self, world: World, current_turn: int) -> float:
        remaining = self.remaining_turns(current_turn)
        if remaining <= 0:
            current = self._get_current(world)
            return 1.0 if current >= self.target else 0.0

        current = self._get_current(world)
        if current >= self.target:
            return 1.0

        time_ratio = 1.0 - (remaining / self.turn_limit)
        progress_ratio = current / self.target
        return progress_ratio * (1.0 - time_ratio * 0.3)

    def _get_current(self, world: World) -> float:
        return self._get_current_from_world(world)

    def _get_target(self) -> float:
        return self.target

    def _get_current_from_world(self, world: World | None = None) -> float:
        if world is None:
            return 0.0

        if self.metric == "circles":
            return float(len([c for c in world.circles if c.status.value == "active"]))
        elif self.metric == "legitimacy":
            return world.legitimacy
        elif self.metric == "pressure":
            return world.pressure
        elif self.metric == "resources":
            return world.resources_global
        elif self.metric == "vitality":
            player = world.get_player_person()
            return player.vitality if player else 0.0
        elif self.metric == "influence":
            return float(len(world.circles))
        elif self.metric == "events":
            return float(len(world.manifestos))
        return 0.0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["metric"] = self.metric
        d["target"] = self.target
        return d


class MaintainGoal(Goal):
    """Keep a metric above/below threshold. E.g., 'Mantener presión > 90'."""

    def __init__(
        self,
        goal_id: str,
        owner_id: str,
        owner_name: str,
        turn_limit: int,
        metric: str,
        operator: str,
        threshold: float,
        description: str,
    ):
        super().__init__(goal_id, owner_id, owner_name, turn_limit)
        self.metric = metric
        self.operator = operator
        self.threshold = threshold
        self._description = description

    @property
    def goal_type(self) -> GoalType:
        return GoalType.MAINTAIN

    @property
    def goal_type_str(self) -> str:
        return "maintain"

    @property
    def description(self) -> str:
        return self._description

    @property
    def short_description(self) -> str:
        self._get_current_from_world()
        op_symbol = ">" if self.operator == "gt" else "<"
        return f"{self.metric} {op_symbol} {int(self.threshold)}"

    def evaluate(self, world: World, current_turn: int) -> float:
        self.remaining_turns(current_turn)
        current = self._get_current(world)

        if self.operator == "gt":
            if current >= self.threshold:
                return 1.0
            return current / self.threshold
        elif self.operator == "lt":
            if current <= self.threshold:
                return 1.0
            return max(0.0, 1.0 - (current - self.threshold) / self.threshold)

        return 0.5

    def _get_current(self, world: World) -> float:
        return self._get_current_from_world(world)

    def _get_target(self) -> float:
        return self.threshold

    def _get_current_from_world(self, world: World | None = None) -> float:
        if world is None:
            return 0.0

        if self.metric == "legitimacy":
            return world.legitimacy
        elif self.metric == "pressure":
            return world.pressure
        elif self.metric == "resources":
            return world.resources_global
        elif self.metric == "clarity":
            echo = world.get_active_echo()
            return echo.clarity if echo else 0.0
        return 0.0


class AccumulateGoal(Goal):
    """Accumulate resources/circles over time. E.g., 'Acumular 50 recursos'."""

    def __init__(
        self,
        goal_id: str,
        owner_id: str,
        owner_name: str,
        turn_limit: int,
        metric: str,
        target: float,
        description: str,
    ):
        super().__init__(goal_id, owner_id, owner_name, turn_limit)
        self.metric = metric
        self.target = target
        self._description = description

    @property
    def goal_type(self) -> GoalType:
        return GoalType.ACCUMULATE

    @property
    def goal_type_str(self) -> str:
        return "accumulate"

    @property
    def description(self) -> str:
        return self._description

    @property
    def short_description(self) -> str:
        return f"{self.metric}: {int(self._get_current_from_world())}/{int(self.target)}"

    def evaluate(self, world: World, current_turn: int) -> float:
        remaining = self.remaining_turns(current_turn)
        current = self._get_current(world)

        if current >= self.target:
            return 1.0

        if remaining <= 0:
            return current / self.target

        progress_ratio = current / self.target
        time_spent_ratio = 1.0 - (remaining / self.turn_limit)

        if time_spent_ratio <= 0:
            return 0.0

        expected_rate = self.target / self.turn_limit
        actual_rate = current / max(1, self.turn_limit - remaining)
        rate_efficiency = min(1.0, actual_rate / expected_rate) if expected_rate > 0 else 0.0

        return progress_ratio * 0.6 + rate_efficiency * 0.4

    def _get_current(self, world: World) -> float:
        return self._get_current_from_world(world)

    def _get_target(self) -> float:
        return self.target

    def _get_current_from_world(self, world: World | None = None) -> float:
        if world is None:
            return 0.0

        if self.metric == "resources":
            return world.resources_global
        elif self.metric == "legitimacy":
            return world.legitimacy
        elif self.metric == "circles":
            return float(len([c for c in world.circles if c.status.value == "active"]))
        elif self.metric == "influence":
            total = 0.0
            for c in world.circles:
                total += c.influence
            return total
        elif self.metric == "food":
            return world.resources.get("food", 0.0)
        elif self.metric == "knowledge":
            return world.resources.get("knowledge", 0.0)
        return 0.0


class SurviveGoal(Goal):
    """Survive for N turns. E.g., 'Sobrevivir 15 turnos'."""

    def __init__(
        self,
        goal_id: str,
        owner_id: str,
        owner_name: str,
        turn_limit: int,
        turns_needed: int | None = None,
    ):
        super().__init__(goal_id, owner_id, owner_name, turn_limit)
        self.turns_needed = turns_needed or turn_limit

    @property
    def goal_type(self) -> GoalType:
        return GoalType.SURVIVE

    @property
    def goal_type_str(self) -> str:
        return "survive"

    @property
    def description(self) -> str:
        return f"Sobrevivir {self.turns_needed} turnos"

    @property
    def short_description(self) -> str:
        return f"Turnos: {self.turns_needed}"

    def evaluate(self, world: World, current_turn: int) -> float:
        turns_elapsed = current_turn
        if turns_elapsed >= self.turns_needed:
            return 1.0
        return turns_elapsed / self.turns_needed

    def _get_current(self, world: World) -> float:
        return 0.0

    def _get_target(self) -> float:
        return float(self.turns_needed)
