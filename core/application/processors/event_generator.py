from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, ClassVar

from adapters.i18n import t
from core.application.processors.random import SeededRandom

if TYPE_CHECKING:
    from core.ai.base import AIAdapter
    from core.ports.logger import Logger


class _NoOpLogger:
    """No-op logger for when logging is not configured."""

    def debug(self, msg: str, **kwargs: Any) -> None: pass
    def info(self, msg: str, **kwargs: Any) -> None: pass
    def warning(self, msg: str, **kwargs: Any) -> None: pass
    def error(self, msg: str, **kwargs: Any) -> None: pass
    def exception(self, msg: str, **kwargs: Any) -> None: pass


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
    def __init__(self, adapter: AIAdapter | None = None, seed: int = 42, pool=None, log: Logger | None = None):
        self.adapter = adapter
        self.rng = SeededRandom.get_instance(seed)
        self.pool = pool
        self._log = log if log is not None else _NoOpLogger()
        self.unknown_tags_log: list[dict] = []

    def generate(self, context: dict) -> GameEvent:
        """Generate an event using pool or fallback to AI adapter."""
        if self.pool is not None:
            return self._generate_from_pool(context)

        if self.adapter is not None:
            return self._generate_from_adapter(context)
        else:
            return self._generate_fallback(context)

    def _generate_from_pool(self, context: dict) -> GameEvent:
        """Generate event using the event pool (YAML)."""
        world_state = context.get("world_state", {})
        category = self.pool.select_category(world_state)
        event_id = self.pool.select_event(category)

        if not event_id:
            self._log.warning("event_generation", stage="no_event_from_pool", category=category)
            return self._generate_fallback(context)

        event_data = self.pool.get_event_data(event_id)
        if not event_data:
            self._log.warning("event_generation", stage="no_event_data", event_id=event_id)
            return self._generate_fallback(context)

        event_data["id"] = event_id

        title = t(f"events:{event_id}:title")
        summary = t(f"events:{event_id}:summary")
        if title == f"events:{event_id}:title" and self.adapter is not None:
            title, summary = self._enrich_text(event_data, context)

        essence_weights = event_data.get("essence_weights", {})
        causes = list(essence_weights.keys())

        choices = self._validate_choices(event_data.get("choices", []))

        self._log.info("event_generated", event_id=event_id, category=category, title=title[:50] if title else "unknown")
        return GameEvent(
            event_id=event_id,
            title=title,
            summary=summary,
            causes=causes,
            choices=choices,
            canonical=all(c.get("canonical", True) for c in choices),
        )

    def _enrich_text(self, event_data: dict, context: dict) -> tuple[str, str]:
        """Use AI adapter to enrich title/summary while keeping structure from pool."""
        self._log.debug("event_enrich", stage="start", event_id=event_data.get("id", "unknown"), adapter=type(self.adapter).__name__)
        enrichment_context = {
            "event_data": event_data,
            "language": context.get("language", "es"),
            "purpose": "enrich_title_and_summary",
        }

        try:
            response = self.adapter.generate_event(enrichment_context)
            if response.success and isinstance(response.data, dict):
                title = response.data.get("title") or response.data.get("event_title")
                summary = response.data.get("summary")
                if title and summary:
                    self._log.debug("event_enrich", stage="success", event_id=event_data.get("id", "unknown"))
                    return title, summary
        except Exception as e:
            self._log.exception("event_enrich", stage="exception", event_id=event_data.get("id", "unknown"), error=str(e))

        event_id = event_data.get("id", "")
        if event_id:
            title = t(f"events:{event_id}:title")
            summary = t(f"events:{event_id}:summary")
            if title != f"events:{event_id}:title":
                self._log.debug("event_enrich", stage="i18n_fallback", event_id=event_id)
                return title, summary

        self._log.warning("event_enrich", stage="no_fallback", event_id=event_id)
        return event_data.get("title", ""), event_data.get("summary", "")

    def _validate_choices(self, choices: list[dict]) -> list[dict]:
        """Validate effect_tags in choices with EffectTagValidator."""
        validated_choices = []
        for choice in choices:
            effect_tags = choice.get("effect_tags", [])
            validated_tags = []
            is_canonical = True

            for tag in effect_tags:
                is_canon, exists = EffectTagValidator.validate(tag)
                if not exists:
                    self._log_unknown_tag(tag, {})
                elif not is_canon:
                    is_canonical = False
                validated_tags.append(tag)

            validated_choices.append({
                "label": choice.get("label", "Unknown"),
                "effect_tags": validated_tags,
                "canonical": is_canonical,
            })

        return validated_choices

    def _generate_from_adapter(self, context: dict) -> GameEvent:
        """Generate event using AI adapter (original behavior)."""
        response = self.adapter.generate_event(context)

        if response.success and response.data:
            return self._create_event(response.data, context)
        else:
            return self._generate_fallback(context)

    def _create_event(self, data: dict, context: dict) -> GameEvent:
        title = data.get("event_title", "")
        if not title:
            title = t("events:unnamed", default="Evento sin nombre")
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
                "label": choice.get("label", t("choices:unknown", default="Opción desconocida")),
                "effect_tags": validated_tags,
                "canonical": is_canonical,
            }
            valid_choices.append(validated_choices)

        return GameEvent(
            event_id=str(uuid.uuid4()),
            title=title,
            summary=summary,
            causes=causes,
            choices=valid_choices,
            canonical=all(c.get("canonical", True) for c in valid_choices),
        )


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
