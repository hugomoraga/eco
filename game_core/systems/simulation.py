"""
SimulationEngine — headless core simulation.
Notifies observers on events. Knows nothing about display or input rendering.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from game_core.domain.entities import World, PlayerPerson
from game_core.factory import process_circle_tick
from game_core.i18n import get_lang
from game_core.systems.damage import calculate_damage, can_deal_damage, should_deal_damage_to_player, apply_damage_to_npc
from game_core.systems.reincarnation import is_in_transition, start_transition_turn, end_transition_turn, preserve_echo_legacy, transform_legacy, reincarnate_echo
from game_core.systems.observer import NullObserver, SimulationObserver
from game_core.systems.random import SeededRandom
from game_core.utils.logger import get_logger, init_logger


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
        input_source: InputSource | None = None,
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
        self.world = self._create_initial_world()
        self.autoplayer_engine = None

        init_logger(self.run_dir)
        self._log = get_logger(__name__)

        self._observers: list[SimulationObserver] = [NullObserver()]

        if input_source is not None:
            self.input_source = input_source
        else:
            from player_core import create_input_source
            self.input_source = create_input_source(autoplay=self.autoplay)

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

    # ─── World setup ─────────────────────────────────────────────────────

    def _create_run_dir(self) -> Path:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = Path(__file__).parent.parent.parent
        run_dir = project_root / "runs" / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _create_initial_world(self) -> World:
        from game_core.factory import (
            create_echo, create_faction, create_ideas_for_essence,
            create_all_civs, create_civ,
        )
        from game_core.systems.random import SeededRandom
        from game_core.data.person_dataset import load_person_dataset

        rng = SeededRandom.get_instance(self.seed)

        # ─── 1. Load Civ (spec-47) via factory
        all_civs = create_all_civs(civs_dir="data/civs")
        selected_civ = create_civ(self.civ_id, civs_dir="data/civs")
        if selected_civ is None:
            selected_civ = all_civs[0] if all_civs else None

        # ─── 2. Load Persons from archetype dataset
        all_persons = load_person_dataset(persons_dir="data/world/persons")
        if selected_civ:
            for p in all_persons:
                p.civ_id = selected_civ.id

        # ─── 3. Create Echo for the player (using host data from civ if available)
        echo_essence = "anarchism"
        echo_name = "First Echo"
        if selected_civ and selected_civ.meta_id == "technocracy":
            echo_essence = "technocracy"
            echo_name = "Data Walker"
        elif selected_civ and selected_civ.meta_id == "theocracy":
            echo_essence = "monoteism"
            echo_name = "The Anointed"
        elif selected_civ and selected_civ.meta_id == "anarchist_utopia":
            echo_essence = "anarchism"
            echo_name = "Free Spirit"

        echo = create_echo(
            name=echo_name,
            essence=echo_essence,
            seed=self.seed,
        )
        echo.known_tags = create_ideas_for_essence(rng, echo_essence, count=3)
        echo.genealogical_lineage = [echo.essence]

        # ─── 4. Create faction
        faction = create_faction(
            name="Circulo Libertario",
            essence=echo.essence,
            ideas=echo.ideas,
            members=5,
            influence=10.0,
            resources={"food": 50, "infrastructure": 30, "energy": 20},
            goals=["expand_influence", "spread_idea"],
        )

        # ─── 5. Build world with Civ metrics
        world = World(
            echoes=[echo],
            factions=[faction],
            active_echo_id=echo.id,
            civs=all_civs,
            population=selected_civ.population if selected_civ else 10000,
            stability=selected_civ.stability if selected_civ else 50.0,
            pressure=selected_civ.pressure if selected_civ else 30.0,
            legitimacy=selected_civ.legitimacy if selected_civ else 60.0,
            resources_global=selected_civ.resources_global if selected_civ else 70.0,
            crisis_threshold=selected_civ.crisis_threshold if selected_civ else 75.0,
            collapse_threshold=selected_civ.collapse_threshold if selected_civ else 15.0,
            resources=selected_civ.resources if selected_civ else {
                "food": 80, "infrastructure": 60, "energy": 50, "knowledge": 50, "legitimacy": 60,
            },
        )

        # ─── 6. Create player Person
        from game_core.factory import create_player_person_for_echo

        player_person = create_player_person_for_echo(world, echo)
        if player_person and selected_civ:
            player_person.civ_id = selected_civ.id

        # ─── 7. Add archetype persons to world
        for p in all_persons[:20]:
            world.persons.append(p)

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
        from game_core.actions.social_actions import (
            Negotiate,
            PropagateIdea,
            RecruitFollower,
            Ritual,
            Ritualize,
            Sabotage,
            SpreadRumor,
            Talk,
        )

        # AI adapter
        from game_core.ai import MiniMaxAdapter, MockAdapter, OpenAIAdapter
        from game_core.autoplayer import AutoplayerEngine, AutoplayMode
        from game_core.factory import create_npc
        from game_core.systems.event_generator import EventGenerator
        from game_core.systems.event_pool import EventPool
        from game_core.systems.faction_tick import FactionTickSystem
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
            "write_manifesto": WriteManifesto,
            "sabotage": Sabotage,
            "ritualize": Ritualize,
            "talk": Talk,
            "spread_rumor": SpreadRumor,
            "recruit_follower": RecruitFollower,
            "negotiate": Negotiate,
            "ritual": Ritual,
        }

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

        # Initial world state snapshot
        self._notify("on_world_state", 0, self.world)

        # World start screen — show Civ, Host, Persons, Turn System
        self._notify("on_world_start", self.world)

        while self.turn < self.max_turns:
            self.turn += 1
            self._log.info("turn_start", turn=self.turn, pressure=self.world.pressure, legitimacy=self.world.legitimacy, resources=self.world.resources_global)

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
                    "language": get_lang(),
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
            self._log.debug("get_action", turn=self.turn, stage="input_source")
            action_name = self.input_source.get_action(self.turn, self.world)
            self._log.debug("get_action", turn=self.turn, action_name=action_name)

            # Autoplay if needed
            if action_name is None and self.autoplay and echo and self.autoplayer_engine:
                self._log.debug("autoplay", turn=self.turn, stage="selecting")
                available_action_names = list(action_classes.keys())
                decision = self.autoplayer_engine.select_action(echo, self.world, available_action_names)
                self._log.debug("autoplay", turn=self.turn, decision=decision.selected_action, scores=decision.scores if hasattr(decision, 'scores') else {})
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
                    self._log.info("action_executed", turn=self.turn, action=action_name, success=result.success, message=result.message)

                    # Track action history (guard against no echo)
                    if echo:
                        if hasattr(echo, 'action_history'):
                            echo.action_history.append(action_name)
                            if len(echo.action_history) > 10:
                                echo.action_history = echo.action_history[-10:]
                        if hasattr(echo, 'last_action_turn'):
                            echo.last_action_turn[action_name] = self.turn

                    # Handle damage to player from NPC actions
                    if should_deal_damage_to_player(action_name) and result and result.success:
                        self._log.debug("npc_damage", turn=self.turn, action=action_name, stage="handling")
                        _handle_npc_damage_to_player(action_name, self.world, self._notify, self.turn)
                        self._log.debug("npc_damage", turn=self.turn, stage="completed")

            # Check transition turn - player cannot act during transition
            if is_in_transition(self.world):
                if self.world.transition_turn <= self.world.clock.action_tick:
                    _handle_reincarnation(self.world, self._notify, self.turn)
                    end_transition_turn(self.world)

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
                        self._log.debug("npc_creation", turn=self.turn, circle=circle.name, essence=circle.essence)
                        npc = create_npc(ai_adapter, {"essence": circle.essence, "context": "circle_growth"}, seed=self.seed)
                        self._log.info("npc_created", turn=self.turn, circle=circle.name, npc_name=npc.name, npc_id=npc.id)
                        if not hasattr(circle, 'npcs'):
                            circle.npcs = []
                        circle.npcs.append(npc.id)
                        # Also register in world.persons (new path)
                        if not hasattr(self.world, 'persons'):
                            self.world.persons = []
                        if npc not in self.world.persons:
                            self.world.persons.append(npc)
                        self._notify("on_npc_created", self.turn, npc.name, npc.role)
                        self._log_event("npc_created", {
                            "npc_id": npc.id,
                            "npc_name": npc.name,
                            "circle_id": circle.id,
                        })

            # World metric evolution
            self.world.evolve_metrics(self.rng)
            new_metrics = self._snapshot_metrics()

            # Notify metric changes
            for metric, new_val in new_metrics.items():
                old_val = old_metrics.get(metric, new_val)
                if abs(new_val - old_val) >= 0.5:
                    self._notify("on_metric_changed", self.turn, metric, old_val, new_val)

            # Notify turn end
            self._notify("on_turn_end", self.turn, self.world, action_name)
            self._log.info("turn_end", turn=self.turn, action=action_name, pressure=self.world.pressure, legitimacy=self.world.legitimacy, resources=self.world.resources_global)

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


    def _handle_npc_damage_to_player(action_name: str, world: World, notify, turn: int) -> None:
        """Handle NPC actions that can damage the player (sabotage, spread_rumor)."""
        log = get_logger(__name__)
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
                _trigger_player_death(world, person, notify, turn)


    def _trigger_player_death(world: World, player_person: PlayerPerson, notify, turn: int) -> None:
        """Trigger player death and start reincarnation process."""
        log = get_logger(__name__)
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


    def _handle_reincarnation(world: World, notify, turn: int) -> None:
        """Handle the end of transition turn and complete reincarnation."""
        log = get_logger(__name__)
        log.debug("reincarnation", stage="handling_end_of_transition", turn=turn)

        person = world.get_active_player_person()
        if not person:
            log.warning("reincarnation", stage="end_transition", error="no_active_player_person", turn=turn)
            return

        log.info("reincarnation_complete", person=person.name, turn=turn)
        notify("on_reincarnation_complete", turn, person.name)


    def _snapshot_metrics(self) -> dict:
            """Capture current world metrics."""
            return {
                "pressure": self.world.pressure,
                "legitimacy": self.world.legitimacy,
                "resources_global": self.world.resources_global,
            }
