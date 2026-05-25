from __future__ import annotations

from typing import TYPE_CHECKING

from game_core.actions.base import Action, ActionContext, ActionResult

if TYPE_CHECKING:
    from game_core.domain.entities import Echo, World


class PropagateIdea(Action):
    name: str = "propagate_idea"
    cooldown: int = 3
    social_cost: float = 2.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from game_core.domain.essence_effects import EssenceEffects
        from game_core.systems.random import SeededRandom

        propagated = 0
        tags_created = []

        if not echo.known_tags:
            return ActionResult(
                success=False,
                message="No ideas to propagate",
                state_delta={"tags_propagated": 0},
                tags_created=[],
                social_cost=self.social_cost,
            )

        echo.get_attribute("resonance")
        rng = SeededRandom.get_instance()

        targets = list(world.factions) + list(world.circles)
        if not targets:
            return ActionResult(
                success=False,
                message="No targets to propagate to",
                state_delta={"tags_propagated": 0},
                tags_created=[],
                social_cost=self.social_cost,
            )

        affinity_modifier = 1.0
        for tag in echo.known_tags[:3]:
            target = targets[propagated % len(targets)]
            tag_key = tag.to_semantic_key()

            if hasattr(target, 'essence'):
                affinity = EssenceEffects.get_essence_affinity(echo.essence, target.essence)
                affinity_modifier = 1.0 + (affinity * 0.02)

            if rng.random() < affinity_modifier and hasattr(target, 'ideology_tags'):
                if tag_key not in target.ideology_tags:
                    target.ideology_tags.append(tag_key)
                    tags_created.append(tag_key)
                    propagated += 1

        if propagated > 0:
            world.pressure += 2 * propagated
            world.legitimacy -= 1
            world.clamp_metrics()

        self._apply_temporal_strain(echo, 1.5)
        self.last_used_tick = context.world_tick

        return ActionResult(
            success=propagated > 0,
            message=f"Propagated {propagated} ideas to {len(targets)} targets",
            state_delta={"tags_propagated": propagated, "affinity_modifier": affinity_modifier},
            tags_created=tags_created,
            social_cost=self.social_cost,
        )


class Sabotage(Action):
    name: str = "sabotage"
    cooldown: int = 8
    social_cost: float = 8.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        world.legitimacy -= 5
        world.resources_global -= 5
        world.pressure += 8
        world.clamp_metrics()

        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message="Sabotaged infrastructure",
            state_delta={},
            social_cost=self.social_cost,
        )


class Ritualize(Action):
    name: str = "ritualize"
    cooldown: int = 6
    social_cost: float = 4.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from game_core.domain.entities import CircleEvent, CircleEventType

        world.pressure -= 3
        world.legitimacy -= 1
        world.clamp_metrics()

        if echo.circles:
            circle_id = echo.circles[0]
            circle = world.get_circle(circle_id)
            if circle:
                circle.history.append(CircleEvent(
                    type=CircleEventType.RITUAL,
                    turn=context.world_tick,
                    echo_id=echo.id,
                    details=f"Ritual performed by {echo.name or 'Echo'}",
                ))

        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message="Ritual completed",
            state_delta={},
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
