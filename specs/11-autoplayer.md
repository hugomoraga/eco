# 11. Autoplayer

## 11.1 Visión

El autoplayer no "gana". Representa una conciencia histórica intentando sobrevivir al tiempo, a las instituciones y a la reinterpretación humana.

El autoplayer: persiste, adapta, interpreta, intenta preservar o expandir una visión del mundo.

## 11.2 Modos

```txt
manual      → el humano decide
suggest     → autoplayer propone, humano confirma
autoplay    → autoplayer decide y ejecuta
director    → IA genera eventos externos, pero no controla al jugador
replay      → reproduce una run anterior
```

## 11.3 Objetivos explícitos

Los goals son intenciones declaradas que pueden cambiar según contexto.

```yaml
goal:
  id: "expand_doctrine"
  priority: 80
  doctrine_id: "doctrine_protocolos_autonomos"
  strategy:
    - identify_receptive_npc
    - plant_idea
    - institutionalize
    - reduce_distortion

goal:
  id: "survive_repression"
  priority: 60
  strategy:
    - reduce_public_presence
    - create_hidden_networks
    - preserve_knowledge
```

## 11.4 Evaluación multiobjetivo

El autoplayer evalúa múltiples métricas simultáneamente. NO existe score único ni victoria absoluta.

```yaml
evaluation:
  doctrinal_clarity: 0.24
  memetic_spread: 0.19
  institutional_control: 0.13
  ideological_stability: 0.18
  survival_probability: 0.11
  adaptability: 0.07
  narrative_risk: 0.04
  historical_impact: 0.04
```

Esto evita: estrategias únicas, loops repetitivos, maximización trivial.

## 11.5 Personalidad estratégica

El autoplayer tiene "estilo" que genera runs distintas incluso con mismo seed parcial.

**Cómo influye player_style en decisiones:**

```yaml
player_style:
  preservationist:
    prioritize:
      - clarity: +30   # weight en evaluación
      - stability: +20
      - continuity: +15
    action_bias:
      write_manifesto: +10   # aumenta score de esta acción
      found_circle: +5
      sabotage: -15          # reduce score de acciones agresivas
      infiltrate: -10

  revolutionary:
    prioritize:
      - spread: +30
      - destabilization: +20
      - radicalization: +15
    action_bias:
      sabotage: +15
      radicalize_members: +10
      write_manifesto: +5
      preserve_knowledge: -10

  manipulator:
    prioritize:
      - shadow: +30
      - infiltration: +25
      - institutional_capture: +15
    action_bias:
      infiltrate: +20
      spread_doctrine: +10
      talk: +5
      direct_conflict: -20

  mystic:
    prioritize:
      - symbolism: +25
      - rituals: +25
      - cultural_influence: +20
    action_bias:
      ritualize: +20
      write_manifesto: +10
      recruit: +5
      sabotage: -15

  technocrat:
    prioritize:
      - infrastructure: +25
      - coordination: +25
      - stability: +20
    action_bias:
      support_infrastructure: +15
      found_circle: +10
      recruit: +5
      radicalize: -10
```

**El player_style se aplica así:**
1. En evaluación multiobjetivo, se multiplican los pesos por los valores de prioritize
2. En scoring de acciones, se aplica action_bias como modificador

## 11.6 Presión adaptativa contextual

El autoplayer cambia prioridades según contexto. Las reglas son machine-readable:

```yaml
adaptive_rules:
  - id: "survive_repression"
    condition:
      and:
        - repression_level: "> 60"
        - influence: "< 40"
    action:
      prioritize_survival: "+= 20"

  - id: "repair_doctrine"
    condition:
      and:
        - doctrine_fragmenting: true
        - clarity: "< 50"
    action:
      prioritize_doctrinal_repair: "+= 15"

  - id: "stabilize_collapse"
    condition:
      civilization_health: "< 40"
    action:
      prioritize_stability: "+= 25"

  - id: "defend_faction"
    condition:
      faction_pressure: "> 70"
    action:
      prioritize_defense: "+= 10"

  - id: "exploit_instability"
    condition:
      and:
        - unrest: "> 70"
        - opposing_faction_strength: "< 50"
    action:
      prioritize_expansion: "+= 15"

  - id: "preserve_legacy"
    condition:
      host_age: "> 55"
    action:
      prioritize_memory: "+= 20"
      increase_transfer_preparation: true
```

**Formato de condición:**
```yaml
condition:
  field_name: "value_or_operator"
  # Operadores: >, <, >=, <=, ==, !=
  # Combinaciones: and, or, not
```

**Formato de acción:**
```yaml
action:
  priority_to_modify: "+= value"  # +=, -=, = (asignar)
  flag_to_set: true              # boolean flags
```

## 11.7 Métricas meméticas persistentes

El éxito principal NO es conquistar territorios ni acumular recursos. Es la persistencia y transformación histórica de ideas.

```txt
La doctrina original desapareció,
pero:
  - inspiró 3 movimientos
  - mutó en 2 religiones
  - causó una revolución
  - sigue viva 300 años después

Eso es éxito memético.
```

Las doctrinas pueden: fragmentarse, mezclarse, deformarse, sobrevivir parcialmente. Eso también puede considerarse "éxito".

## 11.8 Decisión del autoplayer

```json
{
  "turn": 22,
  "selected_action": "talk",
  "target": "npc_maela_ruun",
  "score": 82,
  "reason": "NPC has high influence, compatible hidden beliefs, and low hostility.",
  "alternatives": [
    {"action": "write_manifesto", "score": 61},
    {"action": "sabotage", "score": 34}
  ]
}
```

## 11.9 Take Control

El cliente debe permitir:

```txt
TAKE CONTROL
```

Esto cancela la siguiente acción del autoplayer y pasa a modo manual.

## 11.10 Temporalidad

El autoplayer usa el mismo sistema temporal que el jugador:
- elige acciones con duración
- puede usar bloques explícitos
- encadena secuencias
- espera entre acciones

## 11.11 KISS

**NO:**
- reinforcement learning
- utility AI compleja
- árboles de planificación gigantes
- simulación psicológica profunda

**SÍ:**
- weighted scoring
- goals simples
- context modifiers
- evaluation logs
- replay
- explicabilidad

## 11.12 Debugging obligatorio

```txt
AUTOPLAYER DECISION

Current Goals:
  - preserve_doctrine
  - survive_repression

Context:
  - unrest: 71
  - surveillance: 64
  - clarity: 39

Selected Action: create_hidden_archive

Reason:
  * doctrinal fragmentation increasing
  * high repression risk
  * low public safety
  * archive access available

Expected Effects:
  +memory, +doctrinal_continuity, -public_influence_short_term
```

Si el autoplayer no puede explicar causalmente sus decisiones, la implementación es incorrecta.

---

## Metadata

- Origen: secciones 9.1-9.11 del spec.md original
- Dependencias: 01-architecture.md, 03-player-echo.md, 06-ideological-drift.md, 07-actions.md
- Notas: player_style con action_bias, adaptive_rules machine-readable
- Estado: 🔄 En desarrollo