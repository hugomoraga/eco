# 54 - Adapter Core Architecture

**Estado:** implemented
**Fecha:** 2026-05-26
**Actualizado:** 2026-05-26

---

## Arquitectura Implementada

### Hexagonal Architecture

```
eco/
├── core/                    # Lógica pura (sin dependencias externas)
│   ├── ports/              # Interfaces
│   │   └── logger.py      # Logger port
│   ├── domain/            # Entidades (World, Echo, Circle, etc)
│   ├── application/        # Casos de uso
│   │   ├── processors/     # SimulationEngine, EventGenerator
│   │   ├── players/        # HumanPlayer, AutoPlayer
│   │   └── actions/        # Acciones del juego
│   └── factories/          # Factory methods
│
├── infra/                   # Driven adapters (responden a core)
│   ├── ai/                # AI adapters
│   │   ├── base.py        # AIAdapter, GameAdapter, MockAdapter
│   │   ├── ai.py          # AIGameAdapter
│   │   ├── human.py       # HumanGameAdapter
│   │   ├── minimax_adapter.py
│   │   └── openai_adapter.py
│   ├── config/            # Configuración
│   │   ├── config.py      # Config dataclass, get_config()
│   │   └── tuning.py     # Tuning constants
│   └── logging/           # Logging
│       └── main.py        # structlog implementation
│
└── adapters/               # Driving adapters (inician acciones)
    ├── cli/               # CLI launcher
    ├── tui/               # Textual TUI
    ├── player_input/      # Input sources
    │   ├── base.py        # InputSource ABC
    │   ├── player.py      # PlayerInputSource
    │   ├── autoplay.py    # AutoplayInputSource
    │   ├── hybrid.py      # HybridInputSource
    │   └── factory.py     # create_input_source()
    ├── autoplayer/        # Autoplay engine
    ├── data_loader/        # Data loading
    └── i18n/              # Internacionalización
```

## Puertos (Interfaces)

### Logger Port

```python
# core/ports/logger.py
class Logger(Protocol):
    def debug(self, msg: str, **kwargs) -> None: ...
    def info(self, msg: str, **kwargs) -> None: ...
    def warning(self, msg: str, **kwargs) -> None: ...
    def error(self, msg: str, **kwargs) -> None: ...
    def exception(self, msg: str, **kwargs) -> None: ...
```

### Player Port

```python
# core/ports/player.py
class Player(ABC):
    @abstractmethod
    def select_action(self, turn: int, world, available_actions: list[str]) -> str | None: ...
```

### InputSource (adapters/player_input/base.py)

```python
class InputSource(ABC):
    @abstractmethod
    def get_action(self, turn: int, world: World) -> str | None: ...
    @property
    @abstractmethod
    def mode(self) -> str: ...  # 'autoplay' | 'hybrid' | 'player'
```

## Flujo de Datos

```
User (CLI/TUI)
    │
    ▼
adapters/cli/launcher.py
    │
    ▼
SimulationEngine (core/application/processors/)
    │
    ├──► World (core/domain/)
    │
    ├──► Player (HumanPlayer/AutoPlayer)
    │        │
    │        └──► PlayerInputSource/AutoplayInputSource (adapters/player_input/)
    │
    ├──► AI Adapter (infra/ai/)
    │        │
    │        └──► MiniMaxAdapter / OpenAIAdapter (calls external API)
    │
    └──► Observers (ConsoleDisplay, TUI)
             │
             └──► infra/logging/ (stderr + debug.log)
```

## Implementaciones

| Componente | Ubicación | Rol |
|-----------|----------|-----|
| `HumanPlayer` | `core/application/players/` | Player para humanos |
| `AutoPlayer` | `core/application/players/` | Player automático |
| `PlayerInputSource` | `adapters/player_input/` | Input para humanos |
| `AutoplayInputSource` | `adapters/player_input/` | Siempre retorna None |
| `HybridInputSource` | `adapters/player_input/` | Mixto humano/autoplay |
| `AIGameAdapter` | `infra/ai/` | Adapter para autoplay |
| `HumanGameAdapter` | `infra/ai/` | Adapter para humanos |
| `SimulationEngine` | `core/application/processors/` | Motor de simulación |
| `ConsoleDisplay` | `adapters/tui/` | Display observer |

## Reglas de Arquitectura

1. **core/ NO importa de infra/ ni adapters/**
2. **infra/ implementa puertos (interfaces en core/ports/)**
3. **adapters/ inicia acciones (driving adapters)**
4. **Logging**: `core/utils/logger` → `infra/logging/`

## Estado

- [x] Arquitectura diseñada e implementada
- [x] core/utils/logger shim para hexagonal
- [x] infra/logging con structlog
- [x] infra/ai con adapters de AI
- [x] infra/config para configuración
- [x] adapters/player_input para input de jugadores
- [x] Tests pasando (188)
