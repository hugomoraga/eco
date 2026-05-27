# SPEC: Domain Entity Refactor — Person/Host Pattern

## Status: Draft
## Canonical Reference: specs/45-domain-entities.md

---

## 1. Overview

La jerarquía anterior (`NPC` como entidad plana) se reemplaza por:

- **`Person`** — Individuo base en el mundo. Tiene `type: "npc" | "player"`.
- **`Host`** — Contexto de encarnación. Extiende una `Person` con campos de Echo. No duplica datos de Person.
- **`Echo`** — Consciencia persistente. Vive independiente de cualquier Person.

**El jugador ES una Person con `type="player"` que tiene un Host activo.**

---

## 2. Entity: Person (renamed from NPC)

```python
class Person(BaseModel):
    """
    Individuo base en el mundo.
    - type="npc"   → NPC normal, controlado por el juego
    - type="player"→ Person actualmente habitada por el Echo del jugador
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Identity
    name: str
    essence: str | None = None          # Puede ser None si no tiene doctrina aún
    role: str
    archetype: str

    # Tipo — определяет quién controla esta person
    type: Literal["npc", "player"] = "npc"

    # Historial de Echo — permite saber si fue host anteriormente
    echo_id: str | None = None          # Echo que la habitó (incluso si ya no es player)

    # Faction membership
    faction_id: str | None = None
    loyalty: float = 50.0

    # Influence
    influence: int = 0

    # Métricas de salud (nuevas)
    vitality: float = 100.0            # salud física
    coherence: float = 50.0            # estabilidad ideológica
```

**Reglas:**
- Solo puede haber UNA Person con `type="player"` a la vez
- Cuando una Person "muere" → se marca como inactiva, no se borra
- `echo_id` permanece como registro histórico aunque el Echo se mude a otra Person

---

## 3. Entity: Host (extension layer)

```python
class Host(BaseModel):
    """
    Contexto de encarnación.
    Se "pega" a una Person que tiene type="player".
    NO duplica campos de Person — solo añade contexto de Echo.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Link a la Person que habita
    person_id: str

    # Link al Echo que encarna en esta Person
    echo_id: str

    # Métricas del Host
    will: float = 50.0
    presence: float = 50.0             # capacidad de influenciar

    # Historial
    action_history: list[str] = Field(default_factory=list)
    last_action_turn: dict[str, int] = Field(default_factory=dict)

    # Círculo activo actual
    active_circle_id: str | None = None

    # Contador de acciones este turno (para fatiga)
    actions_this_turn: int = 0
```

**Reglas:**
- Una Person con `type="player"` TIENE exactamente un Host asociado
- Host moribundo = Person moribunda → cuando `Person.vitality <= 0` → `Person.type = "npc"` + Host se desvincula
- El Echo busca nueva Person compatible y crea Host + cambia `Person.type = "player"`
- `Host.is_player` no existe — la distinción está en `Person.type`

---

## 4. Entity: Echo (canonical, unchanged from previous spec)

```python
class Echo(BaseModel):
    """Consciencia persistente del jugador. Sin cuerpo propio."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    name: str = ""

    # Genealogy — historial de essencias mutadas
    genealogical_lineage: list[str] = Field(default_factory=list)

    # Ideas propagadas por este Echo
    ideas: list[Ideas] = Field(default_factory=list)

    resonance: float = 50.0
    memory_depth: int = 0
    clarity: float = 50.0              # coherencia ideológica

    shadow_coherence: float = 100.0
    temporal_strain: float = 0.0

    reincarnation_count: int = 0
    last_awakening: datetime | None = None

    manifestos: list[Manifesto] = Field(default_factory=list)

    @property
    def dominant_essence(self) -> str | None:
        return self.genealogical_lineage[-1] if self.genealogical_lineage else None
```

---

## 5. Entity: Civilization (renamed from World)

```python
class Civilization(BaseModel):
    """Sistema histórico-material. El mundo超大."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unknown Civilization"

    clock: WorldClock

    # Entidades
    echoes: list[Echo] = Field(default_factory=list)
    factions: list[Faction] = Field(default_factory=list)
    circles: list[Circle] = Field(default_factory=list)

    # Persons — TODAS las personas del mundo (npc + player)
    persons: list[Person] = Field(default_factory=list)

    # Hosts activos — uno por Person.type="player"
    hosts: list[Host] = Field(default_factory=list)

    # Essencia del mundo
    dominant_essence: str = "technocracy"

    # Métricas globales
    pressure: float = 30.0
    legitimacy: float = 60.0
    resources_global: float = 70.0
    stability: float = 50.0

    infrastructure: dict[str, float] = Field(default_factory=dict)

    population: int = 0

    crisis_threshold: float = 70.0
    collapse_threshold: float = 30.0

    # Methods
    def get_player_person(self) -> Person | None:
        for p in self.persons:
            if p.type == "player":
                return p
        return None

    def get_player_host(self) -> Host | None:
        pp = self.get_player_person()
        if not pp:
            return None
        for h in self.hosts:
            if h.person_id == pp.id:
                return h
        return None

    def get_player_echo(self) -> Echo | None:
        ph = self.get_player_host()
        if not ph:
            return None
        for e in self.echoes:
            if e.id == ph.echo_id:
                return e
        return None

    def is_crisis(self) -> bool:
        return self.pressure > self.crisis_threshold

    def evolve_metrics(self, rng) -> dict[str, float]:
        ...

    def clamp_metrics(self) -> None:
        ...
```

**Note:** Alias para backward compat: `World = Civilization`

---

## 6. Entity: Ideas (renamed from IdeologicalTag)

```python
class Ideas(BaseModel):
    """Una doctrina específica."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str              # "concept" | "practice" | "symbol"
    name: str                  # "Consenso Horizontal"

    origin_echo_id: str | None = None

    essence_weights: dict[str, float] = Field(default_factory=dict)

    @property
    def dominant_essence(self) -> str | None:
        if not self.essence_weights:
            return None
        return max(self.essence_weights, key=self.essence_weights.get)

    def to_semantic_key(self) -> str:
        return f"{self.category}:{self.name}"
```

---

## 7. Essence — dónde vive

| Entidad | Campo | Significado |
|---|---|---|
| `Echo` | `genealogical_lineage[-1]` | Identidad profunda |
| `Person` | `essence` | Identidad de la persona individual |
| `Host` | heredado de Echo | Doctrina del host |
| `Circle` | `essence` | Doctrina oficial del Círculo |
| `Faction` | `essence` | Doctrina de la facción |
| `Civilization` | `dominant_essence` | Identidad del mundo |

---

## 8. Circle y Faction — Updated with Ideas

```python
class Circle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    essence: str

    member_ids: list[str] = Field(default_factory=list)   # Person ids
    echo_ids: list[str] = Field(default_factory=list)       # Echo ids

    ideas: list[Ideas] = Field(default_factory=list)       # era ideology_tags

    founding_tick: int
    influence: float
    institutionalization_level: float = 0.0
    health: float = 100.0

    status: CircleStatus
    dormant_turns: int = 0
    history: list[CircleEvent] = Field(default_factory=list)
```

```python
class Faction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    essence: str

    ideas: list[Ideas] = Field(default_factory=list)       # era ideology_tags

    members: list[str] = Field(default_factory=list)        # Person ids
    circles: list[str] = Field(default_factory=list)         # Circle ids

    influence: float
    resources: dict[str, float]
    goals: list[str]
    radicalization: float = 0.0
```

**Migration:** `ideology_tags: list[str]` → `ideas: list[Ideas]`

---

## 9. Manifesto

```python
class Manifesto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    essence: str
    written_at_tick: int
    echo_id: str
    ideas: list[Ideas] = Field(default_factory=list)
```

`Echo.manifestos: list[str]` → `Echo.manifestos: list[Manifesto]`

---

## 10. Ciclo de vida Player completo

```
[Start]
  │
  ├─► Civilization tiene Persons[] (varias npc)
  │
  ├─► Echo se despierta → busca Person compatible
  │
  ├─► Person.type = "player" + echo_id set
  │
  ├─► Host creado con (person_id, echo_id)
  │
  ▼
[Game Loop]
  │
  ├─► Player actúa → Host.action_history += action
  │
  ├─► Turno avanza → pressure/legitimacy cambian
  │
  ├─► Si vitality <= 0:
  │     ├─► Person.type = "npc"
  │     ├─► Host desvinculado (queda en hosts[] con estado inactive)
  │     └─► Echo reincarna → busca nueva Person compatible
  │
  ▼
[Continúa]
```

**Regla:** Solo UN `Person.type="player"` y UN `Host.is_active=True` a la vez.

---

## 11. Migration Map

| Antes | Después | Notas |
|---|---|---|
| `World` | `Civilization` | Alias `World = Civilization` |
| `NPC` | `Person` | Rename + `type` field |
| _(ninguno)_ | `Host` | NUEVO — extensión de Person |
| `Echo.code` | `Echo.canonical` | Genealogical lineage en vez de essence directo |
| `IdeologicalTag` | `Ideas` | Rename |
| `World.npcs` | `Civilization.persons` | Rename |
| `World.hosts` | `Civilization.hosts` | Hosts activos (no había antes) |
| `Person.echo_id` | `Person.echo_id` | Nuevo campo — historial de quién la habitó |

---

## 12. Backward Compatibility — 4 fases

### Fase 1 — Aliases y renombrados triviales
```python
# entities/__init__.py
Person = NPC  # backward compat — primero se migran los imports
World = Civilization  # alias

IdeologicalTag = Ideas  # alias
```

### Fase 2 — Nuevo modelo Person + Host (sin romper NPC)
- Crear `Person` con `type: Literal["npc", "player"]`
- Migrar `NPC` fields a `Person`
- Añadir campo `echo_id: str | None` a `Person`
- Crear modelo `Host` con campos de encarnación
- `Civilization.persons: list[Person]` coexist with `Civilization.npcs: list[NPC]` durante transición

### Fase 3 — Migrar Circle/Faction Ideas
- `Circle.ideology_tags` → `Circle.ideas`
- `Faction.ideology_tags` → `Faction.ideas`
- Migración automática: cada string de ideology_tags se convierte a `Ideas(category="concept", name=tag)`

### Fase 4 — Limpiar Legacy
- Eliminar `NPC` — ya no se usa, `Person` lo reemplaza
- Eliminar `Civilization.npcs` — ya no se usa
- Eliminar `World` alias — solo `Civilization`
- Deprecar `IdeologicalTag` alias

---

## 13. Factory updates

```
game_core/factory/
├── person.py    → create_person() — factory de Person/NPC
├── host.py      → create_host()   — vincula Echo + Person, cambia type="player"
├── echo.py      → create_echo()  — factory de Echo (ya existe, actualizar campos)
├── ideas.py     → rename from tags.py → create_ideas_for_essence()
├── tags.py      → DEPRECATED → from tags import Ideas as IdeologicalTag
└── manifesto.py → create_manifesto()
```

**`create_host()` logic:**
```python
def create_host(civ: Civilization, person_id: str, echo_id: str) -> Host:
    person = civ.get_person(person_id)
    person.type = "player"
    person.echo_id = echo_id

    host = Host(person_id=person_id, echo_id=echo_id)
    civ.hosts.append(host)
    return host
```

**Death + reincarnation:**
```python
def on_host_death(civ: Civilization, host: Host):
    person = civ.get_person(host.person_id)
    person.type = "npc"
    person.vitality = 100.0  # reset para posible reuse

    # Buscar nueva person compatible
    compatible = find_compatible_person(civ, host.echo_id)
    if compatible:
        new_host = create_host(civ, compatible.id, host.echo_id)
        echo = civ.get_echo(host.echo_id)
        echo.reincarnation_count += 1
        return new_host
    return None
```

---

## 14. Pending decisions

- [ ] `Person.vitality` — ¿se usa para muerte física (hambruna) o también ideología?
- [ ] `Person.coherence` — ¿cuándo baja de threshold, el Host se considera "desconectado"?
- [ ] Búsqueda de Person compatible — ¿qué campos de Person importan para decidir compatibilidad con un Echo? (esencia, archetype, role?)
- [ ] `Host.presence` vs `Person.influence` — ¿son el mismo concepto en capas diferentes?