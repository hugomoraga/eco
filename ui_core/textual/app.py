"""
EcoTextual - Clean TUI for ECO simulation.
Inspired by posting's layout.
"""

from __future__ import annotations

import subprocess
import sys
import threading
from queue import Queue, Empty

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical

from game_core.i18n import t
from game_core.protocol import ActionCommand, QuitCommand, encode, decode, MessageType
from game_core.utils.logger import get_logger
from ui_core.textual.styles import CSS, ACTIONS
from ui_core.textual.widgets.header import HeaderBar

log = get_logger(__name__)
from ui_core.textual.widgets.echo import EchoPanel
from ui_core.textual.widgets.civ import CivPanel
from ui_core.textual.widgets.metrics import MetricsPanel
from ui_core.textual.widgets.actions import ActionsBar, make_actions_text
from ui_core.textual.widgets.log_panel import LogPanel


class EcoTextualApp(App):
    CSS = CSS

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("1", "do_0", ""), Binding("2", "do_1", ""),
        Binding("3", "do_2", ""), Binding("4", "do_3", ""),
        Binding("5", "do_4", ""), Binding("6", "do_5", ""),
        Binding("7", "do_6", ""), Binding("8", "do_7", ""),
    ]

    def __init__(self, cli_args: list[str] | None = None, theme_name: str = "nebula", **kwargs):
        super().__init__(**kwargs)
        self._cli_args = cli_args or [sys.executable, "-m", "game_core.cli", "--max-turns", "100"]
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
        self._proc: subprocess.Popen | None = None
        self._recv_queue: Queue = Queue()
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
        self._refresh_all()
        self._start_cli()

    def _refresh_all(self) -> None:
        self.query_one(HeaderBar).update_state(
            self._turn, self._world_tick, self._stability, self._pressure, self._population
        )
        self.query_one(EchoPanel).update_state(
            self._echo_name, self._echo_phase, self._echo_clarity, self._echo_essences, self._action_history, self._echo_influence, self._player_vitality
        )
        self.query_one(CivPanel).update_state(
            self._civ_name, self._echoes, self._circles, self._factions, self._population
        )
        self.query_one(MetricsPanel).update_state(
            self._pressure, self._legitimacy, self._resources, self._stability
        )
        self.query_one(ActionsBar).update(make_actions_text())

    def _start_cli(self) -> None:
        log.info("tui_start", cli_args=self._cli_args)
        self._proc = subprocess.Popen(
            self._cli_args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._stderr_reader, daemon=True).start()
        self.set_interval(0.1, self._poll)

    def _reader(self) -> None:
        for line in self._proc.stdout:
            if line.strip():
                self._recv_queue.put(line.strip())

    def _stderr_reader(self) -> None:
        for line in self._proc.stderr:
            if line.strip():
                log.debug("cli_stderr", line=line.strip())

    def _poll(self) -> None:
        try:
            while True:
                line = self._recv_queue.get_nowait()
                msg = decode(line)
                if msg:
                    d = msg.to_dict() if hasattr(msg, 'to_dict') else msg
                    self._handle(d)
        except Empty:
            pass

    def _handle(self, d: dict) -> None:
        from ui_core.textual.colors import GREEN, RED, CYAN, YELLOW, WHITE

        msg_type = d.get("type")
        log_panel = self.query_one(LogPanel)

        if msg_type == MessageType.READY.value:
            log.info("tui_ready", state=d.get("initial_state", {}).get("civ_name"))
            awakening = t("ui:awakening", default="The world awakens...")
            self._log_text += awakening + "\n"
            log_panel.write(f"[cyan]{awakening}[/cyan]\n")
            self._apply_ws(d.get("initial_state", {}))
            self._refresh_all()

        elif msg_type == MessageType.TURN_START.value:
            self._turn = d.get("turn", 0)
            ws = d.get("world_state", {})
            self._apply_ws(ws)
            log.info("tui_turn_start", turn=self._turn)
            turn_label = t("ui:turn", default="Turn")
            self._log_text += f"\n— {turn_label} {self._turn} —\n"
            log_panel.write(f"\n[yellow]— {turn_label} {self._turn} —[/yellow]\n")
            self._refresh_all()

        elif msg_type == MessageType.ACTION_RESULT.value:
            ok = d.get("success", False)
            action = d.get("action", "")
            message = d.get("message", "")
            log.info("tui_action_result", action=action, success=ok, message=message)
            if ok:
                self._log_text += f"+ {message}\n"
                log_panel.write(f"[green]+[/green] {message}\n")
            else:
                self._log_text += f"! {message}\n"
                log_panel.write(f"[red]![/red] {message}\n")
            if ok:
                self._action_history.append(action)
                if len(self._action_history) > 10:
                    self._action_history = self._action_history[-10:]
                self._refresh_all()

        elif msg_type == MessageType.EVENT.value:
            title = d.get("title", "")
            summary = d.get("summary", "")
            log.info("tui_event", title=title, summary=summary[:100] if summary else "")
            if summary:
                self._log_text += f"◆ {title}\n  {summary}\n"
                log_panel.write(f"[magenta]◆ {title}[/magenta]\n")
                log_panel.write(f"  {summary}\n")
            else:
                self._log_text += f"◆ {title}\n"
                log_panel.write(f"[magenta]◆ {title}[/magenta]\n")

        elif msg_type == MessageType.CRISIS.value:
            metric = d.get("metric", "")
            value = d.get("value", 0.0)
            log.warning("tui_crisis", metric=metric, value=value)
            self._log_text += f"⚠ Crisis: {metric} = {value:.1f}\n"
            log_panel.write(f"[red]⚠ Crisis: {metric} = {value:.1f}[/red]\n")

        elif msg_type == MessageType.TERMINATED.value:
            reason = d.get("reason", "")
            log.info("tui_terminated", reason=reason)
            story_ends = t("ui:story_ends", default="The story ends")
            self._log_text += f"\n{story_ends}: {reason}\n"
            log_panel.write(f"\n[cyan]{story_ends}: {reason}[/cyan]\n")

        elif msg_type == MessageType.ECHO_SPAWNED.value:
            parent = d.get("parent_name", "")
            daughter = d.get("daughter_name", "")
            log.info("tui_echo_spawned", parent=parent, daughter=daughter)
            self._log_text += f"↻ {parent} reincarnates as {daughter}\n"
            log_panel.write(f"[magenta]↻ {parent} reincarnates as {daughter}[/magenta]\n")

        elif msg_type == MessageType.REINCARNATION_COMPLETE.value:
            name = d.get("new_host_name", "")
            self._log_text += f"◇ New host emerges: {name}\n"
            log.write(f"[green]◇ New host emerges: {name}[/green]\n")

        elif msg_type == MessageType.CIRCLE_ACTIVITY.value:
            circle_name = d.get("circle_name", "")
            activity = d.get("activity", "")
            self._log_text += f"▸ {circle_name}: {activity}\n"
            log_panel.write(f"[yellow]▸[/yellow] {circle_name}: {activity}\n")

    def _apply_ws(self, ws: dict) -> None:
        self._civ_name = ws.get("civ_name", self._civ_name)
        self._pressure = ws.get("pressure", self._pressure)
        self._legitimacy = ws.get("legitimacy", self._legitimacy)
        self._resources = ws.get("resources_global", self._resources)
        self._world_tick = ws.get("world_tick", self._world_tick)
        self._echoes = ws.get("echo_count", self._echoes)
        self._circles = ws.get("circle_count", self._circles)
        self._factions = ws.get("faction_count", self._factions)
        self._population = ws.get("person_count", 21) * 1000
        self._echo_name = ws.get("echo_name", self._echo_name)
        self._echo_phase = ws.get("echo_phase", self._echo_phase)
        self._echo_clarity = ws.get("echo_clarity", self._echo_clarity)
        self._echo_essences = ws.get("echo_essences", self._echo_essences)
        self._player_vitality = ws.get("player_vitality", self._player_vitality)

    def _send(self, cmd) -> None:
        try:
            if self._proc and self._proc.stdin:
                encoded = encode(cmd)
                self._proc.stdin.write(encoded + "\n")
                self._proc.stdin.flush()
        except (BrokenPipeError, IOError):
            pass

    def _do(self, idx: int) -> None:
        if 0 <= idx < len(ACTIONS):
            action = ACTIONS[idx]
            if self._proc is None or self._proc.stdin is None:
                log.warning("tui_action_skipped", reason="no_proc_or_stdin", action=action)
                return
            try:
                log.info("tui_send_action", action=action, turn=self._turn)
                cmd = ActionCommand(turn=self._turn, action=action)
                encoded = encode(cmd)
                self._proc.stdin.write(encoded + "\n")
                self._proc.stdin.flush()
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

    def action_quit(self) -> None:
        self._send(QuitCommand())
        if self._proc:
            self._proc.terminate()
        self.exit()


if __name__ == "__main__":
    import argparse
    from ui_core.textual.theme import THEMES

    p = argparse.ArgumentParser()
    p.add_argument("--max-turns", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--theme", default="nebula", choices=list(THEMES.keys()))
    args = p.parse_args()

    cli = [sys.executable, "-m", "game_core.cli", "--max-turns", str(args.max_turns), "--seed", str(args.seed)]
    EcoTextualApp(cli_args=cli, theme_name=args.theme).run()