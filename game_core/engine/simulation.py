from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from game_core.domain.entities import Echo, EchoAttribute, EchoPhase, World
from game_core.engine.random import SeededRandom


class SimulationEngine:
    def __init__(
        self,
        seed: int = 42,
        max_turns: int = 100,
        snapshot_interval: int = 10,
        run_dir: str | None = None,
        autoplay: bool = False,
    ):
        self.seed = seed
        self.max_turns = max_turns
        self.snapshot_interval = snapshot_interval
        self.autoplay = autoplay
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

    def _create_run_dir(self) -> Path:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = Path.cwd()
        run_dir = project_root / "game_core" / "runs" / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _create_initial_world(self) -> World:
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
        world = World(
            echoes=[echo],
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
        from game_core.actions.echo_actions import FoundCircle, PropagateIdea

        actions = [FoundCircle(), PropagateIdea()]

        while self.turn < self.max_turns:
            self.turn += 1
            self.world.clock.advance(1)

            result = None
            if self.autoplay:
                action = self.rng.choice(actions)
                echo = self.world.get_active_echo()
                if echo:
                    from game_core.actions.base import ActionContext

                    context = ActionContext(
                        world_tick=self.world.clock.world_tick,
                        action_tick=self.world.clock.action_tick,
                        autoplay=True,
                    )
                    if action.can_execute(echo, self.world, context):
                        result = action.execute(echo, self.world, context)

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