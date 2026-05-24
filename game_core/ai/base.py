from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AIResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class AIAdapter(ABC):
    @abstractmethod
    def generate_npc(self, context: dict) -> AIResponse:
        pass

    @abstractmethod
    def generate_event(self, context: dict) -> AIResponse:
        pass

    @abstractmethod
    def summarize_history(self, events: list[dict]) -> AIResponse:
        pass

    @abstractmethod
    def interpret_consequences(self, situation: dict) -> AIResponse:
        pass


class MockAdapter(AIAdapter):
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.sequential = self.config.get("sequential", True)
        self.loop = self.config.get("loop", True)
        self._npc_index = 0
        self._event_index = 0
        self._history_index = 0

    def generate_npc(self, context: dict) -> AIResponse:
        npc_templates = [
            {
                "name": "Dra. Maela Ruun",
                "role": "investigadora disidente",
                "archetype": "scientist",
                "essence": "technocracy",
            },
            {
                "name": "Kárax el Sin Amo",
                "role": "propagador de ideas",
                "archetype": "propagator",
                "essence": "anarchism",
            },
            {
                "name": "Hermano Vacio",
                "role": "líder carismático",
                "archetype": "cult_leader",
                "essence": "thelema",
            },
        ]

        idx = self._npc_index
        if self.sequential:
            self._npc_index = (self._npc_index + 1) % len(npc_templates)
            if not self.loop and self._npc_index == 0:
                self._npc_index = len(npc_templates) - 1

        return AIResponse(success=True, data=npc_templates[idx])

    def generate_event(self, context: dict) -> AIResponse:
        event_templates = [
            {
                "event_title": "La Huelga del Silencio",
                "summary": "Los obreros dejaron de hablar durante siete días.",
                "choices": [
                    {"label": "Apoyar el silencio", "effect_tags": ["increase_absurdism"]},
                    {"label": "Convertirlo en ritual", "effect_tags": ["increase_thelema", "increase_cult_risk"]},
                ],
            },
            {
                "event_title": "El Laboratorio Abierto",
                "summary": "Se descubrieron nuevos protocolos de coordinación horizontal.",
                "choices": [
                    {"label": "Adoptar los protocolos", "effect_tags": ["increase_technocracy"]},
                    {"label": "Documentar sin implementar", "effect_tags": ["increase_memory"]},
                ],
            },
        ]

        idx = self._event_index
        if self.sequential:
            self._event_index = (self._event_index + 1) % len(event_templates)
            if not self.loop and self._event_index == 0:
                self._event_index = len(event_templates) - 1

        return AIResponse(success=True, data=event_templates[idx])

    def summarize_history(self, events: list[dict]) -> AIResponse:
        summaries = [
            "Año 47: La idea de la Voluntad Colectiva Calculada comenzó a gestarse.",
            "Año 52: Los Protocolos Autónomos se expandieron a tres distritos.",
            "Año 61: Una facción se radicalizó hacia el absurdo.",
        ]

        idx = self._history_index
        if self.sequential:
            self._history_index = (self._history_index + 1) % len(summaries)
            if not self.loop and self._history_index == 0:
                self._history_index = len(summaries) - 1

        return AIResponse(success=True, data={"summary": summaries[idx]})

    def interpret_consequences(self, situation: dict) -> AIResponse:
        return AIResponse(
            success=True,
            data={
                "interpretation": "La facción muestra signos de deriva ideológica.",
                "recommendations": ["Monitorear", "Intervenir", "Ignorar"],
            },
        )