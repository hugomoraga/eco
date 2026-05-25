# SPEC-46: World Generation — Civilization Templates + Person Dataset

**Estado:** draft
**Creado:** 2026-05-24
**Última actualización:** 2026-05-24
**Dependencias:** 01, 02, 03, 19, 28, 30, 43, 47
**Reemplaza:** parcial de 02-domain (inicialización de World)

---

## концепт

El juego ECO se inicia desde un **Template de Civilización** — no desde valores hardcodeados.

Un Template define:
- La **Civilización** completa (parámetros de World)
- El **Host inicial** (Echo encarnado, con su Person tipo "player")
- **Persons pre-generadas** (NPCs, con nombres, roles, esencias, stats)
- **Condiciones de dificultad** (modificadores narrativos)
- **Reglas especiales** (si aplica)

Esto permite escenarios radicalmente distintos:
- Civ anarquista con Host=thelema → partida difícil
- Civ teocrática con Host=atheism radical → partida difícil
- Civ en colapso con Host=mysticism → oportunidades

Los Templates son **datasets editables** — el jugador puede modificar YAML o generar nuevos con IA.

---

## Modelo de Esencias (spec-47)

Este spec usa el modelo EssenceProfile de spec-47:

```python
class EssenceScore:
    essence: str   # ID de esencia (thelema, anarchism, etc.)
    value: int     # 0-100

class EssenceProfile:
    dominant: List[EssenceScore]    # 1-3 esencias, suma ~100
    underlying: List[EssenceScore]  # resto, 0-100 c/u
```

**Las 20 essencias:** thelema, monoteism, polytheism, animism, atheism, absurdism, nihilism, existentialism, humanism, pragmatism, ecology, technocracy, anarchism, feudalism, socialism, capitalism, mysticism, rationalism, romanticism, stoicism

**Compatibilidad Civ vs Person:** target 70% alineados, 30% disidentes.

---

## 1. Arquitectura de Template

### Ubicación

```
eco/
├── game_core/
│   └── data/
│       ├── templates/           # Civilization templates
│       │   ├── default.yaml
│       │   ├── anarchist_utopia.yaml
│       │   ├── dark_ages.yaml
│       │   ├── theocracy.yaml
│       │   ├── technocracy.yaml
│       │   └── ...             # más según se añadigan
│       │
│       └── persons/            # Person dataset
│           ├── archetypes/      # NPCs por arquetipo
│           │   ├── prophets.yaml
│           │   ├── merchants.yaml
│           │   ├── warriors.yaml
│           │   └── ...
│           ├── essences/        # NPCs por esencia
│           │   ├── anarchists.yaml
│           │   ├── socialists.yaml
│           │   ├── nationalists.yaml
│           │   └── ...
│           └── mixed/           # datasets combinados (generados con IA)
│               ├── balanced.yaml
│               └── radical.yaml
```

### Jerarquía de Carga

```
load_template(name):
  1. Busca en game_core/data/templates/{name}.yaml
  2. Si no existe, busca en game_core/data/templates/default.yaml
  3. Combina con defaults hardcoded del sistema
  4. Genera Persons según dataset referenced
  5. Crea World + Host + Persons
```

---

## 2. Template YAML — Estructura Completa

```yaml
# template: anarchist_utopia.yaml
# Description: An anarchist civilization where the Host is a cleric — difficult start

meta:
  id: "anarchist_utopia_v1"
  name: "Anarchist Utopia"
  description: |
    A stateless society built on mutual aid. The Host, a wandering cleric,
    must navigate a world that views institutional religion with suspicion.
  difficulty: "hard"           # easy | normal | hard | extreme
  tags: ["anarchism", "secular", "collective"]

# ─── Civilization (World) ───────────────────────────────────────────────

civilization:
  population: 15000
  stability: 65.0               # fairly stable
  pressure: 20.0                # low unrest
  legitimacy: 40.0               # authority is contested
  resources_global: 75.0
  crisis_threshold: 70.0
  collapse_threshold: 20.0
  resources:
    food: 90
    infrastructure: 70
    energy: 60
    knowledge: 85               # high knowledge (free thinkers)
    legitimacy: 40

# ─── Host / Echo ─────────────────────────────────────────────────────────

host:
  # Person que será el jugador
  person:
    id: "player_001"
    name: "Brother Marcus"
    essence: "theocracy"         # contrasta con la civ
    role: "cleric"
    archetype: "priest"
    type: "player"              # siempre "player"
    vitality: 90.0
    coherence: 70.0
    influence: 15.0
    loyalty: 30.0               # bajo — no confían en clérigos

  # Echo del Host
  echo:
    name: "The Wandering Shepherd"
    essence: "theocracy"         # su esencia real
    phase: "awakened"            # dormant | awakening | awakened | fragmented
    genealogical_lineage: ["theocracy"]

    # Atributos del Echo
    attributes:
      - label: "clarity"
        value: 55
      - label: "influence_range"
        value: 30
      - label: "temporal_strain"
        value: 20

    # Tags/Ideas iniciales
    ideas:
      - category: "doctrine"
        name: "Divine Order"
        essence_weights: {"theocracy": 1.0}
      - category: "practice"
        name: "Ritual Purity"
        essence_weights: {"theocracy": 0.7, "asceticism": 0.3}

# ─── Pre-generated Persons (NPCs) ───────────────────────────────────────

persons:
  # Cada Person tiene id único que se puede referencing en eventos
  - id: "npc_001"
    name: "Comrade Yelena"
    essence: "anarchism"
    role: "agitator"
    archetype: "orator"
    type: "npc"
    vitality: 85.0
    coherence: 65.0
    influence: 40.0
    loyalty: 80.0
    faction_id: "circle_001"     # referencia al círculo que se crea abajo

  - id: "npc_002"
    name: "Engineer Petrov"
    essence: "technocracy"
    role: "engineer"
    archetype: "scholar"
    type: "npc"
    vitality: 70.0
    coherence: 80.0
    influence: 30.0
    loyalty: 60.0
    faction_id: null

  - id: "npc_003"
    name: "Sister Catherine"
    essence: "theocracy"
    role: "cleric"
    archetype: "priest"
    type: "npc"
    vitality: 95.0
    coherence: 50.0
    influence: 25.0
    loyalty: 90.0
    faction_id: null
    # Catherine es ally del Host — misma esencia

  - id: "npc_004"
    name: "Radical Tomás"
    essence: "syndicalism"
    role: "union_leader"
    archetype: "warrior"
    type: "npc"
    vitality: 80.0
    coherence: 55.0
    influence: 50.0
    loyalty: 70.0

  - id: "npc_005"
    name: "Diplomat Wei"
    essence: "confucianism"
    role: "mediator"
    archetype: "scholar"
    type: "npc"
    vitality: 75.0
    coherence: 85.0
    influence: 35.0
    loyalty: 55.0

# ─── Pre-generated Circles ───────────────────────────────────────────────

circles:
  - id: "circle_001"
    name: "Circle of Mutual Aid"
    essence: "anarchism"
    founding_tick: 0
    influence: 45.0
    institutionalization_level: 20.0
    health: 100.0
    member_ids: ["npc_001"]
    echo_ids: []
    ideas:
      - category: "practice"
        name: "Mutual Aid"
        essence_weights: {"anarchism": 1.0}

# ─── Pre-generated Factions ─────────────────────────────────────────────

factions:
  - id: "faction_001"
    name: "The Assembly"
    essence: "anarchism"
    members: 5
    influence: 35.0
    radicalization: 30.0
    ideas:
      - category: "governance"
        name: "Direct Democracy"
        essence_weights: {"anarchism": 0.8, "syndicalism": 0.2}

# ─── Special Rules (optional) ───────────────────────────────────────────

special_rules:
  # El Host tiene -20 de loyalty en esta civ
  - type: "host_modifier"
    target: "loyalty"
    modifier: -20
    reason: "Clerics are viewed with suspicion in anarchist societies"

  # La civ tiene affinity +30 con anarchism
  - type: "civ_essence_modifier"
    target: "anarchism"
    modifier: +30
    reason: "Civilization is built on anarchist principles"

  # Los NPCs con essence=theocracy tienen +15 de influence
  - type: "npc_essence_bonus"
    target_essence: "theocracy"
    target_field: "influence"
    modifier: +15
    reason: "Religious figures carry moral authority even in secular societies"
```

---

## 3. Templates Incluidos

### default.yaml

```yaml
meta:
  id: "default_v1"
  name: "Standard Civilization"
  description: "A balanced civilization with moderate stats. Host is a wandering philosopher."
  difficulty: "normal"
  tags: ["balanced", "philosophy"]

civilization:
  population: 10000
  stability: 50.0
  pressure: 30.0
  legitimacy: 60.0
  resources_global: 70.0
  crisis_threshold: 75.0
  collapse_threshold: 15.0
  resources:
    food: 80
    infrastructure: 60
    energy: 50
    knowledge: 50
    legitimacy: 60

host:
  person:
    id: "player_001"
    name: "The Wanderer"
    essence: "philosophy"
    role: "philosopher"
    archetype: "scholar"
    type: "player"
    vitality: 80.0
    coherence: 75.0
    influence: 20.0
    loyalty: 50.0
  echo:
    name: "Seeker of Truth"
    essence: "philosophy"
    phase: "awakened"
    genealogical_lineage: ["philosophy"]
    attributes:
      - label: "clarity"
        value: 60
      - label: "influence_range"
        value: 40
    ideas: []

persons:
  - id: "npc_001"
    name: "Teacher Maria"
    essence: "pedagogy"
    role: "teacher"
    archetype: "scholar"
    type: "npc"
    vitality: 75.0
    coherence: 70.0
    influence: 25.0
    loyalty: 65.0

  - id: "npc_002"
    name: "Guard Captain Ivan"
    essence: "stoicism"
    role: "soldier"
    archetype: "warrior"
    type: "npc"
    vitality: 95.0
    coherence: 60.0
    influence: 35.0
    loyalty: 75.0

circles: []
factions: []

special_rules: []
```

### anarchist_utopia.yaml

```yaml
# Ver ejemplo completo arriba — Host=clerigo en civ anarquista
# Difficulty: hard
```

### dark_ages.yaml

```yaml
meta:
  id: "dark_ages_v1"
  name: "Dark Ages"
  description: "A civilization in collapse. Low legitimacy, high unrest, scarce resources."
  difficulty: "extreme"
  tags: ["crisis", "collapse", "survival"]

civilization:
  population: 5000
  stability: 25.0
  pressure: 75.0
  legitimacy: 15.0
  resources_global: 30.0
  crisis_threshold: 60.0
  collapse_threshold: 25.0
  resources:
    food: 30
    infrastructure: 20
    energy: 15
    knowledge: 10
    legitimacy: 15

host:
  person:
    id: "player_001"
    name: "Survivor Ana"
    essence: "nihilism"
    role: "survivor"
    archetype: "warrior"
    type: "player"
    vitality: 60.0
    coherence: 40.0
    influence: 10.0
    loyalty: 50.0

  echo:
    name: "The Resilient"
    essence: "nihilism"
    phase: "awakening"
    genealogical_lineage: []
    attributes:
      - label: "clarity"
        value: 35
      - label: "influence_range"
        value: 20
      - label: "temporal_strain"
        value: 50
    ideas: []

persons:
  - id: "npc_001"
    name: "Desperate Ravi"
    essence: "desperation"
    role: "outlaw"
    archetype: "warrior"
    type: "npc"
    vitality: 70.0
    coherence: 30.0
    influence: 45.0
    loyalty: 20.0

  - id: "npc_002"
    name: "Healer Old Mei"
    essence: "stoicism"
    role: "healer"
    archetype: "scholar"
    type: "npc"
    vitality: 50.0
    coherence: 85.0
    influence: 30.0
    loyalty: 80.0

circles: []
factions: []

special_rules:
  - type: "civ_essence_modifier"
    target: "nihilism"
    modifier: +40
    reason: "Society has lost meaning — nihilism spreads"
```

### theocracy.yaml

```yaml
meta:
  id: "theocracy_v1"
  name: "Divine Mandate"
  description: "A rigid theocratic state. Host is a secular intellectual — not welcome."
  difficulty: "hard"
  tags: ["theocracy", "religion", "hierarchy"]

civilization:
  population: 12000
  stability: 55.0
  pressure: 45.0
  legitimacy: 85.0
  resources_global: 60.0
  crisis_threshold: 80.0
  collapse_threshold: 30.0
  resources:
    food: 70
    infrastructure: 75
    energy: 55
    knowledge: 40
    legitimacy: 85

host:
  person:
    id: "player_001"
    name: "Scholar Lin"
    essence: "rationalism"
    role: "scholar"
    archetype: "scholar"
    type: "player"
    vitality: 75.0
    coherence: 60.0
    influence: 15.0
    loyalty: 20.0              # low — they don't trust rationalists

  echo:
    name: "The Questioner"
    essence: "rationalism"
    phase: "awakened"
    genealogical_lineage: ["rationalism"]
    attributes:
      - label: "clarity"
        value: 70
      - label: "influence_range"
        value: 25
    ideas: []

persons:
  - id: "npc_001"
    name: "High Priestess Amara"
    essence: "theocracy"
    role: "priestess"
    archetype: "priest"
    type: "npc"
    vitality: 90.0
    coherence: 80.0
    influence: 55.0
    loyalty: 95.0
    faction_id: "faction_clergy"

  - id: "npc_002"
    name: "Inquisitor Bruno"
    essence: "theocracy"
    role: "inquisitor"
    archetype: "warrior"
    type: "npc"
    vitality: 85.0
    coherence: 70.0
    influence: 40.0
    loyalty: 90.0

circles: []
factions:
  - id: "faction_clergy"
    name: "The Holy Order"
    essence: "theocracy"
    members: 12
    influence: 60.0
    radicalization: 20.0

special_rules:
  - type: "host_modifier"
    target: "loyalty"
    modifier: -30
    reason: "Rationalists are viewed as heretics in the Holy Mandate"
```

### technocracy.yaml

```yaml
meta:
  id: "technocracy_v1"
  name: "Machine Council"
  description: "A technocratic society governed by engineers and scientists."
  difficulty: "medium"
  tags: ["technocracy", "science", "order"]

civilization:
  population: 18000
  stability: 75.0
  pressure: 15.0
  legitimacy: 70.0
  resources_global: 85.0
  crisis_threshold: 85.0
  collapse_threshold: 25.0
  resources:
    food: 80
    infrastructure: 95
    energy: 90
    knowledge: 95
    legitimacy: 70

host:
  person:
    id: "player_001"
    name: "Worker Ji"
    essence: "syndicalism"
    role: "worker"
    archetype: "warrior"
    type: "player"
    vitality: 85.0
    coherence: 65.0
    influence: 20.0
    loyalty: 60.0

  echo:
    name: "The Organized"
    essence: "syndicalism"
    phase: "awakened"
    genealogical_lineage: ["syndicalism"]
    attributes:
      - label: "clarity"
        value: 50
      - label: "influence_range"
        value: 35
    ideas: []

persons:
  - id: "npc_001"
    name: "Chief Engineer Yuki"
    essence: "technocracy"
    role: "engineer"
    archetype: "scholar"
    type: "npc"
    vitality: 70.0
    coherence: 90.0
    influence: 50.0
    loyalty: 85.0

  - id: "npc_002"
    name: "Union Rep Chen"
    essence: "syndicalism"
    role: "union_representative"
    archetype: "orator"
    type: "npc"
    vitality: 80.0
    coherence: 70.0
    influence: 45.0
    loyalty: 80.0

circles:
  - id: "circle_workers"
    name: "Workers Collective"
    essence: "syndicalism"
    influence: 30.0

factions:
  - id: "faction_engineers"
    name: "The Machine Guild"
    essence: "technocracy"
    members: 8
    influence: 55.0

special_rules:
  - type: "civ_essence_modifier"
    target: "technocracy"
    modifier: +40
    reason: "Technocratic values dominate society"
```

---

## 2. Person Dataset — Estructura

### 2.1 EssenceProfile en Persons

```python
class EssenceScore:
    essence: str   # thelema, monoteism, anarchism, etc.
    value: int      # 0-100

class EssenceProfile:
    dominant: List[EssenceScore]    # 1-3 esencias, suma ~100
    underlying: List[EssenceScore]  # resto, 0-100 c/u
```

### 2.2 Dataset YAML

```yaml
# dataset: archetype
# Generado por IA — 20 personas por archivo

meta:
  dataset_type: "archetype"    # archetype | mixed
  archetype: "warrior"
  count: 20

persons:
  - id: "arch_warrior_001"
    name: "Kira Volkov"
    archetype_tags: [warrior, protector]
    essence:
      dominant:
        - essence: "feudalism"
          value: 60
        - essence: "stoicism"
          value: 35
      underlying:
        - essence: "monoteism"
          value: 15
        - essence: "anarchism"
          value: 5
        - essence: "capitalism"
          value: 0
    loyalty: 75
    tags: [martial, disciplined, loyal]

  - id: "arch_warrior_002"
    name: "Sven Ironhand"
    archetype_tags: [warrior, mercenary]
    essence:
      dominant:
        - essence: "capitalism"
          value: 55
        - essence: "pragmatism"
          value: 40
      underlying:
        - essence: "anarchism"
          value: 20
        - essence: "feudalism"
          value: 10
    loyalty: 45
    tags: [opportunistic, skilled, mercenary]
```

### 2.3 Estructura de Archivos

```
data/world/persons/
├── archetypes/
│   ├── warrior.yaml      # 20 warriors
│   ├── mystic.yaml       # 20 mystics
│   ├── merchant.yaml     # 20 merchants
│   ├── scholar.yaml      # 20 scholars
│   ├── artist.yaml       # 20 artists
│   ├── artisan.yaml      # 20 artisans
│   ├── wanderer.yaml     # 20 wanderers
│   └── leader.yaml      # 20 leaders
│
├── mixed/
│   ├── revolutionary.yaml   # 20 disidentes, loyalty baja
│   └── establishment.yaml  # 20 aligned, loyalty alta
│
└── essences/                 # opcional: por esencia dominante
    ├── thelema.yaml
    ├── monoteism.yaml
    └── ...                  # puede no necesitarse si dominant covers
```

### 2.4 Distribución de Escalones

Cada archivo tiene 20 personas divididas en:

| Escalón | Dominant | Loyalty | Count |
|---------|----------|---------|-------|
| bajo | essence total 5-15 | 20-50 | 5 |
| medio | essence total 15-30 | 50-70 | 5 |
| alto | essence total 30-50 | 70-90 | 5 |
| elite | essence total 50-80 | 90-100 | 5 |

---

## 5. Carga de Template — API

### game_core/factory/template.py

```python
from dataclasses import dataclass, field
from typing import Literal

import yaml
from pathlib import Path

@dataclass
class TemplateMetadata:
    id: str
    name: str
    description: str
    difficulty: Literal["easy", "normal", "hard", "extreme"]
    tags: list[str] = field(default_factory=list)

@dataclass
class CivilizationConfig:
    population: int
    stability: float
    pressure: float
    legitimacy: float
    resources_global: float
    crisis_threshold: float
    collapse_threshold: float
    resources: dict[str, float]

@dataclass
class HostConfig:
    person: dict
    echo: dict

@dataclass
class SpecialRule:
    type: Literal["host_modifier", "civ_essence_modifier", "npc_essence_bonus"]
    target: str
    modifier: float
    reason: str

@dataclass
class Template:
    meta: TemplateMetadata
    civilization: CivilizationConfig
    host: HostConfig
    persons: list[dict]
    circles: list[dict] = field(default_factory=list)
    factions: list[dict] = field(default_factory=list)
    special_rules: list[SpecialRule] = field(default_factory=list)

    @classmethod
    def load(cls, name: str) -> "Template":
        """
        Carga un template por nombre.
        Busca en game_core/data/templates/{name}.yaml
        Si no existe, usa default.yaml
        """
        template_dir = Path(__file__).parent.parent / "data" / "templates"
        path = template_dir / f"{name}.yaml"

        if not path.exists():
            path = template_dir / "default.yaml"

        with open(path) as f:
            data = yaml.safe_load(f)

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "Template":
        meta = TemplateMetadata(**data["meta"])
        civ = CivilizationConfig(**data["civilization"])
        host = HostConfig(**data["host"])
        persons = data.get("persons", [])
        circles = data.get("circles", [])
        factions = data.get("factions", [])
        special_rules = [SpecialRule(**r) for r in data.get("special_rules", [])]

        return cls(meta, civ, host, persons, circles, factions, special_rules)
```

### game_core/factory/world_builder.py

```python
from game_core.domain.entities import (
    World, WorldClock, Person, Host, Echo,
    Circle, Faction, Ideas, EchoAttribute
)
from game_core.factory.template import Template, SpecialRule
from game_core.factory.echo import create_echo
from game_core.factory.host import create_host
from game_core.factory.npc import create_npc, create_npcs
from game_core.factory.circle import create_circle
from game_core.factory.faction import create_faction
from game_core.factory.tags import create_ideas_for_essence

def build_world_from_template(template: Template, rng=None) -> World:
    """
    Construye un World completo desde un Template.
    Aplica special_rules durante la construcción.
    """
    rng = rng or random.Random()

    # ─── 1. Crear World base ──────────────────────────────────────────

    world = World(
        clock=WorldClock(),
        population=template.civilization.population,
        stability=template.civilization.stability,
        pressure=template.civilization.pressure,
        legitimacy=template.civilization.legitimacy,
        resources_global=template.civilization.resources_global,
        crisis_threshold=template.civilization.crisis_threshold,
        collapse_threshold=template.civilization.collapse_threshold,
        resources=template.civilization.resources.copy(),
        echoes=[],
        circles=[],
        factions=[],
        manifestos=[],
        persons=[],
        hosts=[],
    )

    # ─── 2. Crear Host (Person + Echo + Host) ──────────────────────────

    host_cfg = template.host

    # Person del host
    person_data = host_cfg["person"]
    host_person = Person(
        id=person_data["id"],
        name=person_data["name"],
        essence=person_data["essence"],
        role=person_data["role"],
        archetype=person_data["archetype"],
        type="player",
        vitality=person_data["vitality"],
        coherence=person_data["coherence"],
        influence=person_data["influence"],
        loyalty=person_data["loyalty"],
    )
    world.persons.append(host_person)

    # Echo del host
    echo_data = host_cfg["echo"]
    host_echo = create_echo(
        name=echo_data["name"],
        essence=echo_data["essence"],
        phase=echo_data.get("phase", "dormant"),
    )
    # Lineage
    if echo_data.get("genealogical_lineage"):
        host_echo.genealogical_lineage = echo_data["genealogical_lineage"]
    # Attributes
    for attr in echo_data.get("attributes", []):
        host_echo.attributes.append(EchoAttribute(**attr))
    # Ideas
    for idea_data in echo_data.get("ideas", []):
        host_echo.ideas.append(Ideas(**idea_data))

    world.echoes.append(host_echo)
    world.active_echo_id = host_echo.id

    # Host linking
    host_link = create_host(
        person_id=host_person.id,
        echo_id=host_echo.id,
        will=50.0,
        presence=50.0,
    )
    world.hosts.append(host_link)

    # ─── 3. Crear NPCs (Persons pre-generadas del template) ───────────

    for npc_data in template.persons:
        npc = Person(
            id=npc_data["id"],
            name=npc_data["name"],
            essence=npc_data["essence"],
            role=npc_data["role"],
            archetype=npc_data["archetype"],
            type="npc",
            vitality=npc_data["vitality"],
            coherence=npc_data["coherence"],
            influence=npc_data["influence"],
            loyalty=npc_data["loyalty"],
            faction_id=npc_data.get("faction_id"),
        )
        world.persons.append(npc)

        # Crear Host para NPC (para que tenga agency)
        npc_host = create_host(
            person_id=npc.id,
            echo_id=None,  # NPC sin Echo hasta que evoluciones
            will=40.0,
            presence=30.0,
        )
        npc_host.is_active = True
        world.hosts.append(npc_host)

    # ─── 4. Crear Circles ─────────────────────────────────────────────

    for circle_data in template.circles:
        ideas = [Ideas(**i) for i in circle_data.get("ideas", [])]
        circle = create_circle(
            name=circle_data["name"],
            essence=circle_data["essence"],
            founding_tick=circle_data.get("founding_tick", 0),
            ideas=ideas,
        )
        circle.id = circle_data["id"]
        circle.influence = circle_data.get("influence", 10.0)
        circle.institutionalization_level = circle_data.get("institutionalization_level", 0.0)
        circle.health = circle_data.get("health", 100.0)
        circle.member_ids = circle_data.get("member_ids", [])
        circle.echo_ids = circle_data.get("echo_ids", [])
        world.circles.append(circle)

    # ─── 5. Crear Factions ─────────────────────────────────────────────

    for faction_data in template.factions:
        ideas = [Ideas(**i) for i in faction_data.get("ideas", [])]
        faction = create_faction(
            name=faction_data["name"],
            essence=faction_data["essence"],
            ideas=ideas,
        )
        faction.id = faction_data["id"]
        faction.members = faction_data.get("members", 0)
        faction.influence = faction_data.get("influence", 10.0)
        faction.radicalization = faction_data.get("radicalization", 0.0)
        world.factions.append(faction)

    # ─── 6. Aplicar Special Rules ────────────────────────────────────

    for rule in template.special_rules:
        _apply_special_rule(world, rule)

    return world


def _apply_special_rule(world: World, rule: SpecialRule) -> None:
    """Aplica una regla especial al world."""
    if rule.type == "host_modifier":
        # Modificar un campo del host (person del player)
        player_person = world.get_player_person()
        if player_person and hasattr(player_person, rule.target):
            current = getattr(player_person, rule.target)
            setattr(player_person, rule.target, current + rule.modifier)

    elif rule.type == "civ_essence_modifier":
        # Los persons con esa esencia ganan influence
        for person in world.persons:
            if person.essence == rule.target and person.type == "npc":
                person.influence += rule.modifier

    elif rule.type == "npc_essence_bonus":
        # Los NPCs con cierta esencia ganan bonus en target_field
        for person in world.persons:
            if person.essence == rule.target and person.type == "npc":
                current = getattr(person, rule.target_field, 0)
                setattr(person, rule.target_field, current + rule.modifier)
```

---

## 6. Integración con SimulationEngine

```python
# game_core/systems/simulation.py — modificado

class SimulationEngine:
    def __init__(
        self,
        seed: int = 42,
        max_turns: int = 999,
        template_name: str = "default",   # NUEVO
        # ... resto de args
    ):
        # ... otros init
        self.template_name = template_name
        self.world = self._init_world()

    def _init_world(self) -> World:
        if self.template_name:
            template = Template.load(self.template_name)
            return build_world_from_template(template, rng=self.rng)
        else:
            # Fallback: crear world básico
            return World(clock=WorldClock())
```

```bash
# Uso
uv run python game_core/run.py --template anarchist_utopia --turns 50
uv run python game_core/run.py --template dark_ages --autoplay
uv run python game_core/run.py --template theocracy --ai minimax
```

---

## 7. Dataset de Personas — Generación

### Proceso de Generación

1. **Definir categorías**: archetypes/ + essences/
2. **Generar con IA**: 20 personas por archivo, prompts temáticos
3. **Validar YAML**: cada archivo parsea correctamente
4. **Testear en simulación**: cargar un template que use el dataset
5. **Refinar**: ajustar stats según feedback

### Archivos a Generar

```
game_core/data/templates/
├── default.yaml           # ✅ manual (ya existe en specs, migrar)
├── anarchist_utopia.yaml # ✅ manual
├── dark_ages.yaml         # ✅ manual
├── theocracy.yaml        # ✅ manual
└── technocracy.yaml      # ✅ manual

game_core/data/persons/archetypes/
├── prophets.yaml         # 🤖 AI → 20 chars carismáticos/idealistas
├── merchants.yaml        # 🤖 AI → 20 chars pragmáticos/negociadores
├── warriors.yaml         # 🤖 AI → 20 chars protectores/soldados
├── scholars.yaml         # 🤖 AI → 20 chars académicos/investigadores
├── priests.yaml          # 🤖 AI → 20 chars clérigos/místicos
├── outlaws.yaml          # 🤖 AI → 20 chars revolucionarios/fuera de ley
├── diplomats.yaml        # 🤖 AI → 20 chars mediadores/diplomáticos
└── healers.yaml          # 🤖 AI → 20 chars sanadores/compasivos

game_core/data/persons/essences/
├── anarchists.yaml       # 🤖 AI → 20 persons essence=anarchism
├── socialists.yaml       # 🤖 AI → 20 persons essence=socialism
├── nationalists.yaml     # 🤖 AI → 20 persons essence=nationalism
├── theocracy.yaml        # 🤖 AI → 20 persons essence=theocracy
├── technocracy.yaml      # 🤖 AI → 20 persons essence=technocracy
├── syndicalism.yaml      # 🤖 AI → 20 persons essence=syndicalism
├── philosophy.yaml       # 🤖 AI → 20 persons essence=philosophy
├── rationalism.yaml      # 🤖 AI → 20 persons essence=rationalism
├── stoicism.yaml         # 🤖 AI → 20 persons essence=stoicism
├── nihilism.yaml         # 🤖 AI → 20 persons essence=nihilism
├── confucianism.yaml     # 🤖 AI → 20 persons essence=confucianism
└── fascism.yaml          # 🤖 AI → 20 persons essence=fascism

game_core/data/persons/mixed/
├── balanced.yaml         # 🤖 AI → mezcla diversa
└── radical.yaml          # 🤖 AI → personas extremas
```

### Formato AI para Dataset

```yaml
# Generated by AI — archetype: prophets
# Prompt: Genera 20 prophets para la civilización anarquista

meta:
  generated: "2026-05-24"
  generator: "MiniMax v2"
  archetype: "prophets"
  essence: "anarchism"
  count: 20

persons:
  - id: "ai_prophet_001"
    name: "The Unbound Voice"
    essence: "anarchism"
    role: "agitator"
    archetype: "prophet"
    vitality: 85
    coherence: 60
    influence: 45
    loyalty: 80
    tags: ["charismatic", "martyr", "popular"]

  - id: "ai_prophet_002"
    name: "Silent Thunder"
    essence: "anarchism"
    role: "orator"
    archetype: "prophet"
    vitality: 90
    coherence: 55
    influence: 50
    loyalty: 75
    tags: ["intense", "transformative", "feared"]

  # ... 18 más
```

---

## 8. Nomenclatura de IDs

| Prefix | Tipo | Ejemplo |
|--------|------|---------|
| `player_001` | Host (Person player) | player_001 |
| `npc_XXX` | NPC manual del template | npc_001, npc_002 |
| `ai_prophet_XXX` | NPC generado por IA (archetype) | ai_prophet_001 |
| `ai_anarchist_XXX` | NPC generado por IA (essence) | ai_anarchist_001 |
| `dataset_XXX` | Person del dataset (mixed) | dataset_prophet_001 |
| `circle_XXX` | Circle | circle_001 |
| `faction_XXX` | Faction | faction_001 |

---

## 9. Estados de Implementación

| Item | Estado | Prioridad |
|------|--------|----------|
| `game_core/factory/template.py` — Template loader | ❌ Falta | alta |
| `game_core/factory/world_builder.py` — Build world from template | ❌ Falta | alta |
| Templates: default, anarchist_utopia, dark_ages, theocracy, technocracy | ✅ Spec | media |
| `game_core/data/templates/` + YAML files | ❌ Falta directorio | alta |
| Person dataset: archetypes/ (8 archivos) | ❌ Falta generar con IA | media |
| Person dataset: essences/ (12 archivos) | ❌ Falta generar con IA | media |
| Person dataset: mixed/ (2 archivos) | ❌ Falta generar con IA | baja |
| Integración con SimulationEngine (--template flag) | ❌ Falta | alta |
| Tests de carga de template | ❌ Falta | media |

---

## Status History

- 2026-05-24: created — draft

---

## Metadata

- Creado: 2026-05-24
- Última actualización: 2026-05-24
- Dependencias: 01, 02, 03, 19, 28, 30, 43
- Reemplaza: parcial de 02-domain (inicialización de World)
- Status: draft