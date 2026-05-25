"""
MiniMax Adapter - Anthropic-compatible API
"""
from __future__ import annotations

import os

from game_core.ai.base import AIAdapter, AIResponse


class MiniMaxAdapter(AIAdapter):
    """Adapter for MiniMax Anthropic-compatible API."""

    BASE_URL = "https://api.minimax.io/anthropic/v1"

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key") or os.environ.get("MINIMAX_API_KEY")
        self.model = self.config.get("model", "MiniMax-M2.7")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 1024)

        if not self.api_key:
            raise ValueError("MiniMax API key not found. Set MINIMAX_API_KEY env var.")

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make request to MiniMax API."""
        import json
        import urllib.request

        url = f"{self.BASE_URL}/messages"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": str(self.api_key),
            },
            method="POST",
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))

        # Parse response - extract text from content blocks
        content_text = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                content_text += block.get("text", "")

        return content_text or ""

    def generate_npc(self, context: dict) -> AIResponse:
        system = "Eres un generador de NPCs para un juego de simulación memética."
        user = f"""Genera un NPC en JSON. Responde SOLO con JSON válido.

Formato exacto:
{{"name": "nombre completo", "title": "título/rol", "backstory": "historia 1-2 oraciones", "motivation": "qué lo motiva", "personality": "rasgo de personalidad"}}

Contexto: {context}

Responde solo con JSON."""
        try:
            result = self._call_llm(system, user)
            import json
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(result)
            return AIResponse(success=True, data=data)
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def generate_event(self, context: dict) -> AIResponse:
        system = "Eres un generador de eventos narrativos para un juego de simulación."
        user = f"""Genera un evento narrativo en JSON. Responde SOLO con JSON válido, sin texto extra.

Formato exacto:
{{"event_title": "título en español (máx 10 palabras)", "summary": "resumen 1-2 oraciones", "causes": ["causa1", "causa2"], "choices": [{{"label": "opción", "effect_tags": ["tag1"]}}]}}

Contexto: {context}

Tags válidos: anarchism, socialism, communism, fascism, progressivism, traditionalism, environmentalism, technocracy, individualism, collectivism, mysticism, rationalism, absurdism, minimalism, post_left, accelerationism, solarpunk, dark_romanticism, primitivism, transhumanism, syncretism, reformism, extremism, moderation, dogmatism, syncretism, reformism, extremism, moderation, dogmatism

Responde solo con JSON."""
        try:
            result = self._call_llm(system, user)
            import json
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(result)
            return AIResponse(success=True, data=data)
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def summarize_history(self, events: list[dict]) -> AIResponse:
        system = "Eres un cronista histórico."
        user = f"Resume estos eventos: {events}"
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"summary": result})
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def interpret_consequences(self, situation: dict) -> AIResponse:
        system = "Eres un intérprete de consecuencias históricas."
        user = f"Interpreta esta situación: {situation}"
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"interpretation": result})
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def generate_manifesto(self, essence: str, context: dict) -> AIResponse:
        system = "Eres un generador de manifestos para un juego de simulación memética."
        user = f"""Escribe un manifesto corto (2-3 párrafos) en español para un movimiento que sigue {essence}.

El manifiesto debe:
- Reflejar los principios centrales de {essence}
- Incluir referencias a etiquetas ideológicas que el eco lleva
- Ser evocador y persuasivo
- Terminar con un grito de guerra o eslogan

Contexto: World tick {context.get('world_tick', 0)}, influencia {context.get('influence', 0)}"""
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"content": result, "essence": essence})
        except Exception as e:
            return AIResponse(success=False, error=str(e))
