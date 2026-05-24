# 16. MVP

## 16.1 Visión

El objetivo del MVP es verificar que ideas producen consecuencias interesantes. Un prototype headless, reproducible, depurable.

## 16.2 MVP 0 — Simulación pura

**Objetivo:** verificar que ideas producen consecuencias interesantes.

**Incluye:**
```txt
1 ciudad
3 distritos
3 NPCs
5 esencias (anarchism, technocracy, absurdism, thelema, ecology)
5 acciones (talk, write_manifesto, found_circle, sabotage, ritualize)
logs JSONL
seed determinista
engine mínimo (sin autoplayer, sin IA, sin Godot)
```

**No incluye:** Godot, IA real, autoplayer completo.

**Verificación:**
```bash
python run.py --seed 42 --turns 50
# Debe generar:
# - runs/run_0001.jsonl
# - runs/snapshots/world_state_0050.json
# - outputconsole con eventos narrativos
```

## 16.3 MVP 1 — IA controlada

**Objetivo:** generar narrativa sin romper reglas.

**Incluye:**
```txt
MockAdapter
OpenAIAdapter opcional
generador de NPCs
generador de eventos
validador JSON
cronista histórico
```

## 16.4 MVP 2 — Autoplayer avanzado

**Objetivo:** probar runs largas.

**Incluye:**
```txt
goals configurables
heurísticas
modo suggest
modo autoplay
take control
replay de runs
```

## 16.5 MVP 3 — Godot read-only

**Objetivo:** visualizar snapshots.

**Incluye:**
```txt
Godot carga world_state.json
renderiza ciudad
renderiza NPCs
muestra acciones disponibles
muestra panel debug
no modifica todavía el engine
```

## 16.6 MVP 4 — Godot interactivo

**Objetivo:** enviar acciones al engine.

**Flujo:**
```txt
Godot muestra acciones
jugador elige acción
Godot escribe command.json
engine procesa acción
engine produce nuevo world_state.json
Godot refresca
```

## 16.7 MVP 5 — Live mode

**Objetivo:** comunicación en vivo.

```txt
Python Engine ↔ WebSocket ↔ Godot Client
```

## 16.8 Criterios de éxito del prototipo

**Verificación de implementación correcta:**

| Criterio | Test | Esperado |
|----------|------|----------|
| 1. Historia interesante | `python run.py --seed 42 --turns 100 --autoplay` | Eventos no triviales, transformaciones |
| 2. Explicable colapso | Inspector analiza run de 100 años | Puede explicar por qué ciudad X cayó |
| 3. Mutación comprensible | Tracking genealogía idea→doctrina | Deriva documentable |
| 4. Decisiones razonables | Log autoplayer revisado | scoring visible, no random |
| 5. Take control funciona | `mode: manual` en command.json | Autoplayer cede control |
| 6. Reproducibilidad | `run --seed 42` dos veces | Mismo resultado |
| 7. Godot desaclopado | Godot recibe snapshots | Sin conocimiento de reglas internas |

## 16.9 Primera tarea técnica

Crear el repositorio con:

```txt
engine mínimo
data/essences.yaml
data/actions.yaml
run.py
logs JSONL
autoplayer básico
world_state.json exportado
```

**Primer comando objetivo:**

```bash
python run.py --seed 42 --turns 50 --autoplay
```

**Debe generar:**

```txt
runs/run_0001.jsonl
runs/snapshots/world_state_0050.json
```

**Y el output de consola:**

```txt
Año 0: nace Nodo Libre Kárax.
Año 7: Maela Ruun funda el Laboratorio Abierto.
Año 13: aparece la idea "Voluntad Colectiva Calculada".
Año 28: la idea se institucionaliza como Protocolos Autónomos.
Año 50: Kárax comienza a derivar hacia tecnocracia informal.
```

---

## Metadata

- Origen: sección 13 del spec.md original
- Dependencias: 01-architecture.md, todas las specs
- Estado: incompleto - requiere revisión de todas las specs derivadas