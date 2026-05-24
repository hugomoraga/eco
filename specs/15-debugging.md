# 15. Debugging

## 15.1 Logs JSONL

Cada turno genera una línea en formato JSONL.

```json
{
  "turn": 14,
  "year": 47,
  "phase": "after_action",
  "action": "found_circle",
  "effects_applied": {
    "technocracy": 8,
    "anarchism": -3,
    "surveillance": 5
  },
  "state_delta": {
    "karax.stability": -4,
    "karax.ideological_drift": 9
  }
}
```

Cada línea contiene:
- estado antes
- acción tomada
- razón de la acción
- efectos aplicados
- estado después
- eventos generados
- mutaciones ideológicas
- decisiones del autoplayer
- prompts/respuestas IA (si aplica)

## 15.2 Inspector

Comando para analizar runs guardadas.

```bash
python inspect.py --run runs/run_0001.jsonl --entity karax
```

Output:

```txt
KÁRAX — Año 77

Dominantes:
- Anarquismo: 41
- Tecnocracia: 63
- Absurdismo: 18

Eventos principales:
- Año 47: Fundación de Protocolos Autónomos
- Año 61: Cisma Antimétrico
- Año 77: Surgimiento de Gobierno Algorítmico Informal

Causas del cambio:
- +22 tecnocracia por Modelo Maela
- -14 anarquismo por crisis de infraestructura
- +18 vigilancia por sabotajes repetidos
```

## 15.3 Replay

Comando para reproducir runs anteriores.

```bash
python replay.py --run runs/run_0001.jsonl --turn 1:100
```

Debe permitir avanzar paso a paso y revisar:
- acciones
- decisiones
- efectos
- eventos
- cambios de estado

## 15.4 Requisitos de logging

Todo debe ser reproducible. La misma seed + misma configuración = misma secuencia de logs.

## 15.5 Niveles de debug

```yaml
log_level:
  minimal:
    description: "solo acciones y resultados"
    fields:
      - turn
      - action
      - result

  standard:
    description: "+ estado delta y decisiones"
    fields:
      - turn
      - action
      - result
      - state_delta
      - autoplayer_decision

  verbose:
    description: "+ prompts IA y reasoning completo"
    fields:
      - turn
      - action
      - result
      - state_delta
      - autoplayer_decision
      - ai_prompt
      - ai_response

  trace:
    description: "+ cada decisión interna del autoplayer"
    fields:
      - all standard fields
      - goal_evaluation
      - context_modifiers
      - action_scores
      - chosen_action_reasoning
```

**Log levels aceptados:** `minimal`, `standard`, `verbose`, `trace`

## 15.6 Snapshot por tick

Para debugging avanzado, guardar snapshots completos en ciertos momentos:

```yaml
snapshot_interval: 10  # cada 10 turns
snapshot_on:
  - HistoricalTick
  - host_death
  - doctrine_mutation
  - faction_fracture
  - major_event
```

## 15.7 Estructura de runs

```txt
runs/
  run_0001.jsonl       # log completo
  run_0001.metadata    # seed, config, duración
  snapshots/
    world_state_0000.json
    world_state_0010.json
    world_state_0020.json
```

## 15.8 Filosofía

El sistema debe poder explicar:
- por qué una doctrina mutó
- por qué una ciudad colapsó
- por qué una facción se radicalizó

Si no puede, el sistema todavía no está listo.

---

## Metadata

- Origen: sección 12 del spec.md original
- Dependencias: 01-architecture.md
- Estado: incompleto - requiere revisión de todas las specs derivadas