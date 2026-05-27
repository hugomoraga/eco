"""
adapter_core.autoplayer.engine - AutoplayerEngine for AI-controlled player decisions.

This module contains the AI logic for deciding player actions.
Moved here from core.autoplayer as part of hexagonal architecture refactor.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from adapters.autoplayer.types import (
    ADAPTIVE_RULES,
    PLAYER_STYLES,
    AutoplayDecision,
    AutoplayMode,
    Goal,
)
from core.application.processors.random import SeededRandom
from infra.logging import get_logger
from adapters.config.tuning import tuning

if TYPE_CHECKING:
    from core.domain import Echo, World

log = get_logger(__name__)


class AutoplayerEngine:
    EVALUATION_WEIGHTS: ClassVar[dict[str, float]] = {
        "doctrinal_clarity": 0.24,
        "memetic_spread": 0.19,
        "institutional_control": 0.13,
        "ideological_stability": 0.18,
        "survival_probability": 0.11,
        "material_security": 0.15,
        "adaptability": 0.07,
        "narrative_risk": 0.04,
        "historical_impact": 0.04,
    }

    def __init__(
        self,
        seed: int = 42,
        mode: AutoplayMode = AutoplayMode.AUTOPLAY,
        style_id: str = "preservationist",
        goals: list[Goal] | None = None,
    ):
        self.rng = SeededRandom.get_instance(seed)
        self.mode = mode
        self.style = PLAYER_STYLES.get(style_id, PLAYER_STYLES["preservationist"])
        self.goals = goals or self._default_goals()
        self.adaptive_rules = ADAPTIVE_RULES
        self.pending_suggestion: AutoplayDecision | None = None
        self.take_control_requested = False

    def _default_goals(self) -> list[Goal]:
        return [
            Goal(id="expand_influence", priority=70, strategy=["found_circle", "propagate_idea"]),
            Goal(id="preserve_doctrine", priority=60, strategy=["write_manifesto", "ritualize"]),
        ]

    def set_mode(self, mode: AutoplayMode) -> None:
        self.mode = mode

    def request_take_control(self) -> None:
        self.take_control_requested = True

    def evaluate_state(self, echo: Echo, world: World) -> dict[str, float]:
        metrics = {}

        echo_clarity = 50.0
        if echo.get_attribute("clarity"):
            echo_clarity = echo.get_attribute("clarity").value

        metrics["doctrinal_clarity"] = echo_clarity
        metrics["memetic_spread"] = min(len(echo.known_tags) * 15 + len(world.circles) * 10, 100)

        faction_influence = sum(f.influence for f in world.factions) / max(len(world.factions), 1)
        metrics["institutional_control"] = min(faction_influence, 100)

        lineage_stability = 100 - (len(echo.genealogical_lineage) * 5)
        metrics["ideological_stability"] = max(lineage_stability, 0)

        survival = 100 - echo.temporal_strain
        metrics["survival_probability"] = max(survival, 0)

        adaptability = echo.get_attribute("will").value if echo.get_attribute("will") else 50
        metrics["adaptability"] = adaptability

        metrics["narrative_risk"] = 100 - echo.shadow_coherence

        historical = (echo.reincarnation_count * 10) + (len(echo.genealogical_lineage) * 5)
        metrics["historical_impact"] = min(historical, 100)

        return metrics

    def calculate_evaluation_score(self, metrics: dict[str, float]) -> float:
        total = 0.0
        for key, weight in self.EVALUATION_WEIGHTS.items():
            value = metrics.get(key, 50)
            total += value * weight
        return total

    def score_action(
        self, action_name: str, echo: Echo, world: World, metrics: dict[str, float]
    ) -> float:
        base_score = 50.0

        style_id = self.style.id
        style_mods = tuning.style_modifiers.get(style_id, {})
        modifier = style_mods.get(action_name, 1.0)
        base_score = base_score * modifier

        for goal in self.goals:
            if action_name in goal.strategy:
                base_score += goal.priority * 0.2

        base_score += metrics.get("memetic_spread", 0) * 0.1 if action_name in ["found_circle", "propagate_idea"] else 0
        base_score += metrics.get("doctrinal_clarity", 0) * 0.1 if action_name in ["write_manifesto", "ritualize"] else 0

        penalty = tuning.diminishing_penalty
        min_mult = tuning.diminishing_min
        repeats = echo.action_history.count(action_name)
        diminishing_factor = max(min_mult, 1.0 - (repeats * penalty))

        last_turn = echo.last_action_turn.get(action_name, 0)
        if last_turn == 0:
            freshness_bonus = tuning.max_freshness_bonus
        else:
            turns_since = world.clock.action_tick - last_turn
            freshness_bonus = min(tuning.max_freshness_bonus, turns_since * tuning.freshness_bonus_per_turn)

        final_score = base_score * diminishing_factor * (1 + freshness_bonus)
        return max(0, min(100, final_score))

    def select_action(
        self, echo: Echo, world: World, available_actions: list[str]
    ) -> AutoplayDecision:
        if self.take_control_requested:
            self.take_control_requested = False
            log.info("autoplay_decision", turn=world.clock.action_tick, selected_action="", reason="take_control_requested")
            return AutoplayDecision(
                turn=world.clock.action_tick,
                selected_action="",
                score=0,
                reason="Take control requested - no action selected",
            )

        metrics = self.evaluate_state(echo, world)

        action_scores = {}
        for action in available_actions:
            action_scores[action] = self.score_action(action, echo, world, metrics)

        best_action = max(action_scores, key=lambda a: (action_scores[a], self.rng.random()))
        best_score = action_scores[best_action]

        alternatives = [
            {"action": a, "score": s} for a, s in sorted(action_scores.items(), key=lambda x: x[1], reverse=True) if a != best_action
        ]

        log.info("autoplay_decision", turn=world.clock.action_tick, echo_name=echo.name,
                 selected_action=best_action, score=best_score, style=self.style.name,
                 metrics=metrics, action_scores=action_scores)

        return AutoplayDecision(
            turn=world.clock.action_tick,
            selected_action=best_action,
            score=best_score,
            reason=f"Selected based on {self.style.name} style and current metrics",
            alternatives=alternatives[:3],
        )

    def suggest_action(self, echo: Echo, world: World, available_actions: list[str]) -> AutoplayDecision:
        decision = self.select_action(echo, world, available_actions)
        self.pending_suggestion = decision
        return decision

    def confirm_suggestion(self) -> AutoplayDecision | None:
        if self.pending_suggestion:
            decision = self.pending_suggestion
            self.pending_suggestion = None
            return decision
        return None

    def reject_suggestion(self) -> None:
        self.pending_suggestion = None

    def should_act(self, echo: Echo, world: World) -> bool:
        if self.mode == AutoplayMode.MANUAL:
            return False
        if self.mode == AutoplayMode.SUGGEST:
            return self.pending_suggestion is not None
        return True
