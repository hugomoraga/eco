from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain import Echo, World
    from core.domain.rules.goals import Goal


NARRATIVE_INTROS: dict[str, list[str]] = {
    "artisan": [
        "Eres la voz de los artesanos, los makers, los que construyen con sus manos.",
        "Tu esencia es el trabajo. La creación es tu protesta.",
        "Los herreros, los tejedores, los constructores... todos tejen el futuro.",
    ],
    "merchant": [
        "De las transacciones surge el poder. Tu riqueza es tu arma.",
        "El comercio mueve ciudades. Y tú mueves el comercio.",
        "Tu moneda habla más fuerte que las balas.",
    ],
    "warrior": [
        "La fuerza bruta abre caminos que la palabra no puede.",
        "Tu puño es tu argumento. La acción tu discurso.",
        "Los músculos mueven montañas. Y tú eres la montaña.",
    ],
    "leader": [
        "Los demás te siguen. Tu palabra mueve multitudes.",
        "Naciste para liderar. El pueblo reconoce a su guía.",
        "Tu voz corta el silencio como espada.",
    ],
    "scholar": [
        "El conocimiento es poder. Y tú posees verdades peligrosas.",
        "Los libros encierran secretos. Tú los has leído todos.",
        "La ignorancia es la prisión. Tú tienes la llave.",
    ],
    "artist": [
        "El arte desafía. Tu creación agita almas dormidas.",
        "Con un pincel cambias lo que espadas no pueden.",
        "Tu arte es tu revolución.",
    ],
    "mystic": [
        "Ves lo que otros no pueden. Tus visiones son profecías.",
        "El velo se ha rasgado. Tú ves más allá.",
        "Tus sueños son mapas del futuro.",
    ],
    "wanderer": [
        "Llegas de donde nadie te espera. Tu libertad es tu mensaje.",
        "Sin hogar, sin cadenas. Tu camino es tu mensaje.",
        "Cruzas fronteras sin pedir permiso.",
    ],
    "neutral": [
        "El cambio viene. Solo falta dirección.",
        "Una nueva era se asoma en el horizonte.",
        "El futuro está por escribirse.",
    ],
}


LEGITIMACY_INTROS = {
    "low": "El pueblo aún no confía en ti. Las viejas estructuras se mantienen erguidas.",
    "medium": "Hay ojos que te observan con esperanza. Algunos susurran tu nombre en las sombras.",
    "high": "Las calles murmuran tu llegada. El cambio parece inevitable.",
}


PRESSURE_INTROS = {
    "low": "La calma precede a la tormenta. Los poderosos duermen tranquilos... por ahora.",
    "medium": "La tensión se siente en el aire. Las reuniones secretas se multiplican.",
    "high": "La revolución late en cada esquina. El pueblo está listo para actuar.",
}


@dataclass
class NarrativeIntro:
    echo_archetype: str
    echo_essence: str
    echo_clarity: float
    legitimacy: float
    pressure: float
    intro_text: str
    legitimacy_text: str
    pressure_text: str


@dataclass
class StoryBeat:
    turn: int
    act: str
    act_number: int
    title: str
    narrative: str
    state_summary: dict


@dataclass
class NarrativeFinale:
    turn: int
    outcome: str
    outcome_text: str
    story_summary: str
    final_stats: dict
    player_goal_progress: float
    winner: str
    winner_name: str


class NarrativeGenerator:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def generate_intro(self, echo: Echo | None, world: World) -> NarrativeIntro:
        archetype = getattr(echo, 'archetype', 'neutral') if echo else "neutral"
        essence = echo.dominant_essence if echo else world.circles[0].essence if world.circles else "anarchism"
        clarity = echo.clarity if echo else 50.0

        from core.domain.registries.archetype_registry import get_archetype
        archetype_data = get_archetype(archetype)
        intro_text = self.rng.choice(archetype_data.intro_texts)

        legitimacy = world.legitimacy
        if legitimacy < 40:
            legit_text = LEGITIMACY_INTROS["low"]
        elif legitimacy < 70:
            legit_text = LEGITIMACY_INTROS["medium"]
        else:
            legit_text = LEGITIMACY_INTROS["high"]

        pressure = world.pressure
        if pressure < 30:
            pressure_text = PRESSURE_INTROS["low"]
        elif pressure < 60:
            pressure_text = PRESSURE_INTROS["medium"]
        else:
            pressure_text = PRESSURE_INTROS["high"]

        return NarrativeIntro(
            echo_archetype=archetype,
            echo_essence=essence,
            echo_clarity=clarity,
            legitimacy=legitimacy,
            pressure=pressure,
            intro_text=intro_text,
            legitimacy_text=legit_text,
            pressure_text=pressure_text,
        )

    def generate_story_beat(self, turn: int, world: World, npc_actions: list[dict]) -> StoryBeat:
        act, act_num, title = self._get_act_info(turn)

        narrative = self._generate_beat_narrative(turn, world, npc_actions)

        state_summary = {
            "circles": len([c for c in world.circles if c.status.value == "active"]),
            "legitimacy": int(world.legitimacy),
            "pressure": int(world.pressure),
            "resources": int(world.resources_global),
        }

        return StoryBeat(
            turn=turn,
            act=act,
            act_number=act_num,
            title=title,
            narrative=narrative,
            state_summary=state_summary,
        )

    def _get_act_info(self, turn: int) -> tuple[str, int, str]:
        if turn <= 5:
            return "Acto I: El Despertar", 1, "LA SEMILLA SE PLARTA"
        elif turn <= 14:
            return "Acto II: La Efervescencia", 2, "EL FUEGO SE EXTIENDE"
        else:
            return "Acto III: El Cruce", 3, "EL DESTINO SE DECIDE"

    def _generate_beat_narrative(self, turn: int, world: World, npc_actions: list[dict]) -> str:
        circles = len([c for c in world.circles if c.status.value == "active"])
        pressure = world.pressure

        if circles == 0:
            base = "Los primeros círculos comienzan a formarse en las sombras."
        elif circles < 3:
            base = "Los círculos crecen en número y fuerza."
        elif circles < 6:
            base = "La red de círculos se expande por toda la ciudad."
        else:
            base = "Los círculos dominan la ciudad. El viejo orden tiembla."

        if pressure > 80:
            base += " La tensión es insostenible."
        elif pressure > 50:
            base += " El régimen responde con cautela."

        return base

    def generate_finale(
        self,
        turn: int,
        world: World,
        player_goal: Goal | None,
        all_goals: list[Goal],
        winner: str,
        winner_name: str,
    ) -> NarrativeFinale:
        player_progress = player_goal.evaluate(world, turn) if player_goal else 0.0

        circles_created = len(world.circles)
        active_circles = len([c for c in world.circles if c.status.value == "active"])

        if winner == "player":
            outcome = "victory"
            outcome_text = self._get_victory_text(player_progress)
        elif winner == "close":
            outcome = "close_defeat"
            outcome_text = self._get_close_defeat_text(player_progress)
        else:
            outcome = "defeat"
            outcome_text = self._get_defeat_text()

        story_summary = f"""Turno {turn}. El sol se pone sobre la ciudad que cambió.

Tu Eco resonó durante {turn} turnos.
Los círculos que fundaste: {circles_created}. Permanecen en pie: {active_circles}.
Las ideas que sembraste no murieron con tu partida."""

        final_stats = {
            "turn": turn,
            "legitimacy": int(world.legitimacy),
            "circles": active_circles,
            "circles_created": circles_created,
            "pressure": int(world.pressure),
            "resources": int(world.resources_global),
        }

        return NarrativeFinale(
            turn=turn,
            outcome=outcome,
            outcome_text=outcome_text,
            story_summary=story_summary,
            final_stats=final_stats,
            player_goal_progress=player_progress,
            winner=winner,
            winner_name=winner_name,
        )

    def _get_victory_text(self, progress: float) -> str:
        if progress >= 1.0:
            return """La revolución ha triunfado. Tu visión se ha hecho realidad.
El pueblo recuerda a quien les liberó del miedo."""
        else:
            pct = int(progress * 100)
            return f"""La revolución no terminó, pero el cambio llegó. Llegaste al {pct}% de tu meta.
Tu nombre será recordado en los anales de los libres."""

    def _get_close_defeat_text(self, progress: float) -> str:
        pct = int(progress * 100)
        return f"""Por poco. El cambio estaba tan cerca que podías tocarlo ({pct}% de tu meta).
Pero las estructuras resistieron. Habrá otra oportunidad."""

    def _get_defeat_text(self) -> str:
        return """El viejo orden prevalece. Tu eco se desvanece sin eco.
Pero las semillas de la duda ya fueron plantadas..."""


def format_intro_screen(intro: NarrativeIntro) -> str:
    lines = [
        "═" * 60,
        "★ ECO DE LA REVOLUCIÓN ★",
        "═" * 60,
        "",
        f"  {intro.intro_text}",
        "",
        f"  El Echo de {intro.echo_archetype} se manifiesta con claridad {int(intro.echo_clarity)}%.",
        f"  Su esencia irradia: {intro.echo_essence}.",
        "",
        f"  {intro.legitimacy_text}",
        "",
        f"  {intro.pressure_text}",
        "",
        "─" * 60,
        "  Presiona ENTER para elegir tu destino...",
    ]
    return "\n".join(lines)


def format_story_beat(beat: StoryBeat) -> str:
    lines = [
        "═" * 60,
        f"★ {beat.act} ★",
        "═" * 60,
        "",
        f"  {beat.narrative}",
        "",
        f"  ★ Progreso: {beat.state_summary['circles']} círculos activos",
        f"  ★ Legitimacy: {beat.state_summary['legitimacy']}/100",
        f"  ★ Presión: {beat.state_summary['pressure']}/100",
        "─" * 60,
    ]
    return "\n".join(lines)


def format_finale(finale: NarrativeFinale, player_goal: Goal | None, top_rival_goals: list[Goal]) -> str:
    goal_desc = player_goal.description if player_goal else "N/A"
    goal_bar = player_goal.progress_bar(None, finale.turn) if player_goal else "░░░░░"
    pct = int(finale.player_goal_progress * 100)

    lines = [
        "═" * 60,
        "★ EPÍLOGO ★",
        "═" * 60,
        "",
        f"  {finale.outcome_text}",
        "",
        finale.story_summary,
        "",
        "─" * 60,
        "  ★ Estadísticas Finales:",
        "  ────────────────────────────────────────────────────",
        f"  Legitimacy final: {finale.final_stats['legitimacy']}/100",
        f"  Círculos restantes: {finale.final_stats['circles']}",
        f"  Círculos creados: {finale.final_stats['circles_created']}",
        f"  Presión final: {finale.final_stats['pressure']}/100",
        "",
        f"  ★ Tu Goal: {goal_desc} [{goal_bar}] {pct}%",
    ]

    if top_rival_goals:
        lines.append("  ★ Goals Rivales:")
        for g in top_rival_goals[:3]:
            bar = g.progress_bar(None, finale.turn)
            prog = int(g.evaluate(None, finale.turn) * 100)
            lines.append(f"    • {g.owner_name}: {g.short_description} [{bar}] {prog}%")

    lines.append("─" * 60)

    if finale.winner == "player":
        lines.append(f"  🏆 RESULTADO: ¡VICTORIA! ({pct}%)")
    else:
        lines.append(f"  ⚔ RESULTADO: Derrota ({pct}% vs {int(top_rival_goals[0].evaluate(None, finale.turn) * 100) if top_rival_goals else 0}%)")

    lines.append("═" * 60)
    return "\n".join(lines)
