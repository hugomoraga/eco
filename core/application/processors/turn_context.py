"""
turn_context.py — Turn processing helpers: damage, reincarnation, metrics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.domain.entities.person import PlayerPerson
from core.domain.entities.world import World
from core.application.processors.damage import calculate_damage, should_deal_damage_to_player
from core.application.processors.reincarnation import (
    end_transition_turn,
    is_in_transition,
    preserve_echo_legacy,
    reincarnate_echo,
    start_transition_turn,
    transform_legacy,
)

if TYPE_CHECKING:
    from core.ports.logger import Logger


class _NoOpLogger:
    """No-op logger for when logging is not configured."""

    def debug(self, msg: str, **kwargs: Any) -> None: pass
    def info(self, msg: str, **kwargs: Any) -> None: pass
    def warning(self, msg: str, **kwargs: Any) -> None: pass
    def error(self, msg: str, **kwargs: Any) -> None: pass
    def exception(self, msg: str, **kwargs: Any) -> None: pass


def snapshot_metrics(world: World) -> dict:
    """Capture current world metrics."""
    return {
        "pressure": world.pressure,
        "legitimacy": world.legitimacy,
        "resources_global": world.resources_global,
    }


def handle_npc_damage_to_player(
    action_name: str,
    world: World,
    notify,
    turn: int,
    log: Logger | None = None,
) -> None:
    """Handle NPC actions that can damage the player (sabotage, spread_rumor)."""
    if log is None:
        log = _NoOpLogger()
    person = world.get_active_player_person()
    if not person:
        log.warning("npc_damage", turn=turn, action=action_name, stage="no_active_player")
        return

    defender_influence = person.influence
    defender_circle_count = len(getattr(person, 'circles', []))

    damage, is_critical = calculate_damage(
        action_name,
        attacker_influence=30.0,
        defender_influence=defender_influence,
        defender_circle_count=defender_circle_count,
    )

    if damage > 0:
        old_vitality = person.vitality
        person.take_damage(damage)
        new_vitality = person.vitality
        log.info("npc_damage", turn=turn, action=action_name, damage=damage, old_vitality=old_vitality, new_vitality=new_vitality)
        notify("on_metric_changed", turn, "player_vitality", old_vitality, new_vitality)

        if person.vitality <= 0:
            log.error("player_death", turn=turn, player=person.name, vitality=0, trigger="npc_damage")
            trigger_player_death(world, person, notify, turn, log)


def trigger_player_death(
    world: World,
    player_person: PlayerPerson,
    notify,
    turn: int,
    log: Logger | None = None,
) -> None:
    """Trigger player death and start reincarnation process."""
    if log is None:
        log = _NoOpLogger()
    log.debug("reincarnation", stage="preserving_legacy", player_person_id=player_person.id, echo_id=player_person.echo_id)

    echo = world.get_echo(player_person.echo_id) if player_person.echo_id else None
    if not echo:
        log.error("reincarnation", stage="trigger_death", error="no_echo_found", player_person_echo_id=player_person.echo_id)
        return

    legacy = preserve_echo_legacy(echo)
    transformed = transform_legacy(legacy, echo)

    log.debug("reincarnation", stage="finding_candidate", echo_id=echo.id)
    new_person = reincarnate_echo(echo, world, legacy, transformed)
    if new_person:
        start_transition_turn(world)
        log.info("reincarnation", stage="success", echo_name=echo.name, old_person=player_person.name, new_person=new_person.name, transition_turn=world.transition_turn)
        notify("on_echo_spawned", turn, echo.name, new_person.name)
    else:
        log.error("reincarnation", stage="failed", error="no_candidate_found", echo_id=echo.id)
        notify("on_crisis", turn, "echo_death", echo.name)


def handle_reincarnation(
    world: World,
    notify,
    turn: int,
    log: Logger | None = None,
) -> None:
    """Handle the end of transition turn and complete reincarnation."""
    if log is None:
        log = _NoOpLogger()
    log.debug("reincarnation", stage="handling_end_of_transition", turn=turn)

    person = world.get_active_player_person()
    if not person:
        log.warning("reincarnation", stage="end_transition", error="no_active_player_person", turn=turn)
        return

    log.info("reincarnation_complete", person=person.name, turn=turn)
    notify("on_reincarnation_complete", turn, person.name)


def check_and_handle_reincarnation(world: World, notify, turn: int, log: Logger | None = None) -> bool:
    """
    Check if transition is due and handle reincarnation.
    Returns True if reincarnation was handled.
    """
    if is_in_transition(world):
        if world.transition_turn <= world.clock.action_tick:
            handle_reincarnation(world, notify, turn, log)
            end_transition_turn(world)
            return True
    return False


def track_echo_action(echo, action_name: str, turn: int) -> None:
    """Track action in echo's history."""
    if not echo:
        return
    if hasattr(echo, 'action_history'):
        echo.action_history.append(action_name)
        if len(echo.action_history) > 10:
            echo.action_history = echo.action_history[-10:]
    if hasattr(echo, 'last_action_turn'):
        echo.last_action_turn[action_name] = turn
