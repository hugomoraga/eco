from __future__ import annotations

import uuid

from core.application.actions.base import Action, ActionContext, ActionResult
from core.domain.entities import Echo, Ideas, World


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
        from adapters.ai import MockAdapter
        from core.domain.entities import Manifesto
        from adapters.i18n import t

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
                idea = Ideas(
                    id=str(uuid.uuid4()),
                    category="concept",
                    name=tag,
                    essence_weights={echo.essence: 1.0},
                )
                if not any(i.to_semantic_key() == idea.to_semantic_key() for i in faction.ideas):
                    faction.ideas.append(idea)

        world.pressure += 3
        world.legitimacy -= 1
        world.clamp_metrics()

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
