# 29 - World State Metrics

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 07, 08, 26  

---

## 1. Contexto

Spec-26 define world metrics (pressure, legitimacy, resources) pero no están implementados. Sin ellos, los eventos no pueden tener consecuencias y el mundo no evoluciona.

---

## 2. Métricas del Mundo

```python
# En World entity (domain/entities.py)
class World(BaseModel):
    # ... existing fields ...
    
    # World State Metrics (spec-26)
    pressure: float = 30.0       # Civil unrest, 0-100
    legitimacy: float = 60.0     # Authority trust, 0-100
    resources: float = 70.0     # Food/energy, 0-100
    
    # Thresholds for events
    crisis_threshold: float = 75.0  # pressure > 75 → crisis events
    collapse_threshold: float = 15.0  # legitimacy < 15 → regime collapse
```

**Rangos:** 0-100 para todas las métricas. Inicializan en valores medios.

---

## 3. Turn Evolution

Cada world tick (entre turnos del jugador), las métricas cambian:

```python
def world_tick_evolve(world: World) -> None:
    """Called during WorldTick, evolves world metrics."""
    
    # Natural drift (small random walk)
    world.pressure += random.uniform(-1.5, +2.0)
    world.legitimacy += random.uniform(-0.5, +1.0)
    world.resources += random.uniform(-0.8, +1.2)
    
    # Pressure affects legitimacy
    if world.pressure > 70:
        world.legitimacy -= (world.pressure - 70) * 0.05
    
    # High resources reduce pressure
    if world.resources > 80:
        world.pressure -= (world.resources - 80) * 0.03
    
    # Clamp values
    world.pressure = max(0, min(100, world.pressure))
    world.legitimacy = max(0, min(100, world.legitimacy))
    world.resources = max(0, min(100, world.resources))
```

---

## 4. Event Consequences

Los eventos definidos en spec-13 modifican las métricas:

```
EVENT TYPES → WORLD METRIC CHANGES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRISIS (negative):
  → pressure += 10-20
  → legitimacy -= 5-15
  → resources -= 5-10

OPPORTUNITY (positive):
  → resources += 5-15
  → legitimacy += 3-8
  → pressure -= 3-5

CONFLICT:
  → pressure += 15-25
  → resources -= 10-20
  → legitimacy -= 10

REVELATION:
  → pressure += 5-10 (unrest from truth)
  → legitimacy -= 3-7

CONVERGENCE:
  → pressure -= 5-10 (stability from unity)
  → legitimacy += 2-5
```

---

## 5. Modificador de Acciones

Las acciones del jugador también pueden modificar métricas:

```
ACTIONS → WORLD METRIC CHANGES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

found_circle:
  → legitimacy -= 2 (authority dislikes assembly)
  → pressure += 1 (organization is threat)

write_manifesto:
  → pressure += 3 (ideas spread unrest)
  → legitimacy -= 1

propagate_idea:
  → pressure += 2 per target
  → legitimacy -= 1

sabotage:
  → legitimacy -= 5 (authority retaliates)
  → resources -= 5
  → pressure += 8 (conflict)

ritualize:
  → pressure -= 3 (rituals calm masses)
  → legitimacy -= 1 (authority dislikes rituals)

talk (successful recruit):
  → pressure += 1 (social bonds)
```

---

## 6. Console Output

Cuando una métrica cambia significativamente:

```
[Turn 5] 📉 Authority legitimacy: 60 → 52 (-8)
[Turn 6] 📈 Civil unrest rises: 45 → 58 (+13)
[Turn 7] ⚡ Crisis threshold crossed (pressure: 76)
```

**Threshold crossed:** cuando `pressure > crisis_threshold`, se marca como evento.

---

## 7. Dependencias con spec-28

El World Activity Summary (spec-28 sección 2) puede incluir cambios de métricas si son significativos (cambio > 10 puntos).

---

## 8. Implementación

**Files to modify:**
- `game_core/domain/entities.py` — agregar campos a World
- `game_core/engine/simulation.py` — world tick evolution
- `game_core/engine/actions/` — cada acción modifica world
- `game_core/events/` — cada evento modifica world

**Tests:**
- Metrics evolve each world tick
- Actions modify metrics correctly
- Events modify metrics correctly
- Clamping keeps values in range