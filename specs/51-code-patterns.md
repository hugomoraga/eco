# 51 - Code Patterns & Conventions

Estandarización de patrones de código para `game_core/factory/` y `game_core/systems/`.

**Status**: draft
**Created**: 2026-05-26
**Depends on**: 01-architecture.md

---

## 1. Motivation

Al crecer el codebase, los patrones se volvieron inconsistentes:

| Problema | Ejemplo |
|----------|---------|
| `factory/` mezcla creación + lifecycle | `circle.py` tiene `process_circle_tick()` |
| `systems/` tiene clases y funciones sueltas | `damage.py` (funciones) vs `faction_tick.py` (clase) |
| Naming inconsistente | `create_npcs()` vs `create_all_civs()` |
| Módulos con responsabilidad mixta | `host.py` = creación + linking + muerte |

Este spec define reglas claras para evitar estas inconsistencias.

---

## 2. Principios

1. **Single Responsibility**: Cada módulo tiene una responsabilidad clara
2. **Consistency over cleverness**: Patrones predecibles > código elegante
3. **Factory = creación pura**: Sin lógica de negocio en factories
4. **Systems = lógica de negocio**: Donde vive el estado y las reglas
5. **Naming paralelo**: Archivo `snake_case.py` → Clase `PascalCase` cuando aplique

---

## 3. FACTORY — Patrones de Creación

### 3.1 Estructura de archivos

```
game_core/factory/
├── __init__.py           # Exports centralizados
├── echo.py               # Creación de Echo
├── circle.py             # Creación de Circle
├── faction.py            # Creación de Faction
├── civ.py               # Cargar civilizations desde YAML
├── host.py              # Vinculación Person↔Echo, reencarnación
├── tags.py              # Creación de Ideas/Tags
├── npc.py               # NPC (deprecated, usar echo.py)
└── types.py             # Tipos compartidos, enum definitions
```

**Regla**: Un módulo factory = un tipo de entidad. No mezclar.

### 3.2 Naming de funciones

| Operación | Naming | Ejemplo |
|-----------|--------|---------|
| Crear uno | `create_<entity>` | `create_echo()`, `create_circle()` |
| Crear varios | `create_<entities>` | `create_echoes()`, `create_circles()` |
| Cargar desde YAML | `load_<entities>` | `load_civs()`, `load_npcs()` |
| Helper interno | `_build_<thing>` | `_build_attribute()`, `_make_idea()` |

### 3.3 Estructura de función create_X

```python
def create_X(
    world: World,
    *,
    required_param: Type,
    optional_param: Type = default,
) -> X:
    """Crear una instancia de X y registrarla en world.

    Args:
        world: World destino
        required_param: Descripción
        optional_param: Descripción (default: default)

    Returns:
        Instancia creada de X

    Raises:
        ValueError: Cuando required_param es inválido
    """
    # 1. Validar parámetros
    if not required_param:
        raise ValueError("...")

    # 2. Crear instancia (Pydantic validation automática)
    entity = X(
        field=required_param,
        other=optional_param,
    )

    # 3. Registrar en world si aplica
    world.entities.append(entity.id)

    return entity
```

### 3.4 REGLA: Sin Lifecycle en Factory

`factory/` SOLO crea entidades. NO incluye:
- Lógica de `tick()`
- Actualización de estado
- Interacciones entre entidades

**Excepción**: Validación de negocio al momento de creación (ej: verificar nombre único).

### 3.5 Exports en __init__.py

```python
# game_core/factory/__init__.py
from game_core.factory.echo import create_echo, create_echoes
from game_core.factory.circle import create_circle, create_circle_name
from game_core.factory.faction import create_faction, create_factions
from game_core.factory.civ import load_civs
# ...

__all__ = [
    "create_echo",
    "create_echoes",
    "create_circle",
    "create_faction",
    "load_civs",
    # ...
]
```

---

## 4. SYSTEMS — Patrones de Lógica de Negocio

### 4.1 Estructura de archivos

```
game_core/systems/
├── __init__.py           # Exports centralizados
├── simulation.py         # SimulationEngine (orquestador)
├── event_pool.py         # EventPool (datos de eventos)
├── event_generator.py    # Generador de eventos
├── faction_tick.py       # FactionTickSystem
├── pressure.py           # Calculadoras de presión
├── narrative_engine.py   # Motor narrativo
├── observer.py           # SimulationObserver ABC
├── random.py             # SeededRandom (singleton)
├── damage.py             # Lógica de daño (REVISAR)
├── reincarnation.py      # Lógica de reencarnación (REVISAR)
└── types.py              # Tipos de sistemas
```

**Regla**: Si un módulo tiene lógica de tick/update/calculate/evaluate, es un sistema.

### 4.2 Sistema base

```python
class BaseSystem(ABC):
    """Clase base para todos los sistemas.

    Pattern a seguir para sistemas complejos.
    """

    def __init__(self, config: SystemConfig | None = None):
        self.config = config or self._default_config()
        self._initialized = False

    @abstractmethod
    def tick(self, context: dict) -> SystemResult:
        """Ejecutar un tick del sistema.

        Args:
            context: Contexto compartido (world, turn, etc.)

        Returns:
            SystemResult con cambios aplicados
        """
        pass

    def _ensure_initialized(self) -> None:
        """Lazy initialization."""
        if not self._initialized:
            self._setup()
            self._initialized = True

    @abstractmethod
    def _setup(self) -> None:
        """Inicialización diferida. Override si necesitas setup delayed."""
        pass

    def _default_config(self) -> dict:
        """Override para config por defecto."""
        return {}
```

### 4.3 Sistemas simples: funciones puras

Para lógica sin estado (ej: cálculos, transformaciones de datos):

```python
# game_core/systems/damage.py
from dataclasses import dataclass

@dataclass
class DamageResult:
    damage: float
    target_id: str
    source: str

def calculate_damage(attacker_power: float, defender_resistance: float) -> float:
    """Calcular daño basado en poder y resistencia."""
    return max(0, attacker_power - defender_resistance * 0.5)

def apply_damage(target: Echo, damage: float) -> DamageResult:
    """Aplicar daño a un Echo."""
    # lógica
    return DamageResult(damage=damage, target_id=target.id, source="...")
```

**Regla**: Usar funciones puras cuando NO haya estado mutable.

### 4.4 Sistemas con estado: clases

```python
class EventGenerator:
    """Generador de eventos con pool de YAML.

    Responsibilities:
    - Cargar eventos desde YAML
    - Seleccionar evento según estado mundial
    - Enriquecer con IA si disponible
    """

    def __init__(
        self,
        pool: EventPool | None = None,
        adapter: AIAdapter | None = None,
        seed: int = 42,
    ):
        self.pool = pool
        self.adapter = adapter
        self.rng = SeededRandom.get_instance(seed)

    def generate(self, context: dict) -> GameEvent:
        """Generar evento basado en contexto."""
        # lógica
        pass

    def _select_from_pool(self, context: dict) -> GameEvent:
        """Selección por weights del pool."""
        pass
```

### 4.5 Exports en __init__.py

```python
# game_core/systems/__init__.py
from game_core.systems.simulation import SimulationEngine
from game_core.systems.event_generator import EventGenerator
from game_core.systems.event_pool import EventPool
# ...

__all__ = [
    "SimulationEngine",
    "EventGenerator",
    "EventPool",
    #	funciones públicas si aplican
    "calculate_damage",
]
```

---

## 5. Naming Conventions

### 5.1 Archivos

| Tipo | Pattern | Ejemplo |
|------|---------|---------|
| Módulo | `snake_case.py` | `event_generator.py` |
| Clase | `PascalCase` | `class EventGenerator:` |
| Función | `snake_case` | `def generate_event()` |
| Constante | `UPPER_SNAKE` | `MAX_TURNS = 1000` |
| Variable | `snake_case` | `event_pool` |

### 5.2 Funciones de fábrica

| Pattern | Correcto | Incorrecto |
|---------|----------|------------|
| Crear uno | `create_circle()` | `found_circle()`, `make_circle()` |
| Crear batch | `create_circles()` | `create_all_circles()`, `spawn_circles()` |
| Cargar de YAML | `load_civs()` | `get_civs_from_yaml()` |
| Generar nombre | `generate_circle_name()` | `make_random_circle_name()` |

### 5.3 Métodos de sistemas

| Pattern | Uso |
|---------|-----|
| `tick()` | Ejecución principal de turno |
| `calculate()` | Cálculos sinmutación |
| `evaluate()` | Decisiones, scoring |
| `generate()` | Creación de entidades/datos |
| `update()` | Mutación de estado |

---

## 6. Lifecycle —Dónde vive cada cosa

```
┌─────────────────────────────────────────────────────────────┐
│ FACTORY (creación pura)                                      │
│   - create_echo() → nueva entidad                          │
│   - create_circle() → validar, registrar en world           │
│   - NO modifica estado de otras entidades                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ SIMULATION (orquestación)                                   │
│   - SimulationEngine.tick()                                │
│   - Llama a cada sistema en orden                          │
│   - Notifica observers                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ SYSTEMS (lógica de negocio con estado)                       │
│   - FactionTickSystem.tick(world) → actualiza factions      │
│   - EventGenerator.generate(context) → nuevo evento         │
│   - PressureCalculator.calculate(world) → valores            │
└─────────────────────────────────────────────────────────────┘
```

**REGLA**: Lifecycle (tick/update) vive en SYSTEMS, no en FACTORY.

---

## 7. Issues Pendientes de Resolver

| Issue | Ubicación actual | Solución propuesta |
|-------|-----------------|-------------------|
| `process_circle_tick()` en factory | `factory/circle.py:262` | Mover a `systems/circle_tick.py` |
| `host.py` mezcla 3 responsabilidades | `factory/host.py` | Split en `link.py` + `reincarnation.py` |
| `damage.py` y `reincarnation.py` son sueltos | `systems/` | Crear `systems/types.py` si son tipos, o mover a clases apropiadas |
| `load_civs()` en `civ.py` | `factory/civ.py` | OK, es creación |

---

## 8. Refactor Checklist

- [ ] `factory/circle.py`: Extraer `process_circle_tick()` → `systems/circle_tick.py`
- [ ] `factory/host.py`: Split en `link.py` + mantener `reincarnation.py`
- [ ] `systems/__init__.py`: Añadir exports
- [ ] `factory/__init__.py`: Verificar exports completos
- [ ] Renombrar si hay inconsistencias de naming

---

## 9. Metadatos

| Campo | Valor |
|-------|-------|
| Created | 2026-05-26 |
| Status | draft |
| Deps | 01-architecture.md |
| Related | 45-domain-entities.md (domain entities pattern) |
