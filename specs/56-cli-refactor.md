# 56-cli-refactor.md

## Status: Draft

## Problem

`adapters/cli/main.py` tiene varios problemas de diseño:

1. **Mixed concerns**: `main()` hace parsing de args, config loading, player creation, engine creation, display setup, y execution todo en un lugar
2. **Sin factory pattern**: Player creation usa if/elif/else que no escala
3. **Magic numbers**: `args.turns or 100` hardcodeado
4. **Tight coupling**: TUI branch hace import directo y corre sin pasar por el sistema de config
5. **Display creation es confusa**: La lógica de ConsoleDisplay está esparcida
6. **Patrón de override repetido**: `args.X if args.X is not None else cfg.X` se repite 7 veces

## Goals

1. **Separar concerns**: Argument parsing → Config resolution → Object creation → Launch
2. **Factory pattern para Players**: `PlayerFactory.create(config)` que retorn el player correcto
3. **Config bundle**: Dataclass `GameConfig` que bundla todos los settings
4. **Registry pattern para modos**: TUI, CLI, headless como LaunchMode handlers
5. **DRY config override**: Un solo lugar para el patrón "arg override config"

## Proposed Architecture

### 1. GameConfig Dataclass

```python
@dataclass
class GameConfig:
    seed: int
    max_turns: int
    player: Player
    ai_adapter_type: str
    run_dir: Path
    civ_id: str
    verbose: bool
    headless: bool
    display_mode: Literal["console", "layout", "tui"]

    @classmethod
    def from_args(cls, args, cfg) -> "GameConfig":
        # Una sola vez, el patrón args override config
        seed = args.seed if args.seed is not None else cfg.simulation.seed
        # ...
```

### 2. PlayerFactory

```python
class PlayerFactory:
    @staticmethod
    def create(config: GameConfig) -> Player | None:
        if config.headless:
            return None
        if config.display_mode == "tui":
            return HumanPlayer()
        if config.autoplay:
            return AutoPlayer(seed=config.seed, mode=config.autoplay_mode, style_id=config.autoplay_style)
        return HumanPlayer()
```

### 3. Launcher Pattern

```python
class Launcher:
    def launch_tui(self, config: GameConfig):
        from adapters.tui.textual.app import EcoTextualApp
        EcoTextualApp(max_turns=config.max_turns, seed=config.seed).run()

    def launch_cli(self, config: GameConfig):
        engine = SimulationEngine(seed=config.seed, ...)
        if not config.headless:
            display = DisplayFactory.create(config)
            engine.register_observer(display)
        engine.run()
```

## Refactoring Steps

1. Extraer `GameConfig.from_args()` con el patrón de override
2. Crear `PlayerFactory.create()`
3. Crear `DisplayFactory.create()` para ConsoleDisplay/TerminalLayout
4. Crear `Launcher.launch_tui()` y `Launcher.launch_cli()`
5. Simplificar `main()` a solo orquestación

## Files Affected

- `adapters/cli/main.py` - refactor completo
- Puede necesitar nuevos archivos en `adapters/cli/`:
  - `config.py` (o mover de `adapters/config/`)
  - `launcher.py`
  - `player_factory.py`
  - `display_factory.py`
