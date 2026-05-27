"""
EcoTextual - Clean TUI for ECO simulation.
Direct integration with engine (no subprocess).
"""

from __future__ import annotations

import threading
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical

from adapters.i18n import t
from core.application.processors.simulation import SimulationEngine
from core.application.players.human import HumanPlayer
from core.application.processors.observer import SimulationObserver
from infra.logging import get_logger
from adapters.tui.textual.styles import CSS, ACTIONS
from adapters.tui.textual.widgets.header import HeaderBar

log = get_logger(__name__)
from adapters.tui.textual.widgets.echo import EchoPanel
from adapters.tui.textual.widgets.civ import CivPanel
from adapters.tui.textual.widgets.metrics import MetricsPanel
from adapters.tui.textual.widgets.actions import ActionsBar, make_actions_text
from adapters.tui.textual.widgets.log_panel import LogPanel


def _serialize_world(turn: int, world) -> dict:
    selected_civ = world.civs[0] if world.civs else None
    civ_name = selected_civ.name if selected_civ else "Unknown"

    echo = world.get_active_echo()
    echo_name = echo.name if echo else "---"
    echo_essence = echo.dominant_essence if echo else "---"
    echo_phase = echo.phase.value if echo and hasattr(echo.phase, 'value') else "dormant"
    echo_clarity = echo.get_attribute("clarity").value if echo and echo.get_attribute("clarity") else 50.0
    echo_essences = [e.essence for e in echo.essence_profile.dominant] if echo and echo.essence_profile else []

    person = world.get_active_player_person()
    player_vitality = person.vitality if person else 100.0

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
        "player_vitality": player_vitality,
    }


class TuiObserver(SimulationObserver):
    """Observer that bridges engine events to TUI updates."""

    def __init__(self, app):
        self._app = app

    def on_ready(self, initial_state: dict):
        pass

    def on_world_start(self, world):
        pass

    def on_turn_start(self, turn: int, world):
        self._app._on_turn_start(turn, world)

    def on_event(self, turn: int, event_type: str, title: str, summary: str = ""):
        self._app._on_event(turn, event_type, title, summary)

    def on_crisis(self, turn: int, metric: str, value: float):
        self._app._on_crisis(turn, metric, value)

    def on_action_selected(self, turn: int, action_name: str | None):
        pass

    def on_action_result(self, turn: int, action_name: str, result):
        self._app._on_action_result(turn, action_name, result)

    def on_circle_activity(self, turn: int, circle_name: str, activity: str):
        self._app._on_circle_activity(turn, circle_name, activity)

    def on_npc_created(self, turn: int, npc_name: str, npc_role: str):
        pass

    def on_npc_action(self, turn: int, npc_name: str, action: str, message: str):
        self._app._on_npc_action(turn, npc_name, action, message)

    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float):
        pass

    def on_turn_end(self, turn: int, world, action_name: str | None):
        pass

    def on_world_state(self, turn: int, world):
        self._app._on_world_state(turn, world)

    def on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str):
        self._app._on_echo_spawned(turn, parent_name, daughter_name)

    def on_reincarnation_complete(self, turn: int, new_host_name: str):
        self._app._on_reincarnation_complete(turn, new_host_name)

    def on_story_beat(self, turn: int, world, goal_results: list):
        pass

    def on_finale(self, finale_data: dict):
        self._app._on_finale(finale_data)


class EcoTextualApp(App):
    CSS = CSS

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("1", "do_0", ""), Binding("2", "do_1", ""),
        Binding("3", "do_2", ""), Binding("4", "do_3", ""),
        Binding("5", "do_4", ""), Binding("6", "do_5", ""),
        Binding("7", "do_6", ""), Binding("8", "do_7", ""),
    ]

    def __init__(self, max_turns: int = 100, seed: int = 42, theme_name: str = "nebula", **kwargs):
        super().__init__(**kwargs)
        self._max_turns = max_turns
        self._seed = seed
        self._turn = 0
        self._world_tick = 0
        self._pressure = 30.0
        self._legitimacy = 60.0
        self._resources = 70.0
        self._stability = 50.0
        self._population = 0
        self._echo_name = "---"
        self._echo_phase = "---"
        self._echo_clarity = 0.0
        self._echo_essences: list[str] = []
        self._echo_influence = 0.0
        self._player_vitality = 100.0
        self._action_history: list[str] = []
        self._civ_name = "---"
        self._echoes = 0
        self._circles = 0
        self._factions = 1
        self._engine: SimulationEngine | None = None
        self._engine_thread: threading.Thread | None = None
        self._running = True
        self._game_over = False
        self._simulation_complete_shown = False
        self._log_text: str = ""

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        with Horizontal(id="main-area"):
            with Vertical(id="left-col"):
                yield EchoPanel()
                yield CivPanel()
            with Vertical(id="right-col"):
                yield MetricsPanel()
                yield LogPanel()
        with Horizontal(id="action-bar"):
            yield ActionsBar()

    def on_mount(self) -> None:
        self._start_engine()

    def _start_engine(self) -> None:
        from infra.logging import get_logger
        engine_log = get_logger("engine_start")
        engine_log.warning("ENGINE_CREATED", max_turns=self._max_turns, seed=self._seed)
        self._human_player = HumanPlayer()
        self._engine = SimulationEngine(
            seed=self._seed,
            max_turns=self._max_turns,
            player=self._human_player,
            civ_id="default",
        )
        observer = TuiObserver(self)
        self._engine.register_observer(observer)

        ws = _serialize_world(0, self._engine.world)
        self._apply_ws(ws)
        awakening = t("ui:awakening", default="The world awakens...")
        self._log_text += awakening + "\n"
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"[cyan]{awakening}[/cyan]\n")
        self._refresh_all()

        self._engine_thread = threading.Thread(target=self._run_engine, daemon=True)
        self._engine_thread.start()

        self.set_interval(0.1, self._poll)

    def _run_engine(self) -> None:
        if self._engine:
            try:
                self._engine.run()
                self._game_over = True
                log.info("engine_finished", turns=self._engine.turn)
            except Exception as e:
                log.error(
                    "engine_thread_crash",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                self._game_over = True
                raise

    def _poll(self) -> None:
        if self._game_over and self._engine and not self._simulation_complete_shown:
            self._simulation_complete_shown = True
            log_panel = self.query_one(LogPanel)
            log_panel.write(f"\n[green]═══ SIMULATION COMPLETE ═══[/green]\n")
            log_panel.write(f"[cyan]Turns played: {self._engine.turn}[/cyan]\n")
            log_panel.write(f"[dim]Press 'q' to quit[/dim]\n")

    def _apply_ws(self, ws: dict) -> None:
        self._civ_name = ws.get("civ_name", self._civ_name)
        self._pressure = ws.get("pressure", self._pressure)
        self._legitimacy = ws.get("legitimacy", self._legitimacy)
        self._resources = ws.get("resources_global", self._resources)
        self._world_tick = ws.get("world_tick", self._world_tick)
        self._echoes = ws.get("person_count", 0) // 1000
        self._circles = ws.get("circle_count", self._circles)
        self._factions = ws.get("faction_count", self._factions)
        self._population = ws.get("person_count", 21) * 1000
        self._echo_name = ws.get("echo_name", self._echo_name)
        self._echo_phase = ws.get("echo_phase", self._echo_phase)
        self._echo_clarity = ws.get("echo_clarity", self._echo_clarity)
        self._echo_essences = ws.get("echo_essences", self._echo_essences)
        self._player_vitality = ws.get("player_vitality", self._player_vitality)

    def _refresh_all(self) -> None:
        self.query_one(HeaderBar).update_state(
            self._turn, self._world_tick, self._stability, self._pressure, self._population
        )
        self.query_one(EchoPanel).update_state(
            self._echo_name, self._echo_phase, self._echo_clarity, self._echo_essences,
            self._action_history, self._echo_influence, self._player_vitality
        )
        self.query_one(CivPanel).update_state(
            self._civ_name, self._echoes, self._circles, self._factions, self._population
        )
        self.query_one(MetricsPanel).update_state(
            self._pressure, self._legitimacy, self._resources, self._stability
        )
        self.query_one(ActionsBar).update(make_actions_text())

    def _on_turn_start(self, turn: int, world) -> None:
        self._turn = turn
        ws = _serialize_world(turn, world)
        self._apply_ws(ws)
        log.info("tui_turn_start", turn=turn)
        turn_label = t("ui:turn", default="Turn")
        self._log_text += f"\n— {turn_label} {turn} —\n"
        self.call_after_refresh(self._write_turn_start, turn_label, turn)

    def _write_turn_start(self, turn_label: str, turn: int) -> None:
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"\n[yellow]— {turn_label} {turn} —[/yellow]\n")
        self._refresh_all()

    def _on_event(self, turn: int, event_type: str, title: str, summary: str) -> None:
        log.info("tui_event", title=title, summary=summary[:100] if summary else "")
        self.call_after_refresh(self._write_event, title, summary)

    def _write_event(self, title: str, summary: str) -> None:
        from adapters.tui.components import Components
        log_panel = self.query_one(LogPanel)
        panel = Components.event_banner("event", title, summary)
        log_panel.write(panel)

    def _on_crisis(self, turn: int, metric: str, value: float) -> None:
        log.warning("tui_crisis", metric=metric, value=value)
        self.call_after_refresh(self._write_crisis, metric, value)

    def _write_crisis(self, metric: str, value: float) -> None:
        self._log_text += f"⚠ Crisis: {metric} = {value:.1f}\n"
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"[red]⚠ Crisis: {metric} = {value:.1f}[/red]\n")

    def _on_action_result(self, turn: int, action_name: str, result) -> None:
        ok = getattr(result, 'success', False)
        message = getattr(result, 'message', str(result))
        log.info("tui_action_result", action=action_name, success=ok, message=message)
        self.call_after_refresh(self._write_action_result, ok, message)

    def _write_action_result(self, ok: bool, message: str) -> None:
        log_panel = self.query_one(LogPanel)
        if ok:
            self._log_text += f"+ {message}\n"
            log_panel.write(f"[green]+[/green] {message}\n")
        else:
            self._log_text += f"! {message}\n"
            log_panel.write(f"[red]![/red] {message}\n")
        if ok:
            self._action_history.append(message)
            if len(self._action_history) > 10:
                self._action_history = self._action_history[-10:]
            self._refresh_all()

    def _on_world_state(self, turn: int, world) -> None:
        ws = _serialize_world(turn, world)
        self._apply_ws(ws)
        self._refresh_all()

    def _on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str) -> None:
        log.info("tui_echo_spawned", parent=parent_name, daughter=daughter_name)
        self._log_text += f"↻ {parent_name} reincarnates as {daughter_name}\n"
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"[magenta]↻ {parent_name} reincarnates as {daughter_name}[/magenta]\n")

    def _on_reincarnation_complete(self, turn: int, new_host_name: str) -> None:
        self._log_text += f"◇ New host emerges: {new_host_name}\n"
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"[green]◇ New host emerges: {new_host_name}[/green]\n")

    def _on_circle_activity(self, turn: int, circle_name: str, activity: str) -> None:
        self._log_text += f"▸ {circle_name}: {activity}\n"
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"[yellow]▸[/yellow] {circle_name}: {activity}\n")

    def _on_npc_action(self, turn: int, npc_name: str, action: str, message: str) -> None:
        self._log_text += f"▸ {npc_name}: {message}\n"
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"[magenta]▸[/magenta] {npc_name}: {message}\n")

    def _do(self, idx: int) -> None:
        if 0 <= idx < len(ACTIONS):
            action = ACTIONS[idx]
            if self._engine is None:
                log.warning("tui_action_skipped", reason="no_engine")
                return
            if self._human_player is None:
                log.warning("tui_action_skipped", reason="no_human_player")
                return
            try:
                log.info("tui_send_action", action=action, turn=self._turn)
                self._human_player.submit_action(action)
            except Exception as e:
                log.error("tui_action_failed", action=action, error=str(e))

    def action_do_0(self) -> None: self._do(0)
    def action_do_1(self) -> None: self._do(1)
    def action_do_2(self) -> None: self._do(2)
    def action_do_3(self) -> None: self._do(3)
    def action_do_4(self) -> None: self._do(4)
    def action_do_5(self) -> None: self._do(5)
    def action_do_6(self) -> None: self._do(6)
    def action_do_7(self) -> None: self._do(7)

    def _on_finale(self, finale_data: dict) -> None:
        outcome = finale_data.get("outcome", "unknown")
        outcome_text = finale_data.get("outcome_text", "")
        winner = finale_data.get("winner_name", "Unknown")
        log_panel = self.query_one(LogPanel)
        log_panel.write(f"\n[yellow]═══ {outcome.upper()} ═══[/yellow]\n")
        log_panel.write(f"[cyan]{outcome_text}[/cyan]\n")
        log_panel.write(f"[dim]Winner: {winner}[/dim]\n")

    def action_quit(self) -> None:
        self._running = False
        self.exit()
