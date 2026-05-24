# 10. Factions

## 10.1 Visión

Las facciones NO son contenedores pasivos. Tampoco tienen autoplayer completo tipo civilización IA total.

Sistema: **Faction Tick System** con objetivos, agency limitada, tick periódico.

## 10.2 Estructura de facción

```yaml
faction:
  id: "protocolos_autonomos"
  doctrines:
    - technocracy
    - anarchism
  goals:
    - stabilize_city
    - increase_algorithmic_governance
    - suppress_anti_metric_movements
  influence:
    districts: 3
    institutions: 2
    npc_support: 41
  behavior:
    aggression: 32
    secrecy: 71
    adaptability: 48
  resources:
    legitimacy: 44
    coordination: 62
    social_support: 39
```

## 10.3 Decisión de facción

Las facciones NO usan IA planner complejo. Usan scoring heurístico:

```yaml
possible_actions:
  - recruit_npc
  - infiltrate_archive
  - spread_doctrine
  - sabotage_rival
  - support_infrastructure
  - radicalize_members

score =
  (goal_alignment * 0.3) +
  (available_resources * 0.2) +
  (local_influence * 0.2) +
  (ideological_pressure * 0.2) +
  (behavior_modifier * 0.1)
  - risk

# Donde:
# - goal_alignment: 0-100, qué tanto la acción ayuda al goal actual
# - available_resources: 0-100, recursos de la facción disponibles
# - local_influence: 0-100, influencia actual en la zona
# - ideological_pressure: 0-100, presión ideológica del contexto
# - behavior_modifier: -20 a +20, según atributos de la facción
#   (aggression, secrecy, adaptability会影响 el score)
# - risk: 0-100, riesgo de la acción
```

**Behavior modifiers:**

```yaml
behavior_attributes:
  aggression:
    description: "Tendencia a acciones directas/confrontacionales"
    high_aggression_bonus:
      sabotage: +15
      radicalize: +10
      recruit: +5
      infiltrate: -10
      support_infrastructure: -5

  secrecy:
    description: "Capacidad de acciones ocultas"
    high_secrecy_bonus:
      infiltrate: +15
      spread_doctrine: +5
      sabotage: -10
      support_infrastructure: -5

  adaptability:
    description: "Capacidad de cambiar según contexto"
    high_adaptability_bonus:
      (all actions): +5
    low_adaptability_penalty:
      (all actions): -10

# Ejemplo de cálculo:
# Faction con aggression=80, secrecy=30, adaptability=50
# Acción: sabotage_rival
#   goal_alignment: 70
#   available_resources: 55
#   local_influence: 60
#   ideological_pressure: 45
#   behavior_modifier: +15 (high aggression bonus)
#   risk: 40

# score = (70*0.3) + (55*0.2) + (60*0.2) + (45*0.2) + (15) - 40
#       = 21 + 11 + 12 + 9 + 15 - 40 = 28
```

## 10.4 Faction Ticks

| Frecuencia | Contenido |
|------------|-----------|
| Daily | mover NPCs, rumores, reclutamiento pequeño |
| Weekly | propaganda, conflictos locales, influencia doctrinal |
| Monthly | expansión institucional, sabotaje, alianzas, cismas menores |
| Historical | fracturas doctrinales, radicalización, guerras, captura de ciudades, mutación ideológica |

## 10.5 Relación con el jugador

El jugador NO controla facciones directamente. Puede:
- infiltrarlas
- influirlas
- destruirlas
- fundarlas
- radicalizarlas
- moderarlas
- dividirlas
- capturarlas parcialmente

El mundo debe resistir al jugador.

## 10.6 Limitaciones

Las facciones NO son omniscientes. Solo reaccionan a:
- información accesible
- eventos visibles
- relaciones
- rumores
- instituciones conectadas
- NPCs afiliados

## 10.7 Ejemplo de tick

```yaml
FACTION_TICK — Protocolos Autónomos

Goal: increase_city_stability

Selected Action: capture_energy_grid

Reason:
  * infraestructura crítica colapsando
  * legitimidad tecnocrática creciendo
  * influencia local alta
  - riesgo militar bajo

Effects:
  +technocracy
  -anarchism
  +surveillance
  +infrastructure
```

## 10.8 Facciones como motores históricos

Las facciones representan ideas organizándose en poder. Son:
- organismos meméticos
- instituciones vivas
- interpretaciones activas de doctrinas
- motores históricos

## 10.9 Relación facciones ↔ deriva

Las facciones son uno de los motores principales de:
- reinterpretación doctrinal
- institucionalización
- radicalización
- propaganda
- mutación histórica

```txt
Idea original: "Voluntad Colectiva Calculada"

Faction A: la interpreta como coordinación horizontal
Faction B: la convierte en vigilancia algorítmica
Faction C: la ritualiza como sistema religioso

El jugador ve: la misma idea mutando en paralelo
```

## 10.10 KISS

**SÍ:**
- faction ticks
- objetivos simples
- scoring heurístico
- acciones limitadas
- logs claros
- replay completo

**NO:**
- GOAP complejo
- behavior trees gigantes
- simulación política profunda
- IA generativa tomando decisiones
- pathfinding estratégico sofisticado

## 10.11 Debugging obligatorio

Si una facción actúa sin causalidad clara, la implementación es incorrecta.

---

## Metadata

- Origen: sección 7.4 del spec.md original
- Dependencias: 01-architecture.md, 02-domain.md, 04-essences.md
- Notas: corregida fórmula de score, agregados behavior modifiers
- Estado: 🔄 En desarrollo