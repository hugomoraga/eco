from __future__ import annotations

from typing import TYPE_CHECKING

from core.application.actions.base import Action, ActionContext, ActionResult
from adapters.i18n import t
from core.utils.logger import get_logger

if TYPE_CHECKING:
    from core.domain.entities import Echo, World

log = get_logger(__name__)


class FoundCircle(Action):
    name: str = "found_circle"
    cooldown: int = 5
    social_cost: float = 3.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.factories import create_circle

        circle = create_circle(
            world=world,
            echo=echo,
            essence=echo.essence,
            ideas=None,
            founding_tick=context.world_tick,
        )

        old_pressure = world.pressure
        old_legitimacy = world.legitimacy

        world.pressure += 1
        world.legitimacy -= 2
        world.clamp_metrics()

        self._apply_temporal_strain(echo, 2.0)
        self.last_used_tick = context.world_tick

        log.info("action_found_circle", action=self.name, echo_name=echo.name, world_tick=context.world_tick,
                 circle_id=circle.id, circle_name=circle.name, essence=circle.essence,
                 pressure_change={"before": old_pressure, "after": world.pressure},
                 legitimacy_change={"before": old_legitimacy, "after": world.legitimacy})

        return ActionResult(
            success=True,
            message=t("actions:founded_circle", name=circle.name),
            state_delta={"circles_added": 1},
            new_entities=[circle.id],
            tags_created=[],
            social_cost=self.social_cost,
        )


class JoinCircle(Action):
    name: str = "join_circle"
    cooldown: int = 3
    social_cost: float = 2.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.domain.entities import CircleEvent, CircleEventType, EssenceRegistry

        if not world.circles:
            return ActionResult(
                success=False,
                message=t("actions:no_circles_to_join"),
                state_delta={},
                tags_created=[],
                social_cost=self.social_cost,
            )

        candidate_circles = [
            c for c in world.circles
            if c.status.value != "dissolved"
            and c.id not in echo.circles
        ]

        if not candidate_circles:
            return ActionResult(
                success=False,
                message=t("actions:no_circles_available"),
                state_delta={},
                tags_created=[],
                social_cost=self.social_cost,
            )

        best_circle = None
        best_affinity = -1

        for circle in candidate_circles:
            if echo.essence == circle.essence:
                affinity = 50.0
            else:
                affinity_forward = EssenceRegistry.get_affinity(echo.essence, circle.essence)
                affinity_back = EssenceRegistry.get_affinity(circle.essence, echo.essence)
                affinity = max(affinity_forward, affinity_back)
            if affinity > best_affinity:
                best_affinity = affinity
                best_circle = circle

        if not best_circle:
            return ActionResult(
                success=False,
                message=t("actions:no_compatible_circles"),
                state_delta={},
                tags_created=[],
                social_cost=self.social_cost,
            )

        if best_affinity < 0.3:
            return ActionResult(
                success=False,
                message=t("actions:essence_mismatch"),
                state_delta={},
                tags_created=[],
                social_cost=self.social_cost,
            )

        best_circle.add_member(echo.id)
        echo.circles.append(best_circle.id)

        best_circle.history.append(CircleEvent(
            type=CircleEventType.JOIN,
            turn=context.world_tick,
            echo_id=echo.id,
            details=f"{echo.name or 'Echo'} joined {best_circle.name}",
        ))

        self.last_used_tick = context.world_tick

        return ActionResult(
            success=True,
            message=t("actions:joined_circle", circle_name=best_circle.name),
            state_delta={"circle_joined": best_circle.id, "circle_name": best_circle.name},
            tags_created=[],
            social_cost=self.social_cost,
        )


class LeaveCircle(Action):
    name: str = "leave_circle"
    cooldown: int = 2
    social_cost: float = 1.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.domain.entities import CircleEvent, CircleEventType

        if not echo.circles:
            return ActionResult(
                success=False,
                message=t("actions:not_member"),
                state_delta={},
                tags_created=[],
                social_cost=self.social_cost,
            )

        circle_id = echo.circles[0]
        circle = world.get_circle(circle_id)

        if not circle:
            echo.circles.remove(circle_id)
            return ActionResult(
                success=False,
                message=t("actions:circle_not_found"),
                state_delta={},
                tags_created=[],
                social_cost=self.social_cost,
            )

        circle.remove_member(echo.id)
        echo.circles.remove(circle_id)

        circle.history.append(CircleEvent(
            type=CircleEventType.LEAVE,
            turn=context.world_tick,
            echo_id=echo.id,
            details=f"{echo.name or 'Echo'} left {circle.name}",
        ))

        self.last_used_tick = context.world_tick

        return ActionResult(
            success=True,
            message=t("actions:left_circle", circle_name=circle.name),
            state_delta={"circle_left": circle.id},
            tags_created=[],
            social_cost=self.social_cost,
        )
