# 1. Architecture

## 1.1 Visión del proyecto

El proyecto es un juego de simulación histórica, filosófica y memética donde el jugador no controla directamente una civilización, sino una influencia persistente —un "Eco"— que atraviesa cuerpos, épocas e instituciones.

El mundo está compuesto por civilizaciones, ciudades, facciones, NPCs, ideas, doctrinas y esencias filosóficas/políticas/espirituales. Las acciones del jugador implantan ideas en personas, grupos o instituciones. Con el paso del tiempo, esas ideas mutan, se institucionalizan, se corrompen o producen nuevas formas sociales.

El primer objetivo no es crear una visualización completa, sino un motor headless altamente depurable que permita probar la lógica sistémica antes de conectarlo a Godot.

## 1.2 Principios de diseño

### 1.2.1 Separación estricta

El engine no debe depender de Godot.

```txt
[Headless Engine]
    verdad del mundo, reglas, turnos, historia, autoplayer

        ↓ JSON / SQLite / API

[Godot Client]
    visualización, input humano, UI, cámara, sprites, tilemaps
```

### 1.2.2 La simulación decide, la IA interpreta

La IA puede generar:
- personajes;
- diálogos;
- eventos narrativos;
- rumores;
- descripciones;
- dilemas;
- interpretación histórica.

La IA no debe decidir directamente:
- economía;
- colapso;
- guerra;
- muerte;
- efectos finales;
- victoria o derrota.

Toda respuesta de IA debe validarse contra un esquema.

### 1.2.3 Todo debe ser observable

Desde el día cero, cada turno debe generar logs:
- estado antes;
- acción tomada;
- razón de la acción;
- efectos aplicados;
- estado después;
- eventos generados;
- mutaciones ideológicas;
- decisiones del autoplayer;
- prompts/respuestas IA, si aplica.

### 1.2.4 Todo debe ser reproducible

Toda simulación debe poder ejecutarse con seed.

```bash
python run.py --seed 42 --turns 100 --autoplay
```

La misma seed y los mismos datos deberían producir la misma historia, salvo cuando se permita explícitamente variación de IA.

## 1.3 Stack recomendado

### 1.3.1 Prototipo headless

```txt
Python 3.12+
Pydantic
PyYAML
SQLite opcional
pytest
rich / textual opcional para debug CLI
```

### 1.3.2 Cliente visual futuro

```txt
Godot 4.x
GDScript
JSON snapshots
WebSocket opcional para modo live
```

### 1.3.3 IA

Adaptadores intercambiables:

```txt
OpenAIAdapter
OllamaAdapter
MockAdapter
```

El `MockAdapter` es obligatorio para testear sin gastar tokens ni depender de red.

## 1.5 Character Encoding

**Todo el código y datos debe usar ASCII estándar.**

- Nombres de archivos y variables: snake_case en inglés
- Comentarios y docstrings: inglés
- Strings en código: inglés
- YAML keys: snake_case en inglés

**Prohibido:** acentos, caracteres especiales, emojis, texto en otros idiomas en código.

```txt
# Ejemplo correcto:
player_echo.py
def get_available_actions():
    """Return list of available actions."""
    pass

# Ejemplo incorrecto:
jugador_echo.py  # español no permitido
café.py          # acentos no permitidos
```

**Excepciones para contenido narrativo:**
- Nombres de personajes: "Dra. Maela Ruun", "Saira Vel"
- Diálogos y descripciones: en data/, runs/, snapshots/
- Output del sistema: campos `narrative`, `description`

---

## 1.6 Arquitectura general

```txt
/game-core
  /engine
    world.py
    simulation.py
    turn.py
    action.py
    effects.py
    history.py
    random.py

  /domain
    civilization.py
    city.py
    district.py
    faction.py
    npc.py
    essence.py
    idea.py
    doctrine.py
    institution.py
    player_echo.py

  /ai
    adapter.py
    mock_adapter.py
    openai_adapter.py
    ollama_adapter.py
    prompt_builder.py
    validators.py

  /autoplayer
    planner.py
    heuristics.py
    goals.py
    decision_log.py

  /renderers
    text_renderer.py
    json_exporter.py
    timeline_renderer.py

  /data
    essences.yaml
    actions.yaml
    event_templates.yaml
    npc_archetypes.yaml
    locations.yaml

  /schemas
    world_state.schema.json
    action.schema.json
    ai_event.schema.json
    godot_contract.schema.json

  /tests
    test_drift.py
    test_actions.py
    test_autoplayer.py
    test_serialization.py

  /runs
    run_0001.jsonl
    snapshots/

  run.py
  inspect.py
  replay.py

/godot-client
  /scenes
  /scripts
  /assets
  /data
```

## 1.5 Sistema temporal (ver [spec-08](08-temporal-system.md))

El sistema temporal completo (ActionTick, WorldTick, HistoricalTick, WorldClock) está definido en [spec-08](08-temporal-system.md).

---

## Metadata

- Origen: secciones 1, 2, 3 del spec.md original
- Dependencias: ninguna (base)
- Notas: sección 1.5 (Sistema temporal) movida a spec-08
- Estado: 🔄 En desarrollo