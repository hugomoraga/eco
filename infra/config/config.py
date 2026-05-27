from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


def _str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes", "on")


@dataclass
class AIConfig:
    adapter: Literal["mock", "minimax", "openai"] = "mock"
    model: str = "MiniMax-M2.7"
    temperature: float = 0.7
    max_tokens: int = 1024


@dataclass
class SimulationConfig:
    seed: int = 42
    max_turns: int = 100
    snapshot_interval: int = 10


@dataclass
class AutoplayConfig:
    default_mode: Literal["manual", "suggest", "autoplay", "director", "replay"] = "autoplay"
    default_style: Literal[
        "preservationist", "revolutionary", "manipulator", "mystic", "technocrat"
    ] = "preservationist"


@dataclass
class InputConfig:
    mode: Literal["autoplay", "hybrid", "player"] = "player"
    interactive_turns: int = 5


@dataclass
class Config:
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    autoplay: AutoplayConfig = field(default_factory=AutoplayConfig)
    input_config: InputConfig = field(default_factory=InputConfig)
    i18n_language: Literal["es", "en"] = "es"
    verbose: bool = False
    run_dir: Path | None = None

    @classmethod
    def load(cls) -> Config:
        return cls(
            simulation=SimulationConfig(
                seed=int(os.getenv("ECO_SEED", "42")),
                max_turns=int(os.getenv("ECO_MAX_TURNS", "100")),
                snapshot_interval=int(os.getenv("ECO_SNAPSHOT_INTERVAL", "10")),
            ),
            ai=AIConfig(
                adapter=os.getenv("ECO_AI_ADAPTER", "mock"),
                model=os.getenv("ECO_MODEL", "MiniMax-M2.7"),
                temperature=float(os.getenv("ECO_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("ECO_MAX_TOKENS", "1024")),
            ),
            autoplay=AutoplayConfig(
                default_mode=os.getenv("ECO_AUTOPLAY_MODE", "autoplay"),
                default_style=os.getenv("ECO_AUTOPLAY_STYLE", "preservationist"),
            ),
            input_config=InputConfig(
                mode=os.getenv("ECO_INPUT_MODE", "player"),
                interactive_turns=int(os.getenv("ECO_INTERACTIVE_TURNS", "5")),
            ),
            i18n_language=os.getenv("ECO_LANG", "es"),
            verbose=_str_to_bool(os.getenv("ECO_VERBOSE", "false")),
            run_dir=Path(os.getenv("ECO_RUN_DIR")) if os.getenv("ECO_RUN_DIR") else None,
        )


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reset_config() -> None:
    global _config
    _config = None
