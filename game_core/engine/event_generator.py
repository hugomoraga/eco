from __future__ import annotations

import uuid
from typing import ClassVar

from game_core.ai.base import AIAdapter, AIResponse
from game_core.engine.random import SeededRandom


class EffectTagValidator:
    CANONICAL_TAGS: ClassVar[set[str]] = {
        "increase_unrest",
        "increase_technocracy",
        "increase_cult_risk",
        "increase_memory_decay",
        "increase_ideological_drift",
        "increase_absurdism",
        "increase_thelema",
        "lower_productivity",
        "increase_surveillance",
        "spawn_faction",
        "increase_anarchism",
        "increase_ecology",
    }

    EMERGENT_TAGS: ClassVar[dict[str, list[str]]] = {
        "collective_memory_bleeding": ["memory_decay", "ideological_drift", "identity_fragmentation"],
        "ritualized_algorithms": ["technocracy", "cult_risk", "institutional_drift"],
        "shared_temporal_echo": ["memory", "ideological_drift", "identity_fragmentation"],
    }

    @classmethod
    def validate(cls, tag: str) -> tuple[bool, bool]:
        canonical = tag in cls.CANONICAL_TAGS
        if canonical:
            return True, True

        if tag in cls.EMERGENT_TAGS:
            return False, True

        return False, False

    @classmethod
    def get_neighbors(cls, emergent_tag: str) -> list[tuple[str, float]]:
        neighbors = cls.EMERGENT_TAGS.get(emergent_tag, [])
        return [(n, 0.6) for n in neighbors]


class GameEvent:
    def __init__(
        self,
        event_id: str,
        title: str,
        summary: str,
        causes: list[str],
        choices: list[dict],
        canonical: bool = True,
    ):
        self.id = event_id
        self.title = title
        self.summary = summary
        self.causes = causes
        self.choices = choices
        self.canonical = canonical


class EventGenerator:
    def __init__(self, adapter: AIAdapter, seed: int = 42):
        self.adapter = adapter
        self.rng = SeededRandom.get_instance(seed)
        self.unknown_tags_log: list[dict] = []

    def generate(self, context: dict) -> GameEvent:
        response = self.adapter.generate_event(context)

        if response.success and response.data:
            return self._create_event(response.data, context)
        else:
            return self._generate_fallback(context)

    def _create_event(self, data: dict, context: dict) -> GameEvent:
        title = data.get("event_title", "Unnamed Event")
        summary = data.get("summary", "")
        causes = data.get("causes", [])
        choices = data.get("choices", [])

        valid_choices = []
        for choice in choices:
            effect_tags = choice.get("effect_tags", [])
            validated_tags = []
            is_canonical = True

            for tag in effect_tags:
                is_canon, exists = EffectTagValidator.validate(tag)
                if not exists:
                    self._log_unknown_tag(tag, context)
                elif not is_canon:
                    is_canonical = False
                validated_tags.append(tag)

            validated_choices = {
                "label": choice.get("label", "Unknown"),
                "effect_tags": validated_tags,
                "canonical": is_canonical,
            }
            valid_choices.append(validated_choices)

        event = GameEvent(
            event_id=str(uuid.uuid4()),
            title=title,
            summary=summary,
            causes=causes,
            choices=valid_choices,
            canonical=all(c.get("canonical", True) for c in valid_choices),
        )

        return event

    def _generate_fallback(self, context: dict) -> GameEvent:
        events = [
            GameEvent(
                event_id=str(uuid.uuid4()),
                title="El Laboratorio Abierto",
                summary="Se descubrieron nuevos protocolos de coordinación horizontal.",
                causes=["technocracy", "innovation"],
                choices=[
                    {"label": "Adoptar los protocolos", "effect_tags": ["increase_technocracy"], "canonical": True},
                    {"label": "Documentar sin implementar", "effect_tags": ["increase_memory_decay"], "canonical": True},
                ],
                canonical=True,
            ),
            GameEvent(
                event_id=str(uuid.uuid4()),
                title="La Huelga del Silencio",
                summary="Los obreros dejaron de hablar durante siete días.",
                causes=["unrest", "absurdism"],
                choices=[
                    {"label": "Apoyar el silencio", "effect_tags": ["increase_absurdism"], "canonical": True},
                    {"label": "Convertirlo en ritual", "effect_tags": ["increase_thelema", "increase_cult_risk"], "canonical": True},
                ],
                canonical=True,
            ),
        ]

        return self.rng.choice(events)

    def _log_unknown_tag(self, tag: str, context: dict) -> None:
        neighbors = EffectTagValidator.get_neighbors(tag)
        self.unknown_tags_log.append({
            "tag": tag,
            "context": context,
            "neighbors": neighbors,
            "canonical": False,
        })

    def get_unknown_tags(self) -> list[dict]:
        return self.unknown_tags_log