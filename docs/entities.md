# entities.yaml — ECO Domain Entities Map

Este documento describe las entidades del dominio ECO, sus atributos y relaciones.
Última actualización: 2026-05-27

---

## Entidades Core

### World
Contenedor principal. Gestiona el estado global del juego.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| clock | WorldClock | action_tick, world_tick, historical_tick |
| echoes | list[Echo] | Consciencias persistentes |
| circles | list[Circle] | Grupos de discusión/acción |
| factions | list[Faction] | Grupos políticos |
| manifestos | list[Manifesto] | Textos generados por Echo |
| persons | list[Person] | Individuos (NPC + player) |
| hosts | list[Host] | Contexto de encarnación |
| civs | list[Civ] | Plantillas de civilización |
| population | int | Población total |
| stability | float | Estabilidad 0-100 |
| pressure | float | Tensión social 0-100 |
| legitimacy | float | Legitimidad del liderazgo 0-100 |
| resources | dict | food, infrastructure, energy, knowledge, legitimacy |
| resources_global | float | Recursos globales agregados |
| active_echo_id | str | Echo actualmente encarnado por el jugador |

**Relaciones:**
- World contiene → Echo, Circle, Faction, Manifesto, Person, Host, Civ
- World tiene → Clock (composición)

---

### Echo
**Alma/identidad persistente.** Supervive a las personas, puede reencarnar.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| name | str | Nombre del Echo |
| essence | str | Esencia dominante (thelema, anarchism, etc) |
| essence_profile | EssenceProfile | Perfil completo de esencias |
| phase | EchoPhase | DORMANT, AWAKENED, MANIFEST, PHANTOM |
| genealogical_lineage | list[str] | Historial de esencias ancestrales |
| temporal_strain | float | Degradación por paso del tiempo |
| shadow_coherence | float | Coherencia de identidad 0-100 |
| presence | float | Presencia en el mundo físico 0-100 |
| influence | float | Influencia política 0-100 |
| reincarnation_count | int | Veces que ha reencarnado |
| known_tags | list[Ideas] | Tags/mems conocidos |
| ideas | list[Ideas] | Ideas generadas |
| manifestos | list[str] | IDs de manifestos creados |
| circles | list[str] | IDs de círculos unidos |
| action_history | list[str] | Acciones realizadas |
| last_action_turn | dict | Último turno por acción |

**Relaciones:**
- Echo puede encarnar en → Host (vía echo_id)
- Echo puede author → Manifesto (vía author_echo_id)
- Echo genera → Ideas
- Echo une → Circle (vía circles[])

---

### Person
**Individuo físico en el mundo.** Puede ser NPC o player.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| name | str | Nombre |
| role | str | Rol social |
| archetype | str | Arquetipo (warrior, mystic, etc) |
| type | str | "npc" o "player" |
| echo_id | str | Echo actualmente encarnado |
| civ_id | str | Civilización a la que pertenece |
| essence_profile | EssenceProfile | Perfil de esencias |
| faction_id | str | Facción a la que pertenece |
| loyalty | float | Lealtad a la civilización 0-100 |
| influence | float | Influencia política 0-100 |
| vitality | float | Salud física 0-100 |
| coherence | float | Coherencia mental 0-100 |

**Relaciones:**
- Person puede tener → Echo encarnado (vía echo_id)
- Person pertenece a → Civ (vía civ_id)
- Person pertenece a → Faction (vía faction_id)
- PlayerPerson extiende Person con: will, presence, reincarnation_count, action_history

---

### Host
**Contexto de encarnación.** Vincula Person ↔ Echo. (DEPRECATED - usar PlayerPerson)

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| person_id | str | Person que hostea |
| echo_id | str | Echo encarnado |
| will | float | Voluntad 0-100 |
| presence | float | Presencia física 0-100 |
| action_history | list[str] | Historial de acciones |
| active_circle_id | str | Círculo activo |
| is_active | bool | Si está actualmente encarnado |

**Relaciones:**
- Host vincula → Person (person_id)
- Host vincula → Echo (echo_id)

---

### Faction
**Grupo político.** Agrupa personas con ideología similar.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| name | str | Nombre |
| essence | str | Esencia dominante |
| ideology_tags | list[str] | Tags ideológicos |
| ideas | list[Ideas] | Ideas que maneja la facción |
| members | int | Cantidad de miembros |
| member_ids | list[str] | IDs de persons |
| circle_ids | list[str] | Círculos afiliados |
| influence | float | Influencia política 0-100 |
| resources | dict | Recursos propios |
| goals | list[str] | Objetivos de la facción |
| radicalization | float | Radicalización 0-100 |

**Relaciones:**
- Faction contiene → Person (vía member_ids)
- Faction afiliado a → Circle (vía circle_ids)
- Faction tiene → Ideas

---

### Circle
**Grupo de discusión/acción.** Meio entre ideas y acción.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| name | str | Nombre |
| echo_id | str | Echo fundador |
| essence | str | Esencia del círculo |
| founding_tick | int | Turno de fundación |
| ideology_tags | list[str] | Tags ideológicos |
| ideas | list[Ideas] | Ideas discutidas |
| member_ids | list[str] | IDs de miembros |
| influence | float | Influencia 0-100 |
| institutionalization_level | float | Nivel de institucionalización 0-100 |
| health | float | Salud del círculo 0-100 |
| status | CircleStatus | ACTIVE, DORMANT, SPLINTERED, DISSOLVED |
| history | list[CircleEvent] | Eventos del círculo |
| npcs | list[str] | NPCs del círculo |

**Relaciones:**
- Circle fundado por → Echo (vía echo_id)
- Circle tiene → Person como miembros (vía member_ids)
- Circle discute → Ideas

---

### Manifesto
**Texto generado por un Echo.** Captura ideas de forma persistente.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| author_echo_id | str | Echo autor |
| content | str | Texto del manifiesto |
| tags | list[str] | Tags/mems del manifiesto |
| world_tick_created | int | Turno de creación |
| essence | str | Esencia dominante |
| influence_generated | float | Influencia generada |

**Relaciones:**
- Manifesto authored_by → Echo (vía author_echo_id)
- Manifesto tiene → Tags (Ideas convertidas a strings)

---

### Civ
**Plantilla de civilización.** Define el contexto inicial del juego.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| meta_id | str | ID del template (technocracy, theocracy, etc) |
| name | str | Nombre |
| description | str | Descripción narrativa |
| difficulty | str | Dificultad |
| essence_profile | EssenceProfile | Esencias dominantes |
| population | int | Población inicial |
| stability | float | Estabilidad inicial |
| pressure | float | Presión inicial |
| legitimacy | float | Legitimidad inicial |
| resources_global | float | Recursos iniciales |
| target_aligned_ratio | float | Ratio objetivo de alignment (0.7) |

---

### WorldClock
**Reloj del mundo.**

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| action_tick | int | Contador de acciones |
| world_tick | int | action_tick / 10 |
| historical_tick | int | world_tick / 100 |

---

## Entidades de Soporte

### EssenceProfile
**Perfil de esencias de una entidad.**

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| dominant | list[EssenceScore] | Esencias dominantes (1-3, suma ~100) |
| underlying | list[EssenceScore] | Resto de esencias (0-100) |

### EssenceScore
**Una esencia con peso.**

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| essence | str | ID de esencia |
| value | float | Peso 0-100 |

### Ideas
**Tag/mem.** Versión simplificada de lo que spec-05 llama "Idea".

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | str | UUID |
| category | str | Categoría (e.g. "doctrine", "belief") |
| name | str | Nombre |
| essence_weights | dict[str,float] | Pesos por esencia |

**Relaciones:**
- Ideas usadas por → Echo (known_tags, ideas)
- Ideas usadas por → Faction
- Ideas usadas por → Circle
- Ideas convertidas a → Manifesto tags

---

## Notas sobre spec-05 (Ideas y Doctrinas)

La spec-05 define un sistema más rico que lo actualmente implementado:

**Lo que dice spec-05:**
- Idea: clarity, virality, stability, mutation_risk, origin
- Doctrina: institutionalization, distortion, branches
- Genealogía memética (ancestros/descendientes)
- Ciclo de vida: germinación → expansión → estabilización → mutación → muerte

**Lo que existe actualmente:**
- Ideas: solo id, category, name, essence_weights
- Manifesto: solo id, author_echo_id, content, tags, essence, influence

**Gap:** Esencias (clarity, virality, stability, mutation_risk) y Doctrina (institutionalization, distortion, branches, genealogía) NO están implementadas.

---

## Arquitectura de Relaciones

```
World
├── echoes[] ──────────────── Echo
│   ├── manifestos[] ──────────── Manifesto
│   ├── known_tags[] ─────────── Ideas
│   ├── ideas[] ─────────────── Ideas
│   └── circles[] ──────────── Circle (vía IDs)
│
├── circles[]
│   ├── ideas[]
│   ├── member_ids[] ────────── Person
│   └── echo_ids[] ─────────── Echo
│
├── factions[]
│   ├── ideas[]
│   ├── member_ids[] ────────── Person
│   └── circle_ids[] ────────── Circle
│
├── persons[]
│   ├── type: "npc" ─────────── NPCPerson
│   ├── type: "player" ──────── PlayerPerson (extiende Person)
│   ├── echo_id ─────────────── Echo (encarnación actual)
│   ├── civ_id ──────────────── Civ
│   └── faction_id ──────────── Faction
│
├── hosts[] (DEPRECATED)
│   ├── person_id ───────────── Person
│   └── echo_id ─────────────── Echo
│
└── civs[]
    └── essence_profile ──────── EssenceProfile
```