# SPEC: Domain Entity Refactor

## Status: Draft
## Canonical Reference: specs/44-domain-entities.md (entity definitions)

---

## 1. Overview

Current domain entities map to canonical ones with these mismatches:

| Code Entity | Canonical Name | Notes |
|---|---|---|
| `World` | `Civilization` | Rename + expand |
| `Echo` (code) | `Host` | Refactor fields, rename |
| `NPC` | `Host` (tipo=npc) | Keep NPC, use as Host |
| `IdeologicalTag` | `Ideas` | Rename only |
| `Circle` | `Circle` | Migrate ideology_tags → list[Ideas] |
| `Faction` | `Faction` | Migrate ideology_tags → list[Ideas] |
| _(none)_ | `Echo` | NEW — conscience without body |
| _(none)_ | `Civilization` | NEW — rename from World |

---

## 2. New Entity: Echo (canonical)

Pure persistent consciousness. **No body, no attributes.**

```python
class Echo(BaseModel):
    """Consciencia persistente del jugador. Sin cuerpo propio."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identity
    name: str = ""
    
    # Genealogy — historial de ESENCIAS mutadas
    # ["anarchism", "eco_anarchism", "technocracy"]
    genealogical_lineage: list[str] = Field(default_factory=list)
    
    # Ideas — doctrinas propagadas por este Echo
    # Pueden serIdeas de diverso origen
    ideas: list[Ideas] = Field(default_factory=list)
    
    # Echo-level memory y resonance
    resonance: float = 50.0
    memory_depth: int = 0
    clarity: float = 50.0   # coherencia ideológica
    
    # Shadow — faceta oculta
    shadow_coherence: float = 100.0
    
    # Metrica de salud del Echo
    temporal_strain: float = 0.0
    
    # Contadores
    reincarnation_count: int = 0
    last_awakening: datetime | None = None
    
    # Manifiestos generados
    manifestos: list[Manifesto] = Field(default_factory=list)
```

**No tiene:**
- `essence` directo → usa `genealogical_lineage[-1]` o `dominant_essence`
- `attributes` → no tiene bodies
- `circles` → no pertenece a circles, los influencia

---

## 3. New Entity: Host

Current incarnation. Links an Echo to a world entity.

```python
class Host(BaseModel):
    """
    Encarnación actual del Echo.
    
    Puede ser:
    - Un NPC existente → tipo="npc"
    - Una entidad standalone → tipo="echo"
    
    Marcar como "jugador": Host.is_player = True
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Link to Echo
    echo_id: str
    
    # Tipo de host
    # "npc"  → NPC del mundo que sepromovió a host
    # "echo" → entidad standalone marcada como host del jugador
    host_type: Literal["npc", "echo"] = "npc"
    
    # Si host_type="npc": referencia al NPC real
    # El Host ENVUELVE un NPC — no duplica datos
    npc_id: str | None = None
    
    # Métricas del Host
    will: float = 50.0
    presence: float = 50.0
    
    # Historial doctrinario de este host
    action_history: list[str] = Field(default_factory=list)
    last_action_turn: dict[str, int] = Field(default_factory=dict)
    
    # Círculo activo actual (si pertenece)
    active_circle_id: str | None = None
```

**Reglas:**
- `is_player = True` → este Host está bajo control del jugador
- Solo puede haber UN Host con `is_player = True` a la vez
- Cuando el Host muere → el Echo busca nuevo NPC compatible → crea nuevo Host con `is_player = True`
- El NPC original se marca como "previous_host" en el genealogy

---

## 4. New Entity: IdeologicalTag → Ideas

Rename `IdeologicalTag` → `Ideas`.

```python
class Ideas(BaseModel):
    """Una doctrina específica. Puede vivir en cualquier entidad."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str           # "concept" | "practice" | "symbol"
    name: str              # "Consenso Horizontal"
    
    # Quién posee esta idea (para tracking depropagación)
    origin_echo_id: str | None = None
    
    # Pesos de esencia — cuáles essencias se asocian con esta idea
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

## 5. Rename: World → Civilization

`World` → `Civilization`. El nombre "World" era demasiado genérico.

```python
class Civilization(BaseModel):
    """Sistema histórico-material. El mundo超大."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unknown Civilization"
    
    # Clock
    clock: WorldClock
    
    # Entidades del mundo
    echoes: list[Echo] = Field(default_factory=list)   # TODOS los Echos (jugador + others)
    factions: list[Faction] = Field(default_factory=list)
    circles: list[Circle] = Field(default_factory=list)
    hosts: list[Host] = Field(default_factory=list)     # NUEVO — todos los hosts activos
    
    # NPCs — base world population
    npcs: list[NPC] = Field(default_factory=list)
    
    # Essencia dominante — la identidad del mundo mismo
    dominant_essence: str = "technocracy"
    
    # Métricas globales
    pressure: float = 30.0
    legitimacy: float = 60.0
    resources_global: float = 70.0
    
    # stability (nuevo)
    stability: float = 50.0
    
    # Infrastructure del mundo
    infrastructure: dict[str, float] = Field(default_factory=dict)
    # e.g. {"food": 60, "energy": 50, "housing": 40}
    
    # Population total
    population: int = 0
    
    # player host id — link directo al host activo
    active_host_id: str | None = None
    
    # Crisis
    crisis_threshold: float = 70.0
    collapse_threshold: float = 30.0
    
    # methods
    def get_active_echo(self) -> Echo | None:
        """Retorna el Echo del jugador (is_player=True)."""
        for h in self.hosts:
            if getattr(h, 'is_player', False):
                for e in self.echoes:
                    if e.id == h.echo_id:
                        return e
        return None
    
    def get_active_host(self) -> Host | None:
        for h in self.hosts:
            if getattr(h, 'is_player', False):
                return h
        return None
    
    def is_crisis(self) -> bool:
        return self.pressure > self.crisis_threshold
    
    def get_echo(self, echo_id: str) -> Echo | None:
        for e in self.echoes:
            if e.id == echo_id:
                return e
        return None
    
    def get_host_for_echo(self, echo_id: str) -> Host | None:
        for h in self.hosts:
            if h.echo_id == echo_id:
                return h
        return None
    
    def evolve_metrics(self, rng) -> dict[str, float]:
        ...
    
    def clamp_metrics(self) -> None:
        ...
```

**Note:** `World.world_core/echoes[]` → `Civilization.echoes[]` donde el primer Echo es el del jugador.

---

## 6. Entity: Manifesto

```python
class Manifesto(BaseModel):
    """Documento doctrinal generado por un Echo."""
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

## 7. Essence — living in multiple layers

Essence vive en:

| Entidad | Campo | Significado |
|---|---|---|
| `Echo` | `genealogical_lineage[-1]` | Identidad profunda del Echo |
| `Host` | heredado via Echo | La doctrina del host |
| `NPC` | `essence` | Identidad del NPC individual |
| `Circle` | `essence` | Doctrina oficial del Círculo |
| `Faction` | `essence` | Doctrina de la facción |
| `Civilization` | `dominant_essence` | Identidad del mundo |

**Migration:**
- Todos los `essence: str` en entidades → se migran normalmente
- El Essence global (anarchism, technocracy, etc.) → se mantiene como string con validator
- Ver spec 44 para `Essence` como Enum cuando seaptime de implementar

---

## 8. NPC — Unchanged interface

NPC queda igual, pero pasa a ser usado como "base body" para Hosts.

```python
class NPC(BaseModel):
    """Individuo normal del mundo. Puede serpromovido a Host."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    essence: str                                     # ← puede ser NULL si no tiene doctrina
    role: str
    archetype: str
    
    # Tracking de si es/era host
    echo_id: str | None = None                      # Si tiene valor → fue host de ese Echo
    faction_id: str | None = None
    
    influence: int
    loyalty: float                                   # Lealtad al factions/circle
```

**Reglas:**
- Cuando un NPC se convierte en Host → se le pone `echo_id` y se crea un `Host` asociado
- Cuando Host muere → el NPC vuelve a "libre" pero puede quedarcon `echo_id` como historical record
- NPCs puedenexisti sin faction_id

---

## 9. Circle — Updated with Ideas

```python
class Circle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    essence: str
    
    # Membresía
    member_ids: list[str] = Field(default_factory=list)  # NPC ids
    echo_ids: list[str] = Field(default_factory=list)      # ECHO ids que están en este circle (si aplica)
    
    # Doctrina
    ideas: list[Ideas] = Field(default_factory=list)       # era ideology_tags: list[str]
    
    founding_tick: int
    influence: float
    institutionalization_level: float = 0.0
    health: float = 100.0
    
    status: CircleStatus
    dormant_turns: int = 0
    history: list[CircleEvent] = Field(default_factory=list)
    
    npcs: list[str] = Field(default_factory=list)          # NPC ids (npcs del juego)
```

**Migration:** `ideology_tags: list[str]` → `ideas: list[Ideas]`
`CircleEvent` también se renombra a algo mássemántico si corresponde.

---

## 10. Faction — Updated with Ideas

```python
class Faction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    essence: str
    
    ideas: list[Ideas] = Field(default_factory=list)       # era ideology_tags
    
    members: list[str] = Field(default_factory=list)        # NPC ids
    circles: list[str] = Field(default_factory=list)         # Circle ids
    
    influence: float
    resources: dict[str, float]
    goals: list[str]
    radicalization: float = 0.0
```

**Migration:** `ideology_tags: list[str]` → `ideas: list[Ideas]`

---

## 11. Migration Map

| Campo | Antes | Después |
|---|---|---|
| `World` | class World | class Civilization |
| `World.echoes` | list[Echo code] | list[Echo canonical] |
| `Echo.code` | essence, attributes, presence, circles | esencia va en genealogical_lineage, sin atributos de cuerpo |
| `NPC.essence` | str | str (sin cambios) |
| `IdeologicalTag` | class IdeologicalTag | class Ideas |
| `Circle.ideology_tags` | list[str] | list[Ideas] |
| `Faction.ideology_tags` | list[str] | list[Ideas] |
| `Echo.known_tags` | list[IdeologicalTag] | list[Ideas] |
| `Echo.manifestos` | list[str] | list[Manifesto] |

---

## 12. Backward Compatibility

**MVP scope — no full rewrite.** Los cambios se hacen en fases:

**Fase 1 — Renombrar:**
- `IdeologicalTag` → `Ideas`
- `World` → `Civilization` (alias `World = Civilization` para no romper imports)

**Fase 2 — Nuevas entidades ligeras:**
- Crear `Echo` (canonical) fuera de entities.py
- Crear `Host` con solo los campos nuevos
- Validar que `World.echoes[]` sigue funcionando

**Fase 3 — Migrar círculos y factions:**
- `Circle.ideology_tags` → `Circle.ideas` con migración automática (string → Ideas trivial)

**Fase 4 —Full Echo/Host split:**
- Crear factory `create_echo()` (canonical Echo)
- Crear factory `create_host()` 
- El código de simulación conecta Echo ↔ Host

**Nota:** `game_core.factory.echo` ya existe. Su `create_echo()` se reusa perocon nuevos campos.

---

## 13. Factory updates

```python
# game_core/factory/
echo.py     → create_echo() — factoryde Echo canonical
host.py     → create_host() — factoryde Host (NPC → Host promotion)
ideas.py   → rename from tags.py → create_ideas_for_essence()
tags.py    → deprecated → import Ideas as alias
manifesto.py → create_manifesto()
```

---

## 14. Orders of migration

1. **Rename IdeologicalTag → Ideas** (trivial, solo import change)
2. **Civilization alias** — `World = Civilization` 
3. **Ideas migration** in Circle, Faction
4. **Expand Echo canonical** — add new fields while keeping old ones (backward compat)
5. **Add Host entity** — separate from NPC
6. **Remove deprecated fields** — post-MVP cleanup
