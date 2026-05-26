"""Narrative Engine - Hybrid narrative generation (50% pre-generated, 50% AI)."""

from __future__ import annotations

import random
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from core.domain.entities import Echo, Person
    from core.ai.base import AIAdapter

from adapters.i18n import get_lang


def _load_templates(language: str = "es") -> dict:
    """Load all pre-generated narrative templates for the given language."""
    templates = {}
    narratives_dir = Path(__file__).parent.parent.parent / "data" / "narratives"

    if not narratives_dir.exists():
        return templates

    for action_dir in narratives_dir.iterdir():
        if not action_dir.is_dir():
            continue
        action_templates = {}
        archetype_dir = action_dir / language
        if archetype_dir.is_dir():
            template_file = archetype_dir / "templates.yaml"
            if template_file.exists():
                with open(template_file) as f:
                    data = yaml.safe_load(f) or {}
                    action_templates[language] = data.get("templates", [])
        if action_templates:
            templates[action_dir.name] = action_templates

    return templates


class NarrativeEngine:
    def __init__(self, ai_adapter=None, language: str | None = None):
        self.ai_adapter = ai_adapter
        self.language = language or get_lang()
        self.templates = _load_templates(self.language)
        self._fallback_templates = self._default_fallback_templates()

    def _default_fallback_templates(self) -> dict:
        """Fallback templates when no pre-generated templates exist."""
        return {
            "found_circle": {
                "es": [
                    "{actor} reunió seguidores y fundó un nuevo círculo",
                    "{actor} estableció una reunión en torno a creencias compartidas",
                ],
                "en": [
                    "{actor} gathered followers and founded a new circle",
                    "{actor} established a gathering around shared beliefs",
                ]
            },
            "join_circle": {
                "es": [
                    "{actor} se unió a un círculo existente",
                    "{actor} pasó a formar parte de una reunión",
                ],
                "en": [
                    "{actor} joined an existing circle",
                    "{actor} became part of a circle",
                ]
            },
            "propagate_idea": {
                "es": [
                    "{actor} propagó ideas a quienes querían escuchar",
                    "{actor} susurró conceptos que desafiaban la norma",
                ],
                "en": [
                    "{actor} spread ideas to those willing to listen",
                    "{actor} whispered concepts that challenged the norm",
                ]
            },
            "spread_rumor": {
                "es": [
                    "{actor} esparció rumores por las calles",
                    "{actor} susurró medias verdades que ganaban tracción",
                ],
                "en": [
                    "{actor} spread rumors through the streets",
                    "{actor} whispered half-truths that gained traction",
                ]
            },
            "recruit_follower": {
                "es": [
                    "{actor} reclutó un nuevo seguidor para la causa",
                    "{actor} convenció a alguien de unirse",
                ],
                "en": [
                    "{actor} recruited a new follower to the cause",
                    "{actor} convinced someone to join",
                ]
            },
            "negotiate": {
                "es": [
                    "{actor} negoció un acuerdo",
                    "{actor} rompió un acuerdo entre las partes",
                ],
                "en": [
                    "{actor} negotiated a deal",
                    "{actor} brokered an agreement",
                ]
            },
            "ritual": {
                "es": [
                    "{actor} realizó un poderoso ritual",
                    "{actor} canalizó energía a través de formas antiguas",
                ],
                "en": [
                    "{actor} performed a powerful ritual",
                    "{actor} channeled energy through ancient forms",
                ]
            },
            "ritualize": {
                "es": [
                    "{actor} completó un ritual",
                    "{actor} realizó acciones ceremoniales",
                ],
                "en": [
                    "{actor} completed a ritual",
                    "{actor} performed ceremonial actions",
                ]
            },
            "sabotage": {
                "es": [
                    "{actor} saboteó infraestructura",
                    "{actor} disruptó operaciones",
                ],
                "en": [
                    "{actor} sabotaged infrastructure",
                    "{actor} disrupted operations",
                ]
            },
            "talk": {
                "es": [
                    "{actor} habló con quienes estaban cerca",
                    "{actor} entabló conversación",
                ],
                "en": [
                    "{actor} spoke with those nearby",
                    "{actor} engaged in conversation",
                ]
            },
            "write_manifesto": {
                "es": [
                    "{actor} escribió sus creencias",
                    "{actor} documentó su filosofía",
                ],
                "en": [
                    "{actor} wrote down their beliefs",
                    "{actor} documented their philosophy",
                ]
            },
            "leave_circle": {
                "es": [
                    "{actor} dejó su círculo",
                    "{actor} se alejó del grupo",
                ],
                "en": [
                    "{actor} left their circle",
                    "{actor} walked away from the group",
                ]
            },
        }

    def generate_narrative(
        self,
        action: str,
        actor_name: str,
        target_name: str | None = None,
        context: dict | None = None,
    ) -> str:
        """Generate a narrative for an action, 50% pre-generated, 50% AI."""
        context = context or {}

        if random.random() < 0.5:
            return self._get_pre_generated_narrative(action, actor_name, context)
        else:
            return self._get_ai_narrative(action, actor_name, target_name, context)

    def _get_pre_generated_narrative(
        self,
        action: str,
        actor_name: str,
        context: dict,
    ) -> str:
        """Get a pre-generated narrative."""
        if action in self.templates and self.language in self.templates[action]:
            templates = self.templates[action][self.language]
        elif action in self._fallback_templates and self.language in self._fallback_templates[action]:
            templates = self._fallback_templates[action][self.language]
        else:
            templates = self._fallback_templates.get(action, {}).get("en", [])

        if templates:
            template = random.choice(templates)
            return template.format(actor=actor_name, **context)

        return f"{actor_name} performed {action}"

    def _get_ai_narrative(
        self,
        action: str,
        actor_name: str,
        target_name: str | None,
        context: dict,
    ) -> str:
        """Get AI-generated narrative."""
        if self.ai_adapter is None:
            return self._get_pre_generated_narrative(action, actor_name, context)

        try:
            prompt = self._build_ai_prompt(action, actor_name, target_name, context)
            response = self.ai_adapter.generate_narrative(prompt)
            if response and response.success:
                return response.data.get("narrative", self._get_pre_generated_narrative(action, actor_name, context))
        except Exception:
            pass

        return self._get_pre_generated_narrative(action, actor_name, context)

    def _build_ai_prompt(
        self,
        action: str,
        actor_name: str,
        target_name: str | None,
        context: dict,
    ) -> str:
        """Build AI prompt for narrative generation."""
        target_part = f" target: {target_name}" if target_name else ""
        context_part = f" context: {context}" if context else ""
        return (
            f"Generate a short narrative (1-2 sentences) for this action: {action}\n"
            f"Actor: {actor_name}\n"
            f"{target_part}\n"
            f"{context_part}\n"
            f"Style: Third person, evocative but brief, game narrative"
        )

    def generate_npc_action_narrative(
        self,
        npc_name: str,
        action: str,
        archetype: str | None = None,
    ) -> str:
        """Generate narrative for NPC action."""
        archetype = archetype or "default"
        return self._get_pre_generated_narrative(action, npc_name, {"archetype": archetype})

    def generate_player_action_narrative(
        self,
        action: str,
        result_success: bool,
        effects: dict | None = None,
    ) -> str:
        """Generate narrative for player action result."""
        effects = effects or {}
        success_templates = {
            "es": {
                "found_circle": "Un nuevo círculo emerge de la influencia del eco",
                "join_circle": "El eco se une a un círculo existente",
                "propagate_idea": "Las ideas se propagan por la civ",
                "write_manifesto": "Se escribe un manifiesto documentando las creencias del eco",
                "ritualize": "El ritual resuena a través de los círculos del eco",
                "sabotage": "La infraestructura se desmorona bajo la influencia del eco",
                "spread_rumor": "Los rumores se extienden, desestabilizando la civ",
                "recruit_follower": "Un nuevo seguidor se une al círculo del eco",
                "negotiate": "Los recursos fluyen de negociaciones exitosas",
                "ritual": "Un poderoso ritual amplifica la presencia del eco",
                "talk": "Las palabras tienen peso en el discurso del eco",
                "leave_circle": "El eco abandona su círculo",
            },
            "en": {
                "found_circle": "A new circle emerges from the echo's influence",
                "join_circle": "The echo joins an existing circle",
                "propagate_idea": "Ideas spread through the civ",
                "write_manifesto": "A manifesto is written, documenting the echo's beliefs",
                "ritualize": "The ritual resonates through the echo's circles",
                "sabotage": "Infrastructure crumbles under the echo's influence",
                "spread_rumor": "Rumors spread, destabilizing the civ",
                "recruit_follower": "A new follower joins the echo's circle",
                "negotiate": "Resources flow from successful negotiations",
                "ritual": "A powerful ritual amplifies the echo's presence",
                "talk": "Words carry weight in the echo's discourse",
                "leave_circle": "The echo leaves their circle",
            },
        }
        if result_success:
            templates = success_templates.get(self.language, success_templates["en"])
            return templates.get(action, f"The echo performed {action}")
        else:
            failed_templates = {
                "es": f"La acción de {action} no tuvo efecto",
                "en": f"The echo's {action} had no effect",
            }
            return failed_templates.get(self.language, failed_templates["en"])