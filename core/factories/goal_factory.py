from __future__ import annotations

import random
import uuid
from typing import TYPE_CHECKING

from core.domain.registries.archetype_registry import get_archetype
from core.domain.rules.goals import (
    AccumulateGoal,
    Goal,
    MaintainGoal,
    ProgressGoal,
    SurviveGoal,
)

if TYPE_CHECKING:
    from core.domain.entities import Person


GOAL_TEMPLATES: dict[str, list[dict]] = {
    "circles": [
        "Fundar {n} círculos autónomos",
        "Crear una red de {n} círculos secretos",
        "Organizar {n} células de base",
    ],
    "legitimacy": [
        "Alcanzar {n} de legitimidad",
        "Ganar la confianza del pueblo ({n})",
        "Llegar a {n} de apoyo popular",
    ],
    "resources": [
        "Acumular {n} recursos",
        "Reunir {n} en provisiones",
        "Asegurar {n} recursos para la causa",
    ],
    "pressure": [
        "Mantener la presión sobre el régimen ({n})",
        "Sostener presión en {n}",
        "Mantener {n} de tensión social",
    ],
    "events": [
        "Crear {n} eventos culturales",
        "Organizar {n} manifestaciones",
        "Realizar {n} acciones públicas",
    ],
}


PLAYER_GOAL_POOL: list[dict] = [
    {
        "metric": "circles",
        "target": 5,
        "description": "Fundar 5 círculos autónomos",
        "difficulty": 4,
    },
    {
        "metric": "circles",
        "target": 3,
        "description": "Fundar 3 círculos y sobrevivir 20 turnos",
        "difficulty": 3,
    },
    {
        "metric": "legitimacy",
        "target": 100,
        "description": "Alcanzar 100 de legitimidad",
        "difficulty": 5,
    },
    {
        "metric": "legitimacy",
        "target": 80,
        "description": "Llegar a 80 de legitimidad manteniendo presión bajo 50",
        "difficulty": 4,
    },
    {
        "metric": "resources",
        "target": 100,
        "description": "Acumular 100 recursos",
        "difficulty": 3,
    },
    {
        "metric": "resources",
        "target": 80,
        "description": "Acumular 80 recursos y sobrevivir 20 turnos",
        "difficulty": 3,
    },
    {
        "metric": "events",
        "target": 5,
        "description": "Crear 5 manifestos",
        "difficulty": 3,
    },
    {
        "metric": "influence",
        "target": 50,
        "description": "Alcanzar 50 de influencia total",
        "difficulty": 4,
    },
]


class GoalFactory:
    @staticmethod
    def create_player_goals(n_options: int = 3, turn_limit: int = 20) -> list[Goal]:
        selected = random.sample(PLAYER_GOAL_POOL, min(n_options, len(PLAYER_GOAL_POOL)))
        goals = []
        for i, template in enumerate(selected):
            goal = ProgressGoal(
                goal_id=f"player_goal_{i}",
                owner_id="player",
                owner_name="Tú",
                turn_limit=turn_limit,
                metric=template["metric"],
                target=float(template["target"]),
                description=template["description"],
            )
            goals.append(goal)
        return goals

    @staticmethod
    def create_npc_goal(npc: Person, turn_limit: int, seed: int | None = None) -> Goal:
        rng = random.Random(seed)

        archetype_id = npc.archetype or "neutral"
        archetype_data = get_archetype(archetype_id)
        gw = archetype_data.goal_weights

        goal_types_and_weights = [
            (ProgressGoal, gw.progress),
            (MaintainGoal, gw.maintain),
            (AccumulateGoal, gw.accumulate),
            (SurviveGoal, gw.survive),
        ]
        goal_types = [g[0] for g in goal_types_and_weights]
        type_weights = [g[1] for g in goal_types_and_weights]

        valid_pairs = [(gt, w) for gt, w in zip(goal_types, type_weights, strict=False) if w > 0]
        if not valid_pairs:
            return GoalFactory._create_survive_goal(npc, turn_limit, rng)

        valid_types = [g[0] for g in valid_pairs]
        valid_weights = [g[1] for g in valid_pairs]
        chosen_type = rng.choices(valid_types, weights=valid_weights, k=1)[0]

        if chosen_type == ProgressGoal:
            return GoalFactory._create_progress_goal(npc, turn_limit, rng)
        elif chosen_type == MaintainGoal:
            return GoalFactory._create_maintain_goal(npc, turn_limit, rng)
        elif chosen_type == AccumulateGoal:
            return GoalFactory._create_accumulate_goal(npc, turn_limit, rng)
        else:
            return GoalFactory._create_survive_goal(npc, turn_limit, rng)

    @staticmethod
    def _create_progress_goal(npc: Person, turn_limit: int, rng: random.Random) -> ProgressGoal:
        metric = rng.choice(["circles", "legitimacy", "resources", "events"])
        templates = GOAL_TEMPLATES.get(metric, GOAL_TEMPLATES["circles"])
        template = rng.choice(templates)

        targets = {
            "circles": rng.randint(2, 4),
            "legitimacy": rng.randint(60, 90),
            "resources": rng.randint(50, 80),
            "events": rng.randint(3, 6),
        }
        target = targets[metric]

        return ProgressGoal(
            goal_id=str(uuid.uuid4()),
            owner_id=npc.id,
            owner_name=npc.name or f"NPC-{npc.id[:8]}",
            turn_limit=turn_limit,
            metric=metric,
            target=float(target),
            description=template.format(n=target),
        )

    @staticmethod
    def _create_maintain_goal(npc: Person, turn_limit: int, rng: random.Random) -> MaintainGoal:
        metric = rng.choice(["legitimacy", "pressure", "clarity"])
        operator = rng.choice(["gt", "lt"])

        thresholds = {
            "legitimacy": (50, 80),
            "pressure": (50, 90),
            "clarity": (40, 70),
        }
        low, high = thresholds[metric]
        threshold = float(rng.randint(low, high))

        op_str = ">" if operator == "gt" else "<"
        description = f"Mantener {metric} {op_str} {int(threshold)}"

        return MaintainGoal(
            goal_id=str(uuid.uuid4()),
            owner_id=npc.id,
            owner_name=npc.name or f"NPC-{npc.id[:8]}",
            turn_limit=turn_limit,
            metric=metric,
            operator=operator,
            threshold=threshold,
            description=description,
        )

    @staticmethod
    def _create_accumulate_goal(npc: Person, turn_limit: int, rng: random.Random) -> AccumulateGoal:
        metric = rng.choice(["resources", "legitimacy", "influence"])
        templates = {
            "resources": ["Acumular {n} recursos", "Juntar {n} en provisiones"],
            "legitimacy": ["Ganar {n} puntos de legitimidad", "Alcanzar {n} de apoyo"],
            "influence": ["Lograr {n} de influencia total", "Acumular {n} de influencia"],
        }

        targets = {
            "resources": rng.randint(40, 80),
            "legitimacy": rng.randint(50, 80),
            "influence": rng.randint(30, 60),
        }

        target = targets[metric]
        template = rng.choice(templates[metric])

        return AccumulateGoal(
            goal_id=str(uuid.uuid4()),
            owner_id=npc.id,
            owner_name=npc.name or f"NPC-{npc.id[:8]}",
            turn_limit=turn_limit,
            metric=metric,
            target=float(target),
            description=template.format(n=target),
        )

    @staticmethod
    def _create_survive_goal(npc: Person, turn_limit: int, rng: random.Random) -> SurviveGoal:
        turns_needed = rng.randint(int(turn_limit * 0.6), turn_limit)
        return SurviveGoal(
            goal_id=str(uuid.uuid4()),
            owner_id=npc.id,
            owner_name=npc.name or f"NPC-{npc.id[:8]}",
            turn_limit=turn_limit,
            turns_needed=turns_needed,
        )
