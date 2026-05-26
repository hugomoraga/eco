"""
simulation_engine.py — Core simulation orchestrator.

Coordinates world state, turn processing, and observer notifications.
Does NOT handle display or input (that's the adapter's job).

Split modules:
- core/systems/world_builder.py: World creation
- core/systems/action_registry.py: Action class registry
- core/systems/turn_context.py: Turn processing helpers
- core/systems/simulation_api.py: Adapter-friendly API
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from core.domain.world import World
from adapters.i18n import get_lang
from core.systems.action_registry import ACTION_CLASSES
from core.systems.circle_processor import process_circle_activities
from core.systems.goal_processor import evaluate_goals, initialize_goals
from core.systems.npc_processor import process_npc_turns
from core.systems.observer import NullObserver, SimulationObserver
from core.systems.random import SeededRandom
from core.systems.simulation_api import SimulationAPI
from core.systems.turn_context import (
    check_and_handle_reincarnation,
    handle_npc_damage_to_player,
    snapshot_metrics,
    track_echo_action,
)
from core.systems.world_builder import build_initial_world
from core.utils.logger import get_logger, init_logger


class SimulationEngine:
    """
    Core simulation — headless, observer-based.

    Responsible for:
    - Managing world state
    - Coordinating turn processing
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
        input_source=None,
        civ_id: str = "default",
    ):
        self.seed = seed
        self.civ_id = civ_id
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
        self.world = build_initial_world(seed, civ_id)
        self.autoplayer_engine = None
        self._running = False
        self.player_goal = None
        self.npc_goals = []

        init_logger(self.run_dir)
        self._log = get_logger(__name__)

        self._observers: list[SimulationObserver] = [NullObserver()]
        self._api = SimulationAPI(self)

        if input_source is not None:
            self.input_source = input_source
        else:
            from adapters.ai.input_source import create_input_source
            self.input_source = create_input_source(autoplay=self.autoplay)

    @property
    def api(self) -> SimulationAPI:
        """Public API for adapters."""
        return self._api

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
                    self._log.exception("observer_notification_failed", observer=type(obs).__name__, method=method_name, error=str(e))

    # ─── Run directory ──────────────────────────────────────────────────

    def _create_run_dir(self) -> Path:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = Path(__file__).parent.parent.parent
        run_dir = project_root / "runs" / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    # ─── Snapshot/logging ───────────────────────────────────────────────

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

    def _serialize_world(self) -> dict:
        """Serialize world state for adapters."""
        return self.world.model_dump()

    # ─── Main loop ──────────────────────────────────────────────────────

    def run(self) -> dict:
        self._running = True

        from adapters.autoplayer import AutoplayerEngine
        from core.shared import AutoplayMode
        from core.systems.event_generator import EventGenerator
        from core.systems.event_pool import EventPool
        from core.systems.faction_tick import FactionTickSystem

        ai_adapter = self._create_ai_adapter()

        faction_system = FactionTickSystem(seed=self.seed)
        faction_tick_interval = 3
        event_pool = EventPool()
        event_gen = EventGenerator(ai_adapter, pool=event_pool, seed=self.seed)
        event_interval = 5

        if self.autoplay:
            mode = AutoplayMode(self.autoplay_mode) if self.autoplay_mode in [m.value for m in AutoplayMode] else AutoplayMode.AUTOPLAY
            self.autoplayer_engine = AutoplayerEngine(
                seed=self.seed,
                mode=mode,
                style_id=self.autoplay_style,
            )

        self._notify("on_world_state", 0, self.world)
        self._notify("on_world_start", self.world)

        initial_npcs = self._spawn_initial_npcs()
        self.player_goal, self.npc_goals = initialize_goals(
            initial_npcs, self.max_turns, self.seed, self._notify, self._log
        )

        from adapters.autoplayer import NPCActionExecutor
        npc_executor = NPCActionExecutor(seed=self.seed)

        while self.turn < self.max_turns:
            self._execute_turn(
                npc_executor=npc_executor,
                ai_adapter=ai_adapter,
                faction_system=faction_system,
                event_gen=event_gen,
                event_interval=event_interval,
                faction_tick_interval=faction_tick_interval,
            )

        finale_data = self._generate_finale()
        self._notify("on_finale", finale_data)

        self._running = False
        return {"turns": self.turn, "run_dir": str(self.run_dir), "finale": finale_data}

    def _create_ai_adapter(self):
        from adapters.ai import MiniMaxAdapter, MockAdapter, OpenAIAdapter

        if self.ai_adapter_type == "openai":
            try:
                return OpenAIAdapter()
            except Exception:
                return MockAdapter()
        elif self.ai_adapter_type == "minimax":
            try:
                return MiniMaxAdapter()
            except Exception:
                return MockAdapter()
        return MockAdapter()

    def _spawn_initial_npcs(self):
        from core.factories import spawn_npcs_to_world

        initial_npcs = spawn_npcs_to_world(self.world, seed=self.seed, max_per_dataset=5)
        for npc in initial_npcs:
            self._notify("on_npc_created", 0, npc.name, npc.role)
            self._log.debug("npc_spawned_at_start", npc_id=npc.id, npc_name=npc.name, archetype=npc.archetype)
        if initial_npcs:
            self._log.info("npcs_spawned", count=len(initial_npcs))
        return initial_npcs

    def _execute_turn(self, npc_executor, ai_adapter, faction_system, event_gen, event_interval, faction_tick_interval):
        from core.application.actions.base import ActionContext
        from core.systems.damage import should_deal_damage_to_player

        self.turn += 1
        self._log.info("turn_start", turn=self.turn, pressure=self.world.pressure, legitimacy=self.world.legitimacy, resources=self.world.resources_global)

        self.world.clock.advance(1)
        self._notify("on_turn_start", self.turn, self.world)

        old_metrics = snapshot_metrics(self.world)
        echo = self.world.get_active_echo()

        process_npc_turns(self.world, self.seed, self.turn, npc_executor, ai_adapter, self._notify, self._log, self._log_event)
        process_circle_activities(self.world, self.rng, self.seed, self.turn, ai_adapter, self._notify, self._log, self._log_event)

        self._generate_world_event(event_gen, event_interval, echo)

        if self.world.is_crisis():
            self._notify("on_crisis", self.turn, "pressure", self.world.pressure)

        action_name = self._get_player_action(echo)

        result = self._execute_player_action(echo, action_name, should_deal_damage_to_player)

        check_and_handle_reincarnation(self.world, self._notify, self.turn)

        if self.turn % faction_tick_interval == 0 and self.world.factions:
            faction_results = faction_system.tick(self.world)
            for fr in faction_results:
                self._log_event("faction_tick", fr)

        self.world.evolve_metrics(self.rng)
        new_metrics = snapshot_metrics(self.world)
        for metric, new_val in new_metrics.items():
            old_val = old_metrics.get(metric, new_val)
            if abs(new_val - old_val) >= 0.5:
                self._notify("on_metric_changed", self.turn, metric, old_val, new_val)

        self._notify("on_turn_end", self.turn, self.world, action_name)
        self._log.info("turn_end", turn=self.turn, action=action_name, pressure=self.world.pressure, legitimacy=self.world.legitimacy, resources=self.world.resources_global)

        goal_results = evaluate_goals(self.player_goal, self.npc_goals, self.world, self.turn, self._notify)

        if self.turn % 5 == 0:
            self._notify("on_story_beat", self.turn, self.world, goal_results)

        self._log_event("tick", {
            "turn": self.turn,
            "world_tick": self.world.clock.world_tick,
            "action_result": result.model_dump() if result else None,
            "goal_results": goal_results,
        })

        if self.turn % self.snapshot_interval == 0:
            self._save_snapshot(self.world, self.turn)
            self._notify("on_world_state", self.turn, self.world)

    def _generate_world_event(self, event_gen, event_interval, echo):
        if self.turn % event_interval == 0:
            context_for_event = {
                "turn": self.turn,
                "world_tick": self.world.clock.world_tick,
                "resources": self.world.resources,
                "echo_essence": echo.essence if echo else "anarchism",
                "language": get_lang(),
            }
            event = event_gen.generate(context_for_event)
            self._notify("on_event", self.turn, "event", event.title, event.summary)
            self._log_event("event", {
                "title": event.title,
                "summary": event.summary,
                "canonical": event.canonical,
            })

    def _get_player_action(self, echo):
        self._log.debug("get_action", turn=self.turn, stage="input_source")
        action_name = self.input_source.get_action(self.turn, self.world)
        self._log.debug("get_action", turn=self.turn, action_name=action_name)

        if action_name is None and self.autoplay and echo and self.autoplayer_engine:
            self._log.debug("autoplay", turn=self.turn, stage="selecting")
            available_action_names = list(ACTION_CLASSES.keys())
            decision = self.autoplayer_engine.select_action(echo, self.world, available_action_names)
            self._log.debug("autoplay", turn=self.turn, decision=decision.selected_action, scores=decision.scores if hasattr(decision, 'scores') else {})
            self._log_event("autoplay_decision", decision.model_dump())
            action_name = decision.selected_action
            self._notify("on_action_selected", self.turn, None)
        elif action_name:
            self._notify("on_action_selected", self.turn, action_name)

        return action_name

    def _execute_player_action(self, echo, action_name, should_deal_damage_fn):
        from core.application.actions.base import ActionContext

        result = None
        if action_name and action_name in ACTION_CLASSES:
            action = ACTION_CLASSES[action_name]()
            context = ActionContext(
                world_tick=self.world.clock.world_tick,
                action_tick=self.world.clock.action_tick,
                autoplay=(action_name is None),
            )
            if action.can_execute(echo, self.world, context):
                result = action.execute(echo, self.world, context)
                self._log.info("action_executed", turn=self.turn, action=action_name, success=result.success, message=result.message)
                self._notify("on_action_result", self.turn, action_name, result)

                track_echo_action(echo, action_name, self.turn)

                if should_deal_damage_fn(action_name) and result and result.success:
                    try:
                        handle_npc_damage_to_player(action_name, self.world, self._notify, self.turn)
                    except Exception as e:
                        self._log.error("npc_damage", turn=self.turn, action=action_name, stage="error", error=str(e), error_type=type(e).__name__)

        return result

    # ─── Finale ─────────────────────────────────────────────────────────

    def _generate_finale(self) -> dict:
        from core.factories.narrative_generator import NarrativeGenerator

        gen = NarrativeGenerator(seed=self.seed)

        player_progress = self.player_goal.evaluate(self.world, self.turn) if self.player_goal else 0.0
        all_goals = [self.player_goal] + self.npc_goals if self.player_goal else self.npc_goals

        best_npc_progress = max((g.evaluate(self.world, self.turn) for g in self.npc_goals), default=0.0)

        if player_progress >= best_npc_progress:
            winner = "player"
            winner_name = "Tú"
        else:
            winner = "npc"
            winner_name = max(self.npc_goals, key=lambda g: g.evaluate(self.world, self.turn)).owner_name if self.npc_goals else "NPC"

        finale = gen.generate_finale(
            turn=self.turn,
            world=self.world,
            player_goal=self.player_goal,
            all_goals=all_goals,
            winner=winner,
            winner_name=winner_name,
        )

        return {
            "turn": finale.turn,
            "outcome": finale.outcome,
            "outcome_text": finale.outcome_text,
            "story_summary": finale.story_summary,
            "final_stats": finale.final_stats,
            "player_goal_progress": finale.player_goal_progress,
            "player_goal_description": self.player_goal.description if self.player_goal else None,
            "player_goal_bar": self.player_goal.progress_bar(self.world, self.turn) if self.player_goal else "░░░░░",
            "winner": winner,
            "winner_name": winner_name,
            "npc_goal_results": [
                {
                    "name": g.owner_name,
                    "description": g.description,
                    "progress": g.evaluate(self.world, self.turn),
                    "bar": g.progress_bar(self.world, self.turn),
                }
                for g in self.npc_goals
            ],
        }
