# 14. Godot Contract

## 14.1 Visión

Separación estricta entre engine y cliente visual. El engine modela significado, causalidad, relaciones, historia. Godot modela percepción, estética, presentación, experiencia sensorial.

## 14.2 Principio fundamental

El engine describe "qué es". Godot decide "cómo se ve".

**El engine NO conoce:** sprites, shaders, tilemaps, escenas Godot, VFX, assets específicos.

## 14.3 Snapshots genéricos

El engine exporta estado semántico abstracto:

```json
{
  "meta": {
    "schema_version": "0.2.0",
    "seed": 42,
    "turn": 14,
    "year": 47,
    "current_date": "Año 47, Día 284"
  },
  "player": {
    "id": "player_echo",
    "mode": "autoplay",
    "host_id": "host_044",
    "location_id": "lab_karax"
  },
  "locations": [
    {
      "id": "lab_karax",
      "entity_type": "location",
      "location_type": "laboratory",
      "name": "Laboratorios Abiertos del Este",
      "city_id": "karax",
      "faction_tags": ["anarchist", "technocratic"],
      "mood_tags": ["tense", "experimental", "cold"],
      "danger_level": 71,
      "visual_tags": ["industrial", "underground", "experimental"]
    }
  ],
  "npcs": [
    {
      "id": "npc_maela_ruun",
      "entity_type": "npc",
      "archetype": "scientist",
      "name": "Dra. Maela Ruun",
      "role": "investigadora tecnócrata disidente",
      "faction_tags": ["technocratic", "dissident"],
      "mood_tags": ["paranoid", "focused"],
      "location_id": "lab_karax",
      "attitude": {
        "trust": 31,
        "hostility": 18,
        "curiosity": 76
      }
    }
  ],
  "available_actions": [...],
  "narrative": {
    "location_description": "El edificio no tiene puerta principal...",
    "current_prompt": "Maela levanta la vista. —¿Vienes a destruir el laboratorio o a entenderlo?"
  }
}
```

## 14.4 VisualRegistry en Godot

Godot mantiene un registry que traduce tags → assets:

```yaml
VisualRegistry:
  entity_type_map:
    laboratory: "res://scenes/locations/Laboratory.tscn"
    district: "res://scenes/locations/District.tscn"
    archive: "res://scenes/locations/Archive.tscn"

  archetype_map:
    scientist: "res://scenes/npcs/Scientist.tscn"
    archivist: "res://scenes/npcs/Archivist.tscn"
    soldier: "res://scenes/npcs/Soldier.tscn"

  mood_tag_overrides:
    paranoid:
      animation_modifiers: ["look_around", "nervous_idle"]
    tense:
      lighting: "cold_blue"
    ritualistic:
      particles: "incense"

  visual_tag_compositor:
    industrial:
      props: ["pipes", "machinery"]
      lighting: "harsh"
    underground:
      props: ["darkness", "damp"]
      lighting: "dim"
    experimental:
      effects: ["chemical_glow", "sparking"]
```

## 14.5 Capas de arquitectura

```
[Engine] → genera estado abstracto
     ↓
[Exporter] → serializa snapshot
     ↓
[Godot Adapter] → interpreta snapshot
     ↓
[VisualRegistry] → traduce tags → assets
```

## 14.6 Múltiples clientes posibles

- terminal renderer
- Godot renderer
- web map
- replay timeline
- ASCII mode
- cinematic mode

Todos consumen el mismo snapshot abstracto.

## 14.7 API-style queries

**NO implementar inicialmente.** Razón: complejidad innecesaria, premature optimization, más acoplamiento runtime, debugging más difícil.

Primero: snapshots completos, archivos JSON, carga simple.

Luego: streaming, queries, WebSocket, delta updates, live sync.

## 14.8 GDScript mínimo

```gdscript
extends Node2D

func load_world_state(path: String) -> void:
    var file := FileAccess.open(path, FileAccess.READ)
    var data = JSON.parse_string(file.get_as_text())
    render_locations(data["locations"])
    render_npcs(data["npcs"])

func render_locations(locations: Array) -> void:
    for location in locations:
        var scene_path = VisualRegistry.location_type_map[location["location_type"]]
        var instance = load(scene_path).instantiate()
        instance.position = Vector2(location["x"] * 32, location["y"] * 32)
        add_child(instance)

func render_npcs(npcs: Array) -> void:
    for npc in npcs:
        var scene_path = VisualRegistry.archetype_map[npc["archetype"]]
        var instance = load(scene_path).instantiate()
        instance.position = Vector2(npc["x"] * 32, npc["y"] * 32)
        instance.set_meta("npc_id", npc["id"])
        add_child(instance)
```

## 14.9 Versionado

Agregar `schema_version` en cada snapshot para permitir evolución controlada.

## 14.10 KISS

**SÍ:**
- snapshot JSON autocontenido
- tags abstractos
- IDs estables
- VisualRegistry en Godot
- semántica desacoplada

**NO:**
- RPC complejo
- ECS distribuido
- GraphQL
- runtime entity queries
- networking complejo

---

## Metadata

- Origen: secciones 11.1-11.7 del spec.md original
- Dependencias: 01-architecture.md, 02-domain.md, 03-player-echo.md, 08-temporal-system.md
- Estado: incompleto - requiere revisión de todas las specs derivadas