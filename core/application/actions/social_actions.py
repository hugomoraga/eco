"""Social actions for ECO game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from adapters.i18n import t
from core.application.actions.base import Action, ActionContext, ActionResult

if TYPE_CHECKING:
    from core.domain import Echo, World


# ─── Action Metadata ──────────────────────────────────────────────────────────

# ACTION_DAMAGE_MAP is now imported from core.shared.actions


# ─── Propagate Idea ────────────────────────────────────────────────────────────


class PropagateIdea(Action):
    name: str = "propagate_idea"
    cooldown: int = 3
    social_cost: float = 2.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.application.processors.random import SeededRandom
        from core.domain.rules.essence_effects import EssenceEffects

        propagated = 0
        tags_created = []

        if not echo.known_tags:
            return ActionResult(
                success=False,
                message=t("actions:no_ideas_to_propagate"),
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
                message=t("actions:no_targets"),
                state_delta={"tags_propagated": 0},
                tags_created=[],
                social_cost=self.social_cost,
            )

        affinity_modifier = 1.0
        for tag in echo.known_tags[:3]:
            target = targets[propagated % len(targets)]
            tag_key = tag.to_semantic_key()

            if hasattr(target, "essence"):
                affinity = EssenceEffects.get_essence_affinity(echo.essence, target.essence)
                affinity_modifier = 1.0 + (affinity * 0.02)

            if rng.random() < affinity_modifier and hasattr(target, "ideology_tags"):
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
            message=t("actions:propagated_ideas", count=propagated, target_count=len(targets)),
            state_delta={"tags_propagated": propagated, "affinity_modifier": affinity_modifier},
            tags_created=tags_created,
            social_cost=self.social_cost,
        )


# ─── Sabotage ──────────────────────────────────────────────────────────────────


class Sabotage(Action):
    name: str = "sabotage"
    cooldown: int = 8
    social_cost: float = 8.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        old_pressure = world.pressure
        old_legitimacy = world.legitimacy
        old_resources = world.resources_global

        world.legitimacy -= 5
        world.resources_global -= 5
        world.pressure += 8
        world.clamp_metrics()

        self.last_used_tick = context.world_tick

        return ActionResult(
            success=True,
            message=t("actions:sabotage"),
            state_delta={},
            social_cost=self.social_cost,
        )


# ─── Ritualize ─────────────────────────────────────────────────────────────────


class Ritualize(Action):
    name: str = "ritualize"
    cooldown: int = 6
    social_cost: float = 4.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.domain import CircleEvent, CircleEventType

        world.pressure -= 3
        world.legitimacy -= 1
        world.clamp_metrics()

        if echo.circles:
            circle_id = echo.circles[0]
            circle = world.get_circle(circle_id)
            if circle:
                circle.history.append(
                    CircleEvent(
                        type=CircleEventType.RITUAL,
                        turn=context.world_tick,
                        echo_id=echo.id,
                        details=f"Ritual performed by {echo.name or 'Echo'}",
                    )
                )

        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message=t("actions:ritual_completed"),
            state_delta={},
            social_cost=self.social_cost,
        )


# ─── Talk ──────────────────────────────────────────────────────────────────────


class Talk(Action):
    name: str = "talk"
    cooldown: int = 1
    social_cost: float = 0.5
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        self.last_used_tick = context.world_tick
        return ActionResult(
            success=True,
            message=t("actions:talked"),
            state_delta={},
            social_cost=self.social_cost,
        )


# ─── Spread Rumor (new) ────────────────────────────────────────────────────────


class SpreadRumor(Action):
    name: str = "spread_rumor"
    cooldown: int = 4
    social_cost: float = 3.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.application.processors.random import SeededRandom

        rng = SeededRandom.get_instance()
        success_chance = 0.5 + (echo.influence / 200)

        if rng.random() < success_chance:
            old_pressure = world.pressure
            old_legitimacy = world.legitimacy

            world.pressure += 5
            world.legitimacy -= 2
            world.clamp_metrics()
            self._apply_temporal_strain(echo, 2.0)
            self.last_used_tick = context.world_tick

            return ActionResult(
                success=True,
                message=t("actions:rumors_spread"),
                state_delta={"pressure_delta": 5, "legitimacy_delta": -2},
                social_cost=self.social_cost,
            )
        else:
            world.legitimacy -= 1
            world.clamp_metrics()
            self.last_used_tick = context.world_tick
            return ActionResult(
                success=False,
                message=t("actions:rumors_fizzled"),
                state_delta={"legitimacy_delta": -1},
                social_cost=self.social_cost,
            )


# ─── Recruit Follower (new) ────────────────────────────────────────────────────


class RecruitFollower(Action):
    name: str = "recruit_follower"
    cooldown: int = 5
    social_cost: float = 4.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.application.processors.random import SeededRandom

        if not echo.circles:
            return ActionResult(
                success=False,
                message=t("actions:need_circle_to_recruit"),
                state_delta={},
                social_cost=self.social_cost,
            )

        rng = SeededRandom.get_instance()
        circle = world.get_circle(echo.circles[0])
        if not circle:
            return ActionResult(
                success=False,
                message=t("actions:circle_not_found"),
                state_delta={},
                social_cost=self.social_cost,
            )

        success_chance = 0.4 + (echo.influence / 150)

        if rng.random() < success_chance:
            circle.member_count += 1
            echo.influence += 2
            world.pressure += 1
            world.clamp_metrics()
            self._apply_temporal_strain(echo, 3.0)
            self.last_used_tick = context.world_tick
            return ActionResult(
                success=True,
                message=t("actions:recruited"),
                state_delta={"new_members": 1, "influence_delta": 2},
                social_cost=self.social_cost,
            )
        else:
            world.legitimacy -= 1
            world.clamp_metrics()
            self.last_used_tick = context.world_tick
            return ActionResult(
                success=False,
                message=t("actions:no_one_interested"),
                state_delta={"legitimacy_delta": -1},
                social_cost=self.social_cost,
            )


# ─── Negotiate (new) ────────────────────────────────────────────────────────────


class Negotiate(Action):
    name: str = "negotiate"
    cooldown: int = 6
    social_cost: float = 3.5
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.application.processors.random import SeededRandom

        rng = SeededRandom.get_instance()
        success_chance = 0.5 + (echo.influence / 200)

        if rng.random() < success_chance:
            resource_gain = rng.randint(5, 15)
            world.resources_global += resource_gain
            world.legitimacy += 2
            world.clamp_metrics()
            self._apply_temporal_strain(echo, 2.5)
            self.last_used_tick = context.world_tick
            return ActionResult(
                success=True,
                message=t("actions:negotiated"),
                state_delta={"resources_delta": resource_gain, "legitimacy_delta": 2},
                social_cost=self.social_cost,
            )
        else:
            world.pressure += 2
            world.clamp_metrics()
            self.last_used_tick = context.world_tick
            return ActionResult(
                success=False,
                message=t("actions:negotiations_failed"),
                state_delta={"pressure_delta": 2},
                social_cost=self.social_cost,
            )


# ─── Ritual (new - powerful version) ───────────────────────────────────────────


class Ritual(Action):
    name: str = "ritual"
    cooldown: int = 10
    social_cost: float = 6.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from core.application.processors.random import SeededRandom
        from core.domain import CircleEvent, CircleEventType

        rng = SeededRandom.get_instance()
        success_chance = 0.6 + (echo.influence / 250)

        if rng.random() < success_chance:
            world.pressure -= 8
            world.legitimacy += 3
            world.resources_global += 5
            world.clamp_metrics()

            if echo.circles:
                circle_id = echo.circles[0]
                circle = world.get_circle(circle_id)
                if circle:
                    circle.history.append(
                        CircleEvent(
                            type=CircleEventType.RITUAL,
                            turn=context.world_tick,
                            echo_id=echo.id,
                            details=f"Powerful ritual by {echo.name or 'Echo'}",
                        )
                    )
                    circle.coherence = min(100, circle.coherence + 5)

            self._apply_temporal_strain(echo, 5.0)
            self.last_used_tick = context.world_tick
            return ActionResult(
                success=True,
                message=t("actions:powerful_ritual"),
                state_delta={
                    "pressure_delta": -8,
                    "legitimacy_delta": 3,
                    "resources_delta": 5,
                },
                social_cost=self.social_cost,
            )
        else:
            world.pressure += 4
            world.legitimacy -= 3
            world.clamp_metrics()
            self._apply_temporal_strain(echo, 4.0)
            self.last_used_tick = context.world_tick
            return ActionResult(
                success=False,
                message=t("actions:ritual_backfired"),
                state_delta={
                    "pressure_delta": 4,
                    "legitimacy_delta": -3,
                },
                social_cost=self.social_cost,
            )
