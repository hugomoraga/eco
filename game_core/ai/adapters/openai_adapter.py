from __future__ import annotations

import os

from game_core.ai.base import AIAdapter, AIResponse

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAIAdapter(AIAdapter):
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
        model = self.config.get("model", "gpt-4")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 500)

        if OpenAI is None:
            raise ImportError("openai package not installed. Run: uv add openai")

        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            return ""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""

    def generate_npc(self, context: dict) -> AIResponse:
        from game_core.i18n import LANG_PROMPT

        system = f"Eres un generador de NPCs para un juego de simulacion memetica. {LANG_PROMPT}."
        user = f"Genera un NPC basado en este contexto: {context}"
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"raw": result})
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def generate_event(self, context: dict) -> AIResponse:
        from game_core.i18n import LANG_PROMPT

        system = f"Eres un generador de eventos narrativos. {LANG_PROMPT}."
        user = f"Genera un evento basado en este contexto: {context}"
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"raw": result})
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def summarize_history(self, events: list[dict]) -> AIResponse:
        from game_core.i18n import LANG_PROMPT

        system = f"Eres un cronista historico. {LANG_PROMPT}."
        user = f"Resume estos eventos: {events}"
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"summary": result})
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def interpret_consequences(self, situation: dict) -> AIResponse:
        from game_core.i18n import LANG_PROMPT

        system = f"Eres un interprete de consecuencias historicas. {LANG_PROMPT}."
        user = f"Interpreta esta situacion: {situation}"
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"interpretation": result})
        except Exception as e:
            return AIResponse(success=False, error=str(e))

    def generate_manifesto(self, essence: str, context: dict) -> AIResponse:
        from game_core.i18n import LANG_PROMPT

        system = f"Eres un generador de manifestos para un juego de simulacion memetica. {LANG_PROMPT}."
        user = f"""Escribe un manifesto corto (2-3 parrafos) {LANG_PROMPT} para un movimiento que sigue {essence}.

El manifiesto debe:
- Reflejar los principios centrales de {essence}
- Incluir referencias a etiquetas ideologicas que el eco lleva
- Ser evocador y persuasivo
- Terminar con un grito de guerra o eslogan

Contexto: World tick {context.get('world_tick', 0)}, influencia {context.get('influence', 0)}"""
        try:
            result = self._call_llm(system, user)
            return AIResponse(success=True, data={"content": result, "essence": essence})
        except Exception as e:
            return AIResponse(success=False, error=str(e))
