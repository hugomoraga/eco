from __future__ import annotations

from game_core.actions.base import Action, ActionContext, ActionResult
from game_core.domain.entities import Circle, Echo, World


class FoundCircle(Action):
    name: str = "found_circle"
    cooldown: int = 5
    social_cost: float = 3.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        circle = Circle(
            name=f"Circle of {echo.name or 'the unknown'}",
            echo_id=echo.id,
            founding_tick=context.world_tick,
            ideology_tags=[tag.to_semantic_key() for tag in echo.known_tags],
            members=1,
            influence=5.0,
        )
        world.circles.append(circle)
        echo.phase = echo.phase.ACTIVE

        self._apply_temporal_strain(echo, 2.0)
        self.last_used_tick = context.world_tick

        return ActionResult(
            success=True,
            message=f"Founded circle: {circle.name}",
            state_delta={"circles_added": 1},
            new_entities=[circle.id],
            tags_created=[],
            social_cost=self.social_cost,
        )


class PropagateIdea(Action):
    name: str = "propagate_idea"
    cooldown: int = 3
    social_cost: float = 2.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from game_core.domain.entities import IdeologicalTag

        propagated = 0
        tags_created = []

        if echo.known_tags:
            target_circle = world.circles[0] if world.circles else None
            if target_circle:
                for tag in echo.known_tags[:2]:
                    if tag.to_semantic_key() not in target_circle.ideology_tags:
                        target_circle.ideology_tags.append(tag.to_semantic_key())
                        tags_created.append(tag.to_semantic_key())
                        propagated += 1

        self._apply_temporal_strain(echo, 1.5)
        self.last_used_tick = context.world_tick

        return ActionResult(
            success=propagated > 0,
            message=f"Propagated {propagated} ideas",
            state_delta={"tags_propagated": propagated},
            tags_created=tags_created,
            social_cost=self.social_cost,
        )


class Talk(Action):
    name: str = "talk"
    cooldown: int = 1
    social_cost: float = 0.5
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message="Talked (stub)",
            state_delta={},
            social_cost=self.social_cost,
        )


class WriteManifesto(Action):
    name: str = "write_manifesto"
    cooldown: int = 10
    social_cost: float = 5.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message="Wrote manifesto (stub)",
            state_delta={},
            social_cost=self.social_cost,
        )


class Sabotage(Action):
    name: str = "sabotage"
    cooldown: int = 8
    social_cost: float = 8.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message="Sabotaged (stub)",
            state_delta={},
            social_cost=self.social_cost,
        )


class Ritualize(Action):
    name: str = "ritualize"
    cooldown: int = 6
    social_cost: float = 4.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message="Ritualized (stub)",
            state_delta={},
            social_cost=self.social_cost,
        )