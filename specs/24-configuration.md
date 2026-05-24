# 24 - Configuration System

## Metadata

- Status: draft
- Created: 2026-05-24
- Priority: high
- Depends on: 01 (Architecture)

## Context

Currently configuration is scattered:
- API keys via `os.environ.get()` (no .env loading)
- Language via `os.getenv("ECO_LANG")`
- No central config file
- Adapters read env vars directly

We need a unified configuration system.

## Proposal

### 1. Environment Variables (always supported)

```bash
# API Keys
MINIMAX_API_KEY=          # MiniMax API key
OPENAI_API_KEY=           # OpenAI API key

# Language
ECO_LANG=es               # es (default) | en

# Simulation
ECO_SEED=42              # Default seed
ECO_MAX_TURNS=100         # Default max turns
ECO_AUTOPLAY=false        # true | false

# Output
ECO_RUN_DIR=              # Custom run directory (optional)
ECO_VERBOSE=false         # Debug output

# AI Adapter Selection
ECO_AI_ADAPTER=mock       # mock | minimax | openai
```

### 2. .env File (development)

```bash
# API Keys
MINIMAX_API_KEY=tu-key-de-minimax
OPENAI_API_KEY=tu-key-de-openai

# Language
ECO_LANG=es

# Simulation defaults
ECO_SEED=42
ECO_MAX_TURNS=100
ECO_AUTOPLAY=false
ECO_VERBOSE=false
ECO_AI_ADAPTER=mock
```

### 3. Config File (production) - `config.yaml`

```yaml
# config.yaml - production settings
simulation:
  seed: 42
  max_turns: 100
  autoplay: false
  snapshot_interval: 10

ai:
  adapter: mock  # mock | minimax | openai
  model: "MiniMax-M2.7"
  temperature: 0.7
  max_tokens: 1024

minimax:
  api_key: "${MINIMAX_API_KEY}"  # Reference env var
  base_url: "https://api.minimax.io/anthropic/v1"

openai:
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-4"

output:
  run_dir: null  # null = auto-generate
  verbose: false

i18n:
  language: es

autoplay:
  default_mode: autoplay
  default_style: preservationist
```

### 4. Priority Order

```
CLI args (highest priority)
  ↓
config.yaml
  ↓
.env file
  ↓
Environment variables
  ↓
Hardcoded defaults (lowest priority)
```

### 5. Config Module

```python
# game_core/config.py
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal

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
    autoplay: bool = False
    snapshot_interval: int = 10

@dataclass
class Config:
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    i18n_language: Literal["es", "en"] = "es"
    verbose: bool = False
    run_dir: Path | None = None

def load_config() -> Config:
    """Load config with priority: CLI > config.yaml > .env > defaults"""
    # Load .env if exists
    _load_dotenv_if_exists()

    # Parse config.yaml if exists
    yaml_config = _load_yaml_config()

    # Build Config object
    return Config(
        simulation=SimulationConfig(
            seed=int(os.getenv("ECO_SEED", 42)),
            max_turns=int(os.getenv("ECO_MAX_TURNS", 100)),
            autoplay=_str_to_bool(os.getenv("ECO_AUTOPLAY", "false")),
            snapshot_interval=yaml_config.get("simulation", {}).get("snapshot_interval", 10),
        ),
        ai=AIConfig(
            adapter=os.getenv("ECO_AI_ADAPTER", yaml_config.get("ai", {}).get("adapter", "mock")),
            model=os.getenv("ECO_MODEL", yaml_config.get("ai", {}).get("model", "MiniMax-M2.7")),
            temperature=float(os.getenv("ECO_TEMPERATURE", yaml_config.get("ai", {}).get("temperature", 0.7))),
            max_tokens=int(os.getenv("ECO_MAX_TOKENS", yaml_config.get("ai", {}).get("max_tokens", 1024))),
        ),
        i18n_language=os.getenv("ECO_LANG", yaml_config.get("i18n", {}).get("language", "es")),
        verbose=_str_to_bool(os.getenv("ECO_VERBOSE", "false")),
        run_dir=Path(os.getenv("ECO_RUN_DIR")) if os.getenv("ECO_RUN_DIR") else None,
    )
```

### 6. Configuration Options to Consider

#### API Keys
| Variable | Description | Required |
|----------|-------------|----------|
| `MINIMAX_API_KEY` | MiniMax API key | For MiniMax adapter |
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI adapter |

#### Simulation
| Variable | Default | Description |
|----------|---------|-------------|
| `ECO_SEED` | 42 | Random seed |
| `ECO_MAX_TURNS` | 100 | Max simulation turns |
| `ECO_AUTOPLAY` | false | Enable autoplay by default |
| `ECO_SNAPSHOT_INTERVAL` | 10 | Turns between snapshots |

#### Language
| Variable | Default | Description |
|----------|---------|-------------|
| `ECO_LANG` | es | es (Spanish) or en (English) |

#### AI
| Variable | Default | Description |
|----------|---------|-------------|
| `ECO_AI_ADAPTER` | mock | mock, minimax, openai |
| `ECO_MODEL` | MiniMax-M2.7 | Model name |
| `ECO_TEMPERATURE` | 0.7 | LLM temperature (0-2) |
| `ECO_MAX_TOKENS` | 1024 | Max response tokens |

#### Output
| Variable | Default | Description |
|----------|---------|-------------|
| `ECO_VERBOSE` | false | Debug output |
| `ECO_RUN_DIR` | auto | Custom run directory |
| `ECO_LOG_LEVEL` | INFO | DEBUG, INFO, WARNING, ERROR |

#### Autoplay Defaults
| Variable | Default | Description |
|----------|---------|-------------|
| `ECO_AUTOPLAY_MODE` | autoplay | manual, suggest, autoplay, director, replay |
| `ECO_AUTOPLAY_STYLE` | preservationist | preservationist, revolutionary, manipulator, mystic, technocrat |

#### Future Options (consider now)
| Variable | Description |
|----------|-------------|
| `ECO_THEME` | UI theme (dark/light) |
| `ECO_TTS_ENABLED` | Text-to-speech for events |
| `ECO_TTS_VOICE` | Voice ID for TTS |
| `ECO_SAVE_INTERVAL` | Auto-save every N turns |
| `ECO_MAX_RUNS` | Max saved runs before cleanup |
| `ECO_AI_CACHE` | Cache AI responses (true/false) |
| `ECO_NETWORK_PROXY` | Proxy for API calls |
| `ECO_RATE_LIMIT_DELAY` | Delay between API calls (ms) |

### 7. Files to Create

```
game_core/
├── config.py              # Config loader + dataclasses
├── config.yaml           # Example config (optional, gitignored)
├── .env.example          # Template for .env (committed)
└── .env                  # Local config (gitignored)
```

### 8. Files to Modify

- `game_core/run.py` - Use Config from config.py instead of argparse defaults
- `game_core/engine/simulation.py` - Use Config for adapter selection
- `game_core/ai/adapters/*.py` - Remove direct os.environ calls, use Config

### 9. Implementation Order

1. Create `game_core/config.py` with dataclasses
2. Add `load_dotenv()` to load .env
3. Add `.env.example` file
4. Update `run.py` to use Config
5. Update adapters to read from Config
6. Add `config.yaml` support (optional Phase 2)

## Status History

- 2026-05-24: draft created