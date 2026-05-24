# 2. Domain

## 2.1 Entidades principales

```txt
World
 ├── Civilizations
 │    ├── Cities
 │    │    ├── Districts
 │    │    ├── NPCs
 │    │    ├── Factions
 │    │    └── Institutions
 │    └── Dominant Essences
 ├── Ideas
 ├── Doctrines
 ├── Historical Events
 └── Player Echo
```

## 2.2 Estructura de Civilization

```yaml
civilization:
  id: "karax"
  name: "Nodo Libre Kárax"
  essences:
    anarchism: 65
    technocracy: 35
    absurdism: 20
  economy:
    food: 62
    infrastructure: 48
    energy: 71
    housing: 39
    logistics: 52
    inequality: 67
    production: 58
    stability: 44
```

Una civilización no tiene una sola esencia. Tiene mezcla. Esto permite sociedades contradictorias:

```txt
Anarquismo federado + facciones tecnocráticas + cultos absurdistas.
```

## 2.3 Estructura de City

```yaml
city:
  id: "karax_city"
  civilization_id: "karax"
  name: "Kárax"
  districts:
    - id: "open_labs_east"
      name: "Laboratorios Abiertos del Este"
      type: "laboratory"
    - id: "old_quarter"
      name: "Barrio Antiguo"
      type: "residential"
    - id: "underground_market"
      name: "Mercado Subterráneo"
      type: "market"
  npcs:
    - id: "npc_maela_ruun"
    - id: "npc_kell_vorren"
    - id: "npc_saira_vel"
  factions:
    - id: "protocolos_autonomos"
    - id: "circulo_sabedores"
```

## 2.4 Estructura de District

```yaml
district:
  id: "open_labs_east"
  city_id: "karax"
  name: "Laboratorios Abiertos del Este"
  type: "laboratory"
  mood_tags:
    - "tense"
    - "experimental"
    - "cold"
  danger_level: 71
  visual_tags:
    - "industrial"
    - "underground"
    - "experimental"
  tension: 78
```

## 2.5 Estructura de NPC

```yaml
npc:
  id: "npc_maela_ruun"
  name: "Dra. Maela Ruun"
  role: "investigadora tecnócrata disidente"
  archetype: "scientist"
  location_id: "open_labs_east"
  age: 31
  faction_tags:
    - "technocratic"
    - "dissident"
  mood_tags:
    - "paranoid"
    - "focused"
  attitude:
    trust: 31
    hostility: 18
    curiosity: 76
  access:
    - "archives"
    - "technical_networks"
  limitations:
    - "no_military_access"
    - "surveillance_risk"
```

## 2.6 Estructura de Institution

```yaml
institution:
  id: "archivo_karax"
  name: "Archivo Distribuido de Kárax"
  type: "archive"
  city_id: "karax"
  district_id: "old_quarter"
  faction_id: "protocolos_autonomos"
  doctrines:
    - "protocolos_autonomos"
  institutionalization: 62
  distortion: 31
  upkeep:
    infrastructure: 5
    energy: 3
    social_trust: 8
  branches:
    - "rama_libertaria"
    - "rama_algoritmica"
```

## 2.7 Estructura de Historical Event

```json
{
  "event_id": "evt_000442",
  "turn": 47,
  "year": 47,
  "type": "IdeaImplanted",
  "actor": "player_echo",
  "target": "npc_maela_ruun",
  "payload": {
    "idea_id": "idea_collective_will_calculation"
  }
}
```

## 2.8 Constraints y validación

```yaml
entity_constraints:
  essence_value: "0-100"
  entity_id_format: "^[a-z0-9_]+$"
  year_format: "integer >= 0"
  turn_format: "integer >= 0"

required_fields_by_entity_type:
  civilization:
    - id
    - name
    - essences
  city:
    - id
    - name
    - civilization_id
  district:
    - id
    - name
    - city_id
    - type
  npc:
    - id
    - name
    - location_id
  faction:
    - id
    - doctrines
    - goals
  institution:
    - id
    - type
    - city_id
  idea:
    - id
    - name
    - essences
  doctrine:
    - id
    - name
    - source_ideas

validation_rules:
  - "essence percentages per civilization sum may exceed 100 (intentional for tension)"
  - "city must reference valid civilization_id"
  - "district must reference valid city_id"
  - "npc must reference valid location_id"
  - "faction doctrines must reference valid doctrine ids"
```

---

## Metadata

- Origen: sección 5.1 del spec.md original
- Dependencias: 01-architecture.md
- Notas: agregada sección 2.8 (Constraints y validación)
- Estado: 🔄 En desarrollo