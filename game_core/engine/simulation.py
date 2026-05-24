from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from game_core.domain.entities import Echo, EchoAttribute, EchoPhase, World, Circle, Faction
from game_core.engine.random import SeededRandom


class SimulationEngine:
    def __init__(
        self,
        seed: int = 42,
        max_turns: int = 100,
        snapshot_interval: int = 10,
        run_dir: str | None = None,
        autoplay: bool = False,
        autoplay_mode: str = "autoplay",
        autoplay_style: str = "preservationist",
    ):
        self.seed = seed
        self.max_turns = max_turns
        self.snapshot_interval = snapshot_interval
        self.autoplay = autoplay
        self.autoplay_mode = autoplay_mode
        self.autoplay_style = autoplay_style
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

    def _create_run_dir(self) -> Path:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = Path.cwd()
        run_dir = project_root / "game_core" / "runs" / f"run_{run_id}"
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

    def run(self) -> dict:
        from game_core.actions.echo_actions import FoundCircle, PropagateIdea, Talk, WriteManifesto, Sabotage, Ritualize
        from game_core.engine.faction_tick import FactionTickSystem
        from game_core.engine.event_generator import EventGenerator
        from game_core.ai import MockAdapter
        from game_core.domain.npc_generator import NPCGenerator
        from game_core.autoplayer import AutoplayMode, AutoplayerEngine

        action_classes = {
            "found_circle": FoundCircle,
            "propagate_idea": PropagateIdea,
            "talk": Talk,
            "write_manifesto": WriteManifesto,
            "sabotage": Sabotage,
            "ritualize": Ritualize,
        }
        actions = [FoundCircle(), PropagateIdea()]
        faction_system = FactionTickSystem(seed=self.seed)
        faction_tick_interval = 3

        ai_adapter = MockAdapter()
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

        while self.turn < self.max_turns:
            self.turn += 1
            self.world.clock.advance(1)

            result = None
            echo = self.world.get_active_echo()

            if self.autoplay and echo and self.autoplayer_engine:
                available_action_names = list(action_classes.keys())
                decision = self.autoplayer_engine.select_action(echo, self.world, available_action_names)

                self._log_event("autoplay_decision", decision.model_dump())

                if decision.selected_action and decision.selected_action in action_classes:
                    action = action_classes[decision.selected_action]()
                    from game_core.actions.base import ActionContext

                    context = ActionContext(
                        world_tick=self.world.clock.world_tick,
                        action_tick=self.world.clock.action_tick,
                        autoplay=True,
                    )
                    if action.can_execute(echo, self.world, context):
                        result = action.execute(echo, self.world, context)

            if self.turn % faction_tick_interval == 0 and self.world.factions:
                faction_results = faction_system.tick(self.world)
                for fr in faction_results:
                    self._log_event("faction_tick", fr)

            if self.turn % event_interval == 0:
                context_for_event = {
                    "turn": self.turn,
                    "world_tick": self.world.clock.world_tick,
                    "resources": self.world.resources,
                    "echo_essence": self.world.get_active_echo().essence if self.world.get_active_echo() else "anarchism",
                }
                event = event_gen.generate(context_for_event)
                self._log_event("event", {
                    "title": event.title,
                    "summary": event.summary,
                    "canonical": event.canonical,
                })

            for circle in self.world.circles:
                if circle.members >= 3:
                    if len(getattr(circle, 'npcs', [])) < circle.members:
                        npc = npc_gen.generate({"essence": circle.essence, "context": "circle_growth"})
                        if not hasattr(circle, 'npcs'):
                            circle.npcs = []
                        circle.npcs.append(npc.id)
                        self._log_event("npc_created", {
                            "npc_id": npc.id,
                            "npc_name": npc.name,
                            "circle_id": circle.id,
                        })

            self._log_event(
                "tick",
                {
                    "turn": self.turn,
                    "world_tick": self.world.clock.world_tick,
                    "action_result": result.model_dump() if result else None,
                },
            )

            if self.turn % self.snapshot_interval == 0:
                self._save_snapshot(self.world, self.turn)

            print(
                f"[Turn {self.turn:4d}] WT={self.world.clock.world_tick} "
                f"Echoes={len(self.world.echoes)} Circles={len(self.world.circles)} "
                f"Factions={len(self.world.factions)}"
            )

        return {"turns": self.turn, "run_dir": str(self.run_dir)}