"""
SimulationEngine — headless core simulation.
Notifies observers on events. Knows nothing about display or input rendering.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from game_core.domain.entities import Echo, EchoAttribute, EchoPhase, World, Circle, Faction
from game_core.systems.random import SeededRandom
from game_core.systems.observer import SimulationObserver, NullObserver
from game_core.circle.circle_manager import process_circle_tick
from game_core.utils.debug_log import DebugLog, dbg


class _NoOpDebugLog:
    """Null object for debug logging when DebugLog is unavailable."""
    def turn_start(self, turn, world): pass
    def turn_end(self, turn, action): pass
    def input_mode(self, mode, input_class): pass
    def menu_interactive(self, interactive, reason): pass
    def menu_raw_enable(self, fd): pass
    def menu_raw_restore(self): pass
    def key_captured(self, key_desc, raw): pass
    def menu_selection(self, action, index): pass
    def menu_autoplay_trigger(self, reason): pass
    def fallback_to_text(self, reason): pass
    def fallback_to_autoplay(self, reason): pass
    def debug(self, msg): pass
    def info(self, msg): pass
    def warn(self, msg): pass
    def error(self, msg, exc=None): pass


class SimulationEngine:
    """
    Core simulation — headless, observer-based.

    Responsible for:
    - Managing world state
    - Executing actions
    - Notifying observers on events

    NOT responsible for:
    - Display (that's the observer's job)
    - Input handling (that's the input_source's job)
    - Rendering anything
    """

    def __init__(
        self,
        seed: int = 42,
        max_turns: int = 100,
        snapshot_interval: int = 10,
        run_dir: str | None = None,
        autoplay: bool = False,
        autoplay_mode: str = "autoplay",
        autoplay_style: str = "preservationist",
        ai_adapter_type: str = "mock",
        verbose: bool = False,
        input_source: "InputSource | None" = None,
    ):
        self.seed = seed
        self.max_turns = max_turns
        self.snapshot_interval = snapshot_interval
        self.autoplay = autoplay
        self.autoplay_mode = autoplay_mode
        self.autoplay_style = autoplay_style
        self.ai_adapter_type = ai_adapter_type
        self.verbose = verbose
        self.rng = SeededRandom.get_instance(seed)
        self.run_dir = Path(run_dir) if run_dir else self._create_run_dir()
        if not self.run_dir.is_absolute():
            base = Path(__file__).parent.parent.parent
            self.run_dir = base / self.run_dir
        self.log_file = self.run_dir / "simulation.jsonl"
        self.snapshots_dir = self.run_dir / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.turn = 0
        self.world = self._create_initial_world()
        self.autoplayer_engine = None

        DebugLog.init(self.run_dir)
        _dbg = DebugLog.get()
        self._dbg = _dbg if _dbg else _NoOpDebugLog()

        self._observers: list[SimulationObserver] = [NullObserver()]

        if input_source is not None:
            self.input_source = input_source
        else:
            from player_core import create_input_source
            self.input_source = create_input_source()

    # ─── Observer management ─────────────────────────────────────────────

    def register_observer(self, observer: SimulationObserver) -> None:
        """Attach an observer (e.g., ConsoleDisplay)."""
        self._observers.append(observer)

    def _notify(self, method_name: str, *args, **kwargs) -> None:
        """Notify all observers that implement the method."""
        for obs in self._observers:
            method = getattr(obs, method_name, None)
            if callable(method):
                try:
                    method(*args, **kwargs)
                except Exception as e:
                    self._dbg.error(f"Observer {type(obs).__name__}.{method_name} failed", e)

    # ─── World setup ─────────────────────────────────────────────────────

    def _create_run_dir(self) -> Path:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = Path(__file__).parent.parent.parent
        run_dir = project_root / "runs" / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _create_initial_world(self) -> World:
        from game_core.domain.tag_generator import TagGenerator

        tag_gen = TagGenerator(seed=self.seed)
        echo = Echo(
            name="First Echo",
            essence="anarchism",
            phase=EchoPhase.ACTIVE,
            attributes=[
                EchoAttribute(label="clarity", value=60.0),
                EchoAttribute(label="resonance", value=50.0),
                EchoAttribute(label="presence", value=40.0),
                EchoAttribute(label="memory", value=30.0),
                EchoAttribute(label="will", value=70.0),
                EchoAttribute(label="shadow", value=20.0),
            ],
        )
        echo.known_tags = tag_gen.generate_for_essence("anarchism", count=3)
        echo.genealogical_lineage = [echo.essence]

        faction = Faction(
            name="Circulo Libertario",
            essence=echo.essence,
            ideology_tags=[t.to_semantic_key() for t in echo.known_tags],
            members=5,
            influence=10.0,
            resources={"food": 50, "infrastructure": 30, "energy": 20},
            goals=["expand_influence", "spread_idea"],
        )

        world = World(
            echoes=[echo],
            factions=[faction],
            active_echo_id=echo.id,
        )
        return world

    def _load_snapshot(self, path: str) -> World:
        with open(path) as f:
            data = json.load(f)
        return World.model_validate(data)

    def _save_snapshot(self, world: World, turn: int) -> str:
        path = self.snapshots_dir / f"snapshot_{turn:05d}.json"
        with open(path, "w") as f:
            json.dump(world.model_dump(), f, indent=2)
        return str(path)

    def _log_event(self, event_type: str, data: dict) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "turn": self.turn,
            "event_type": event_type,
            "data": data,
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ─── Main loop ──────────────────────────────────────────────────────

    def run(self) -> dict:
        from game_core.actions.circle_actions import FoundCircle, JoinCircle, LeaveCircle
        from game_core.actions.manifesto_actions import WriteManifesto
        from game_core.actions.social_actions import PropagateIdea, Talk, Sabotage, Ritualize
        from game_core.systems.faction_tick import FactionTickSystem
        from game_core.systems.event_generator import EventGenerator
        from game_core.domain.npc_generator import NPCGenerator
        from game_core.autoplayer import AutoplayMode, AutoplayerEngine

        # AI adapter
        from game_core.ai import MockAdapter, MiniMaxAdapter, OpenAIAdapter
        if self.ai_adapter_type == "openai":
            try:
                ai_adapter = OpenAIAdapter()
            except Exception:
                ai_adapter = MockAdapter()
        elif self.ai_adapter_type == "minimax":
            try:
                ai_adapter = MiniMaxAdapter()
            except Exception:
                ai_adapter = MockAdapter()
        else:
            ai_adapter = MockAdapter()

        action_classes = {
            "found_circle": FoundCircle,
            "join_circle": JoinCircle,
            "leave_circle": LeaveCircle,
            "propagate_idea": PropagateIdea,
            "talk": Talk,
            "write_manifesto": WriteManifesto,
            "sabotage": Sabotage,
            "ritualize": Ritualize,
        }

        faction_system = FactionTickSystem(seed=self.seed)
        faction_tick_interval = 3
        event_gen = EventGenerator(ai_adapter, seed=self.seed)
        npc_gen = NPCGenerator(ai_adapter, seed=self.seed)
        event_interval = 5

        if self.autoplay:
            mode = AutoplayMode(self.autoplay_mode) if self.autoplay_mode in [m.value for m in AutoplayMode] else AutoplayMode.AUTOPLAY
            self.autoplayer_engine = AutoplayerEngine(
                seed=self.seed,
                mode=mode,
                style_id=self.autoplay_style,
            )

        # Initial world state snapshot
        self._notify("on_world_state", 0, self.world)

        while self.turn < self.max_turns:
            self.turn += 1
            self._dbg.turn_start(self.turn, self.world)

            # Advance world clock
            self.world.clock.advance(1)

            # Notify turn start — display renders initial frame
            self._notify("on_turn_start", self.turn, self.world)

            # Track old metrics for change detection
            old_metrics = self._snapshot_metrics()

            echo = self.world.get_active_echo()

            # World events
            if self.turn % event_interval == 0:
                context_for_event = {
                    "turn": self.turn,
                    "world_tick": self.world.clock.world_tick,
                    "resources": self.world.resources,
                    "echo_essence": echo.essence if echo else "anarchism",
                }
                event = event_gen.generate(context_for_event)
                self._notify("on_event", self.turn, "event", event.title, event.summary)
                self._log_event("event", {
                    "title": event.title,
                    "summary": event.summary,
                    "canonical": event.canonical,
                })

            # Crisis check
            if self.world.is_crisis():
                self._notify("on_crisis", self.turn, "pressure", self.world.pressure)

            # Get action from input source (returns action name string only)
            action_name = self.input_source.get_action(self.turn, self.world)

            # Autoplay if needed
            if action_name is None and self.autoplay and echo and self.autoplayer_engine:
                available_action_names = list(action_classes.keys())
                decision = self.autoplayer_engine.select_action(echo, self.world, available_action_names)
                self._log_event("autoplay_decision", decision.model_dump())
                action_name = decision.selected_action
                self._notify("on_action_selected", self.turn, None)  # autoplay
            elif action_name:
                self._notify("on_action_selected", self.turn, action_name)

            # Execute action
            result = None
            if action_name and action_name in action_classes:
                action = action_classes[action_name]()
                from game_core.actions.base import ActionContext

                context = ActionContext(
                    world_tick=self.world.clock.world_tick,
                    action_tick=self.world.clock.action_tick,
                    autoplay=(action_name is None),
                )
                if action.can_execute(echo, self.world, context):
                    result = action.execute(echo, self.world, context)
                    self._notify("on_action_result", self.turn, action_name, result)

                    # Track action history (guard against no echo)
                    if echo:
                        if hasattr(echo, 'action_history'):
                            echo.action_history.append(action_name)
                            if len(echo.action_history) > 10:
                                echo.action_history = echo.action_history[-10:]
                        if hasattr(echo, 'last_action_turn'):
                            echo.last_action_turn[action_name] = self.turn

            # Faction tick
            if self.turn % faction_tick_interval == 0 and self.world.factions:
                faction_results = faction_system.tick(self.world)
                for fr in faction_results:
                    self._log_event("faction_tick", fr)

            # Circle processing
            for circle in self.world.circles:
                activities = process_circle_tick(circle, self.world, self.rng)
                for activity in activities:
                    self._notify("on_circle_activity", self.turn, circle.name, activity)

                # NPC generation for mature circles
                if circle.member_count >= 3:
                    if len(getattr(circle, 'npcs', [])) < circle.member_count:
                        npc = npc_gen.generate({"essence": circle.essence, "context": "circle_growth"})
                        if not hasattr(circle, 'npcs'):
                            circle.npcs = []
                        circle.npcs.append(npc.id)
                        self._notify("on_npc_created", self.turn, npc.name, npc.role)
                        self._log_event("npc_created", {
                            "npc_id": npc.id,
                            "npc_name": npc.name,
                            "circle_id": circle.id,
                        })

            # World metric evolution
            drift = self.world.evolve_metrics(self.rng)
            new_metrics = self._snapshot_metrics()

            # Notify metric changes
            for metric, new_val in new_metrics.items():
                old_val = old_metrics.get(metric, new_val)
                if abs(new_val - old_val) >= 0.5:
                    self._notify("on_metric_changed", self.turn, metric, old_val, new_val)

            # Notify turn end
            self._notify("on_turn_end", self.turn, self.world, action_name)
            self._dbg.turn_end(self.turn, action_name)

            # JSONL log
            self._log_event("tick", {
                "turn": self.turn,
                "world_tick": self.world.clock.world_tick,
                "action_result": result.model_dump() if result else None,
            })

            # Snapshot
            if self.turn % self.snapshot_interval == 0:
                self._save_snapshot(self.world, self.turn)
                self._notify("on_world_state", self.turn, self.world)

        return {"turns": self.turn, "run_dir": str(self.run_dir)}

    def _snapshot_metrics(self) -> dict:
        """Capture current world metrics."""
        return {
            "pressure": self.world.pressure,
            "legitimacy": self.world.legitimacy,
            "resources_global": self.world.resources_global,
        }