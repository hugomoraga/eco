from __future__ import annotations

import uuid

from game_core.actions.base import Action, ActionContext, ActionResult
from game_core.domain.entities import Circle, Echo, World, Manifesto


class FoundCircle(Action):
    name: str = "found_circle"
    cooldown: int = 5
    social_cost: float = 3.0
    tags_required: list[str] = []

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        circle = Circle(
            name=f"Circle of {echo.name or 'the unknown'}",
            echo_id=echo.id,
            essence=echo.essence,
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
        from game_core.domain.essence_effects import EssenceEffects
        from game_core.engine.random import SeededRandom

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

        resonance_attr = echo.get_attribute("resonance")
        resonance = resonance_attr.value if resonance_attr else 50.0
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

        for tag in echo.known_tags[:3]:
            target = targets[propagated % len(targets)]
            tag_key = tag.to_semantic_key()

            affinity_modifier = 1.0
            if hasattr(target, 'essence'):
                affinity = EssenceEffects.get_essence_affinity(echo.essence, target.essence)
                affinity_modifier = 1.0 + (affinity * 0.02)

            if rng.random() < affinity_modifier:
                if hasattr(target, 'ideology_tags'):
                    if tag_key not in target.ideology_tags:
                        target.ideology_tags.append(tag_key)
                        tags_created.append(tag_key)
                        propagated += 1

        self._apply_temporal_strain(echo, 1.5)
        self.last_used_tick = context.world_tick

        return ActionResult(
            success=propagated > 0,
            message=f"Propagated {propagated} ideas to {len(targets)} targets",
            state_delta={"tags_propagated": propagated, "affinity_modifier": affinity_modifier},
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

    ESSENCE_KEYWORDS: dict[str, list[str]] = {
        "anarchism": ["libertad", "autonomia", "horizontal", "estado", "revolucion", "solidaridad"],
        "technocracy": ["conocimiento", "protocolo", "expertos", "ciencia", "eficiencia", "sistema"],
        "absurdism": ["caos", "absurdo", "risa", "vacio", "nonsense", "ironia"],
        "thelema": ["voluntad", "destino", "magia", "gnosis", "individuo", "poder"],
        "ecology": ["naturaleza", "equilibrio", "sustentable", "tierra", "ciclo", "vida"],
    }

    def execute(self, echo: Echo, world: World, context: ActionContext) -> ActionResult:
        from game_core.ai import MockAdapter
        from game_core.i18n import t

        ai_adapter = MockAdapter()
        ai_response = ai_adapter.generate_manifesto(echo.essence, {
            "world_tick": context.world_tick,
            "influence": 10,
        })

        content = ""
        if ai_response.success and ai_response.data:
            content = ai_response.data.get("content", "")

        tags = self._extract_tags(content, echo.essence)

        influence_gain = len(tags) * 5 if tags else 1
        doctrinal_clarity_gain = len(tags) * 0.1

        manifesto = Manifesto(
            id=str(uuid.uuid4()),
            author_echo_id=echo.id,
            content=content,
            tags=tags,
            world_tick_created=context.world_tick,
            essence=echo.essence,
            influence_generated=float(influence_gain),
        )

        world.manifestos.append(manifesto)
        echo.manifestos.append(manifesto.id)

        clarity_attr = echo.get_attribute("clarity")
        if clarity_attr:
            clarity_attr.value = min(100, clarity_attr.value + doctrinal_clarity_gain * 10)

        for faction in world.factions:
            for tag in tags:
                if tag not in faction.ideology_tags:
                    faction.ideology_tags.append(tag)

        self.last_used_tick = context.world_tick

        if tags:
            message = t("actions:write_manifesto:success", n=len(tags))
        else:
            message = t("actions:write_manifesto:no_tags")

        return ActionResult(
            success=True,
            message=message,
            state_delta={
                "manifestos": [manifesto.id],
                "doctrinal_clarity": +doctrinal_clarity_gain,
                "influence": +influence_gain,
            },
            new_entities=[manifesto.id],
            tags_created=tags,
            social_cost=self.social_cost,
        )

    def _extract_tags(self, content: str, essence: str) -> list[str]:
        content_lower = content.lower()
        found_tags = []

        essence_keywords = self.ESSENCE_KEYWORDS.get(essence, [])
        for keyword in essence_keywords:
            if keyword in content_lower:
                tag = f"{essence}:{keyword}"
                if tag not in found_tags:
                    found_tags.append(tag)

        if len(found_tags) < 2:
            for other_essence, keywords in self.ESSENCE_KEYWORDS.items():
                if other_essence == essence:
                    continue
                for keyword in keywords:
                    if keyword in content_lower:
                        tag = f"{other_essence}:{keyword}"
                        if tag not in found_tags:
                            found_tags.append(tag)
                            if len(found_tags) >= 3:
                                break
                if len(found_tags) >= 3:
                    break

        return found_tags[:5]


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