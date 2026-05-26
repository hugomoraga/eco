"""
game_core.cli - Headless simulation process with JSON stdin/stdout protocol.
Run as: python -m game_core.cli [options]

Protocol:
  - stdin: ActionCommand, QueryCommand, QuitCommand (JSON lines)
  - stdout: events (ready, turn_start, turn_end, tick, etc.)

The CLI wraps SimulationEngine and translates observer callbacks to protocol messages.
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
import queue
from dataclasses import dataclass
from typing import TYPE_CHECKING

from game_core.protocol import (
    ActionCommand,
    QueryCommand,
    QuitCommand,
    ReadyEvent,
    TurnStartEvent,
    TurnEndEvent,
    ActionResultEvent,
    GameEvent,
    CrisisEvent,
    WorldStateEvent,
    TickEvent,
    TerminatedEvent,
    ErrorEvent,
    EchoSpawnedEvent,
    ReincarnationCompleteEvent,
    encode,
    decode_command,
    MessageType,
    QueryType,
)
from game_core.systems.simulation import SimulationEngine, SimulationObserver
from game_core.systems.random import SeededRandom

if TYPE_CHECKING:
    from game_core.domain.entities import World


def _serialize_world(turn: int, world) -> dict:
    selected_civ = world.civs[0] if world.civs else None
    civ_name = selected_civ.name if selected_civ else "Unknown"

    echo = world.get_active_echo()
    echo_name = echo.name if echo else "---"
    echo_essence = echo.dominant_essence if echo else "---"
    echo_phase = echo.phase.value if echo and hasattr(echo.phase, 'value') else "dormant"
    echo_clarity = echo.get_attribute("clarity").value if echo and echo.get_attribute("clarity") else 50.0
    echo_essences = [e.essence for e in echo.essence_profile.dominant] if echo and echo.essence_profile else []

    return {
        "turn": turn,
        "civ_name": civ_name,
        "pressure": world.pressure,
        "legitimacy": world.legitimacy,
        "resources_global": world.resources_global,
        "world_tick": world.clock.world_tick,
        "active_echo_id": getattr(world, 'active_echo_id', None),
        "circle_count": len(getattr(world, 'circles', [])),
        "faction_count": len(getattr(world, 'factions', [])),
        "person_count": len(getattr(world, 'persons', [])),
        "echo_name": echo_name,
        "echo_essence": echo_essence,
        "echo_phase": echo_phase,
        "echo_clarity": echo_clarity,
        "echo_essences": echo_essences,
    }


def _serialize_metrics(world) -> dict:
    return {
        "pressure": world.pressure,
        "legitimacy": world.legitimacy,
        "resources_global": world.resources_global,
    }


class ProtocolObserver(SimulationObserver):
    def __init__(self, emit_fn):
        self._emit = emit_fn

    def on_ready(self, initial_state: dict):
        pass

    def on_world_start(self, world):
        pass

    def on_turn_start(self, turn: int, world):
        self._emit(TurnStartEvent(
            turn=turn,
            world_tick=world.clock.world_tick,
            world_state=_serialize_world(turn, world),
        ))

    def on_event(self, turn: int, event_type: str, title: str, summary: str = ""):
        self._emit(GameEvent(turn=turn, event_type=event_type, title=title, summary=summary))

    def on_crisis(self, turn: int, metric: str, value: float):
        self._emit(CrisisEvent(turn=turn, metric=metric, value=value))

    def on_action_selected(self, turn: int, action_name: str | None):
        pass

    def on_action_result(self, turn: int, action_name: str, result):
        msg = getattr(result, 'message', str(result))
        success = getattr(result, 'success', True)
        delta = getattr(result, 'model_dump', lambda: {})()
        self._emit(ActionResultEvent(
            turn=turn,
            action=action_name,
            success=success,
            message=msg,
            delta=delta,
        ))

    def on_circle_activity(self, turn: int, circle_name: str, activity: str):
        pass

    def on_npc_created(self, turn: int, npc_name: str, npc_role: str):
        pass

    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float):
        pass

    def on_turn_end(self, turn: int, world, action_name: str | None):
        self._emit(TurnEndEvent(
            turn=turn,
            world_tick=world.clock.world_tick,
            action_taken=action_name,
        ))

    def on_world_state(self, turn: int, world):
        self._emit(WorldStateEvent(
            turn=turn,
            civ=getattr(world, 'civ', {}),
            echo=getattr(world, 'echo', {}),
            metrics=_serialize_metrics(world),
            entities={},
        ))

    def on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str):
        self._emit(EchoSpawnedEvent(
            turn=turn,
            parent_name=parent_name,
            daughter_name=daughter_name,
        ))

    def on_reincarnation_complete(self, turn: int, new_host_name: str):
        self._emit(ReincarnationCompleteEvent(
            turn=turn,
            new_host_name=new_host_name,
        ))


class StdinInputSource:
    def __init__(self, cmd_queue: queue.Queue):
        self._queue = cmd_queue
        self._mode = "player"

    @property
    def mode(self) -> str:
        return self._mode

    def get_action(self, turn: int, world: World) -> str | None:
        try:
            item = self._queue.get(timeout=300)
            if isinstance(item, ActionCommand):
                return item.action
            return None
        except queue.Empty:
            return None

    def supports_realtime_override(self) -> bool:
        return True

    def inject_action(self, action: str) -> None:
        pass


def _stdin_reader(cmd_queue: queue.Queue):
    for line in sys.stdin:
        if not line.strip():
            continue
        cmd = decode_command(line.strip())
        if cmd is None:
            continue
        if isinstance(cmd, QuitCommand):
            cmd_queue.put(QuitCommand())
            break
        cmd_queue.put(cmd)
        print(f"CLI: received command: {line.strip()}", flush=True)


def run_cli():
    parser = argparse.ArgumentParser(description="ECO Simulation Engine CLI")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-turns", type=int, default=100)
    parser.add_argument("--autoplay", action="store_true")
    parser.add_argument("--autoplay-mode", default="autoplay")
    parser.add_argument("--autoplay-style", default="preservationist")
    args = parser.parse_args()

    cmd_queue: queue.Queue = queue.Queue()

    input_source = StdinInputSource(cmd_queue)

    engine = SimulationEngine(
        seed=args.seed,
        max_turns=args.max_turns,
        autoplay=args.autoplay,
        autoplay_mode=args.autoplay_mode,
        autoplay_style=args.autoplay_style,
        civ_id="default",
        input_source=input_source,
    )

    def emit(msg):
        print(encode(msg), flush=True)

    observer = ProtocolObserver(emit)
    engine.register_observer(observer)

    ready = ReadyEvent(initial_state=_serialize_world(0, engine.world))
    emit(ready)

    stdin_thread = threading.Thread(target=_stdin_reader, args=(cmd_queue,), daemon=True)
    stdin_thread.start()

    result = engine.run()

    emit(TerminatedEvent(reason="completed"))


if __name__ == "__main__":
    run_cli()