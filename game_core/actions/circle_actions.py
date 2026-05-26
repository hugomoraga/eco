from __future__ import annotations

from typing import TYPE_CHECKING

from game_core.actions.base import Action, ActionContext, ActionResult
from game_core.i18n import t

if TYPE_CHECKING:
    from game_core.domain.entities import Echo, World


class FoundCircle(Action):
    name: str = "found_circle"
    cooldown: int = 5
    social_cost: float = 3.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from game_core.factory import create_circle

        circle = create_circle(
            world=world,
            echo=echo,
            essence=echo.essence,
            ideas=None,
            founding_tick=context.world_tick,
        )

        world.pressure += 1
        world.legitimacy -= 2
        world.clamp_metrics()

        self._apply_temporal_strain(echo, 2.0)
        self.last_used_tick = context.world_tick

        return ActionResult(
            success=True,
            message=t("actions:founded_circle", default=f"Fundó {circle.name}"),
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
        from game_core.domain.entities import CircleEvent, CircleEventType, EssenceRegistry

        if not world.circles:
            return ActionResult(
                success=False,
                message=t("actions:no_circles_to_join", default="No hay círculos para unirse"),
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
                message=t("actions:no_circles_available", default="No hay círculos disponibles para unirse"),
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
                message=t("actions:no_compatible_circles", default="No se encontraron círculos compatibles"),
                state_delta={},
                tags_created=[],
                social_cost=self.social_cost,
            )

        if best_affinity < 0.3:
            return ActionResult(
                success=False,
                message=t("actions:essence_mismatch", default=f"Incompatibilidad de esencia (afinidad: {best_affinity:.2f})"),
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
            message=t("actions:joined_circle", default=f"Se unió a {best_circle.name}"),
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
        from game_core.domain.entities import CircleEvent, CircleEventType

        if not echo.circles:
            return ActionResult(
                success=False,
                message=t("actions:not_member", default="No eres miembro de ningún círculo"),
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
                message=t("actions:circle_not_found", default="Círculo no encontrado"),
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
            message=t("actions:left_circle", default=f"Abandonó {circle.name}"),
            state_delta={"circle_left": circle.id},
            tags_created=[],
            social_cost=self.social_cost,
        )
