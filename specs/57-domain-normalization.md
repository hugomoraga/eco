# 57 - Domain Normalization

**Status:** draft
**Created:** 2026-05-27
**Goal:** Clean separation between static data and runtime state

---

## Principios

1. **entities/** = solo estado runtime mutable
2. **data/** = catálogos YAML estáticos (no importar directamente)
3. **definitions/** = wrappers tipados para data
4. **value_objects/** = estructuras inmutables reutilizables
5. `Host` = legacy, no usar en código nuevo
6. Resonance = definición estática en data, NO entidad runtime

---

## Estructura de Carpetas

```
eco/
├── core/
│   └── domain/
│       ├── entities/              # Estado runtime mutable
│       │   ├── actor.py           # Compite, gana, tiene influence
│       │   ├── echo.py            # Identidad persistente
│       │   ├── person.py          # Cuerpo / NPC
│       │   ├── civ.py             # Estado social vivo
│       │   ├── world.py           # Contenedor runtime
│       │   ├── idea.py            # Meme activo
│       │   ├── doctrine.py        # Idea estabilizada
│       │   ├── manifesto.py       # Texto que crea/modifica ideas
│       │   ├── circle.py          # Célula / grupo pequeño
│       │   ├── faction.py          # Grupo político
│       │   └── event.py           # Log runtime
│       │
│       ├── value_objects/          # Estructuras inmutables
│       │   ├── resonance_profile.py
│       │   ├── resonance_score.py
│       │   └── resource_pool.py
│       │
│       └── definitions/            # Wrappers tipados para data estática
│           ├── resonance_def.py
│           ├── action_def.py
│           ├── civ_template.py
│           ├── person_archetype.py
│           ├── goal_def.py
│           └── idea_archetype.py
│
├── data/                          # YAML estático
│   ├── resonances.yaml            # Definiciones de esencias
│   ├── actions.yaml
│   ├── civs/
│   └── persons/
│
└── adapters/
```

---

## Entidades Runtime (entities/)

### Actor
**Unidad que juega y puede ganar.**

```python
class Actor:
    id: str
    name: str
    type: Literal["human", "npc", "faction_ai"]

    # Links de vinculación
    echo_id: str | None              # Link a Echo (identidad)
    person_id: str | None            # Link a Person (cuerpo encarnado)
    faction_id: str | None           # Link a Faction (si pertenece)

    # Meta
    goal_id: str                      # Goal activo

    # Estado competitivo
    influence: float = 0.0           # Influencia política
    resources: ResourcePool

    # Historial
    action_history: list[str]

    # Recursos meméticos
    idea_ids: list[str]
    doctrine_ids: list[str]
    manifesto_ids: list[str]
    circle_ids: list[str]
```

### Echo
**Identidad persistente.** Supervive a las encarnaciones.

```python
class Echo:
    id: str
    name: str

    # Resonance de la identidad
    resonance: ResonanceProfile

    # Fase de existencia
    phase: EchoPhase                # DORMANT, AWAKENED, MANIFEST, PHANTOM

    # Genealogía (se mueve aquí desde Actor)
    genealogical_lineage: list[str]  # Historial de esencias
    reincarnation_count: int = 0    # Veces reencarnado

    # Atributos de identidad
    temporal_strain: float = 0.0     # Degradación por tiempo
    shadow_coherence: float = 100.0 # Coherencia de identidad
    presence: float = 0.0           # Presencia física

    # Reencarnación
    last_awakening: datetime | None

    # Eventos existenciales (NO acciones de gameplay)
    # - awakenings: cuando el Echo se manifiesta
    # - reincarnations: cuando cambia de Person
    # - fractures: cuando una idea se bifurca
    # - lineage_events: cambios en genealogical_lineage
    existential_events: list[ExistentialEvent]

    # Ideas y manifestos (referencias)
    idea_ids: list[str]
    manifesto_ids: list[str]
    known_doctrine_ids: list[str]
```

**Nota:** `Echo.action_history` eliminado. Las acciones de gameplay viven en `Actor.action_history`. Echo solo registra eventos existenciales/metafísicos.

### Person
**Cuerpo físico.** Puede ser NPC o Player.

```python
class Person:
    id: str
    name: str

    archetype: str                   # warrior, mystic, merchant, scholar, etc
    role: str                        # Rol social

    # Civ a la que pertenece
    civ_id: str | None

    # Facciones
    faction_ids: list[str]

    # Estado físico (se mueve aquí desde Actor)
    vitality: float = 100.0

    # Tipo
    type: Literal["npc", "player"]

    # Link a Actor (si está encarnado)
    actor_id: str | None
```

### Civ
**Estado social vivo de una civilización.**

```python
class Civ:
    id: str
    meta_id: str                      # Template ID (technocracy, theocracy, etc)
    name: str
    description: str

    # Estado social
    population: int = 10000
    stability: float = 50.0           # Estabilidad general
    pressure: float = 30.0            # Tensión social
    legitimacy: float = 60.0          # Legitimidad del liderazgo
    resources: ResourcePool

    # Resonance de la civ
    resonance: ResonanceProfile

    # Ratios objetivo
    target_aligned_ratio: float = 0.7

    # Entidades de la civ
    person_ids: list[str]
    faction_ids: list[str]
```

### World
**Contenedor runtime.** Solo IDs y eventos, no estado duplicado.

```python
class World:
    clock: WorldClock

    # Solo IDs - el estado vive en las entidades
    civ_ids: list[str]
    actor_ids: list[str]
    person_ids: list[str]
    circle_ids: list[str]
    faction_ids: list[str]
    idea_ids: list[str]
    doctrine_ids: list[str]
    manifesto_ids: list[str]

    # Event log
    events: list[Event]

    # Turno activo
    active_actor_id: str | None

class WorldClock:
    action_tick: int = 0
    world_tick: int = 0              # action_tick / 10
    historical_tick: int = 0         # world_tick / 100
```

### Idea
**Meme activo runtime.**

```python
class Idea:
    id: str
    author_actor_id: str

    name: str
    kind: Literal[
        "belief",
        "rumor",
        "movement_seed",
        "manifesto_seed"
    ]

    # Resonance weights
    resonance: ResonanceProfile

    # Atributos meméticos (spec-05)
    clarity: float = 50.0             # Coherencia, resistencia a distorsión
    virality: float = 50.0           # Capacidad de propagación
    stability: float = 50.0           # Resistencia a mutación
    mutation_risk: float = 50.0       # Probabilidad de transformación
    spread: float = 0.0               # Alcance actual
    followers: int = 0                # Seguidores actuales

    # Ciclo de vida
    state: IdeaState                 # GERMINATING, EXPANDING, STABLE, MUTATING, DEAD
    world_tick_created: int

    # Genealogía
    parent_idea_ids: list[str]
    child_idea_ids: list[str]

    # Distorsión (alejamiento del origen)
    distortion: float = 0.0

    # Institucionalización
    doctrine_id: str | None          # Si se convirtió en doctrina
```

### Doctrine
**Idea estabilizada en institución.**

```python
class Doctrine:
    id: str
    name: str
    source_idea_id: str

    resonance: ResonanceProfile

    # Institucionalización
    institutionalization: float = 0.0
    distortion: float = 0.0

    # Ramas
    branches: list[DoctrineBranch]

    # Seguidores
    follower_count: int = 0
    stability: float = 50.0

class DoctrineBranch:
    id: str
    name: str
    emphasis: str                    # Interpretación principal
    core_resonance_id: str           # Esencia dominante
    secondary_resonance_id: str     # Esencia secundaria
    distortion: float = 0.0
    follower_count: int = 0
    stability: float = 50.0
```

### Manifesto
**Vehículo textual que crea o modifica Ideas.**

```python
class Manifesto:
    id: str
    author_actor_id: str
    content: str                     # Texto
    resonance_id: str                 # Esencia dominante

    # Ideas que creó o modificó
    created_idea_ids: list[str]
    modified_idea_ids: list[str]

    # Impacto
    influence_generated: float = 0.0
    world_tick_created: int

    # Tags derivados (IDs de Ideas)
    tag_ids: list[str]
```

### Circle
**Célula / grupo pequeño.** Miembros son personas físicas.

```python
class Circle:
    id: str
    name: str
    founder_actor_id: str | None      # Fundador (Actor)
    resonance_id: str                 # Esencia del círculo
    founding_tick: int

    # Miembros (personas físicas)
    member_person_ids: list[str]

    # Ideas discutidas
    idea_ids: list[str]

    # Estado
    influence: float = 0.0
    institutionalization: float = 0.0
    health: float = 100.0
    status: CircleStatus             # ACTIVE, DORMANT, SPLINTERED, DISSOLVED

    # Eventos históricos
    history: list[CircleEvent]
```

### Faction
**Grupo político.** Goals pertenecen al Actor, no a la Faction.

```python
class Faction:
    id: str
    name: str
    resonance_id: str
    ideology_tag_ids: list[str]      # Idea IDs usados como tags

    # Miembros
    member_person_ids: list[str]
    circle_ids: list[str]

    # Estado
    influence: float = 0.0
    radicalization: float = 0.0

    # Recursos propios
    resources: ResourcePool

    # Líder/Controlador (único Actor que dirige la facción)
    actor_id: str | None
```

### Event
**Entrada del event log runtime.**

```python
class Event:
    turn: int
    type: str
    data: dict
    timestamp: datetime
```

---

## Value Objects (value_objects/)

### ResonanceProfile
```python
class ResonanceProfile:
    dominant: list[ResonanceScore]      # 1-3 esencias, suma ~100
    underlying: list[ResonanceScore]    # Resto, 0-100 c/u
```

### ResonanceScore
```python
class ResonanceScore:
    resonance_id: str                  # ID de esencia (thelema, anarchism, etc)
    value: float                       # 0-100
```

### ResourcePool
```python
class ResourcePool:
    food: float = 100.0
    infrastructure: float = 80.0
    energy: float = 60.0
    knowledge: float = 40.0
    # NOTA: legitimacy NO está aquí, vive en Civ
```

---

## Definitions (definitions/)

Wrappers tipados para data estática YAML. Se cargan una vez y se cachean.

### ResonanceDef
Wrapper para `resonances.yaml` (antes `essences.yaml`)

### ActionDef
Wrapper para `actions.yaml`

### CivTemplate
Wrapper para `civs/*.yaml`

### PersonArchetype
Wrapper para `persons/archetypes/*.yaml`

### GoalDef
Wrapper para goals

### IdeaArchetype
Wrapper para idea templates

---

## Archivos a ELIMINAR / LEGACY

### Mover a legacy/
- `host.py` - DEPRECATED, reemplazado por Actor.person_id + Person.actor_id
- `npc.py` - Redundante con Person
- `ideas.py` - Reemplazado por `idea.py` + value_objects

### Renombrar en data/
- `essences.yaml` → `resonances.yaml`

---

## Relaciones Finales

```
Actor = unidad que compite, gana y acumula influence
    ├── echo_id → Echo (identidad persistente)
    ├── person_id → Person (cuerpo encarnado)
    ├── faction_id → Faction (grupo político)
    └── goal_id → GoalDef (objetivo competitivo)

Echo = identidad persistente / alma / linaje
    ├── resonance (ResonanceProfile)
    ├── genealogical_lineage
    ├── reincarnation_count
    ├── presence
    └── last_awakening, phase (eventos existenciales)

Person = cuerpo físico / NPC
    ├── vitality
    ├── civ_id → Civ
    └── actor_id → Actor (si está encarnado)

Civ = estado social vivo
    ├── population, pressure, legitimacy, stability
    ├── resources (ResourcePool)
    ├── resonance (ResonanceProfile)
    └── person_ids[], faction_ids[]

World = contenedor runtime
    └── Solo IDs + eventos

Idea = meme activo
    ├── clarity, virality, stability, mutation_risk, spread, followers
    ├── state (ciclo de vida)
    └── doctrine_id → Doctrine (si se estabilizó)

Doctrine = idea estabilizada
    └── branches[]

Manifesto = vehículo textual
    └── created_idea_ids[], modified_idea_ids[]

Circle = célula social pequeña
    ├── member_person_ids[] (personas físicas)
    └── idea_ids[]

Faction = grupo político
    ├── resonance_id
    ├── member_person_ids[]
    ├── circle_ids[]
    └── actor_id → Actor (líder/controlador)

GoalDef = definición de objetivo (pertenece a Actor)
```

---

## Notas de Naming

1. **resonance** = término técnico para el perfil de esencias runtime
2. **essence** = término narrativo/lore, NO usar en código
3. `resonances.yaml` = archivo de definiciones estáticas
4. `ResonanceScore.resonance_id` = ID de la esencia
5. `ResonanceProfile` = contenedor de ResonanceScores

## Notas de Migración

1. `Actor.vitality` → `Person.vitality`
2. `Actor.presence` → `Echo.presence`
3. `Actor.reincarnation_count` → `Echo.reincarnation_count`
4. `Actor.genealogical_lineage` → `Echo.genealogical_lineage`
5. `essences.yaml` → `resonances.yaml`
6. `Host` → legacy, no nuevo uso