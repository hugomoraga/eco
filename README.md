# ECO - Engine of Memetic Evolution

> **Status: MVP** — This is an early proof-of-concept. See [Vision](#vision) for the full scope.

---

**ECO** es un motor de simulación memética y civilizacional sobre ideologías, tiempo, instituciones y reinterpretación histórica.

ECO es un engine headless enfocado en:
- mutación ideológica
- presión civilizacional
- deformación institucional
- persistencia memética
- emergencia histórica
- simulación reproducible
- narrativa asistida por IA

El proyecto está diseñado alrededor de:
- simulación determinista
- arquitectura event-log-first
- Clean Architecture
- worldbuilding asistido por IA
- sistemas ideológicos emergentes
- futura visualización en Godot

---

## Visión

ECO explora una pregunta central:

> *¿Qué les ocurre a las ideas cuando colisionan con el tiempo, las instituciones, la realidad material y la interpretación humana?*

El jugador no controla simplemente una nación. En cambio, encarna un **Eco**: una conciencia memética persistente capaz de influir civilizaciones a través de generaciones.

Las ideas:
- mutan
- se fragmentan
- se institucionalizan
- se radicalizan
- sobreviven
- desaparecen
- se convierten en mitos

Las civilizaciones reaccionan a:
- escasez
- colapso de infraestructura
- tensión ideológica
- aceleración tecnológica
- presión ecológica
- trauma histórico

---

## Conceptos Centrales

### Player Echo (Eco)

El jugador no es inmortal como individuo. Controla un Eco: una entidad memética persistente que reencarna en distintos hosts a través del tiempo histórico.

**Atributos futuros:**
- `clarity` — coherencia doctrinal
- `resonance` — capacidad de propagación
- `presence` — influencia en el mundo
- `memory` — persistencia memética
- `will` — determinación
- `shadow` — faceta oculta/corrupta

**Estado MVP:** Solo `essence` implementado.

### Deriva Ideológica

Las ideas no son estáticas. Las doctrinas evolucionan mediante:
- tensión estructural
- institucionalización
- reinterpretación
- degradación generacional
- presión social
- contexto histórico

Una filosofía fundada como liberación puede mutar en autoritarismo, ritualismo, tecnocracia o cults del colapso.

**Estado MVP:** Essence affinity system básico existe.

### Facciones

Las facciones son organismos ideológicos semi-autónomos. Pueden:
- reclutar
- propagar doctrinas
- capturar instituciones
- radicalizarse
- fragmentarse
- reaccionar a condiciones materiales

No son simples "equipos" — son interpretaciones activas de ideas.

**Estado MVP:** Facciones estáticas sin comportamiento autónomo.

### Presión Estructural

La realidad material importa. La simulación modela:
- alimentos
- infraestructura
- energía
- vivienda
- desigualdad
- unrest
- legitimidad

Las ideas son puestos a prueba por la realidad.

**Estado MVP:** Sistema de presión básico existe (DerivePressureCalculator).

### Arquitectura Event-Log-First

ECO está diseñado alrededor de:
- **replay** — cualquier simulación puede reproducirse
- **observabilidad** — todo se loguea
- **debugging determinista** — misma seed = mismo resultado

Toda acción importante genera:
- eventos
- logs (simulation.jsonl)
- snapshots
- trazas históricas

**Estado MVP:** Logs + snapshots funcionan.

---

## Arquitectura

```
game_core/
├── domain/           # Entidades (Echo, Circle, Faction, World)
├── engine/           # Motor de simulación
│   ├── simulation.py    # Loop principal
│   ├── pressure.py      # Sistema de presión
│   ├── event_generator  # Eventos generados por IA
│   └── faction_tick.py  # Tick de facciones
├── actions/          # Acciones ejecutables
│   ├── found_circle     # Fundar un círculo
│   ├── propagate_idea   # Propagar idea a otros Echos
│   ├── write_manifesto  # Escribir manifesto con IA
│   ├── ritualize         # Ejecutar ritual
│   ├── sabotage         # Sabotear doctrina enemiga
│   └── talk             # Conversación
├── ai/
│   ├── adapters/         # MiniMax, OpenAI, Mock
│   └── base.py           # Interfaz común
├── autoplayer/          # Motor de autoplay (5 modos, 5 estilos)
├── config.py            # Sistema de configuración
├── i18n/                # Sistema de idiomas (es/en)
└── runs/                # Logs de simulaciones
```

---

## Quick Start

### Instalar

```bash
cd game_core
uv sync
```

### Configurar API Key (opcional)

```bash
cp .env.example .env
# Editar .env y agregar MINIMAX_API_KEY
```

Sin API key, el juego usa adaptadores mock (funcional pero sin IA real).

### Correr

```bash
# Con IA real (requiere MINIMAX_API_KEY en .env)
uv run python game_core/run.py --seed 42 --turns 50 --autoplay --ai-adapter minimax

# Con mock (sin API)
uv run python game_core/run.py --seed 42 --turns 50 --autoplay

# Estilos de autoplay
--autoplay-style revolutionary    # Enfoque en fundar círculos
--autoplay-style preservationist # Enfoque en mantener doctrina
--autoplay-style manipulator    # Enfoque en sabotaje
--autoplay-style mystic         # Enfoque en rituales
--autoplay-style technocrat     # Enfoque en propagar ideas

# Verbose para más output
uv run python game_core/run.py --turns 20 --autoplay --verbose
```

---

## Sistemas Implementados (MVP)

### Essences

Cada Echo tiene una esencia que define su base ideológica:

```
anarchism, socialism, communism, fascism,
progressivism, traditionalism, environmentalism,
technocracy, individualism, collectivism,
mysticism, rationalism, absurdism,
accelerationism, solarpunk, primitivism
```

Las esencias tienen **afinidad** entre sí (bonus/penalización en acciones).

### Circles

Grupos de Echos que comparten doctrina. Se fundan con `FoundCircle` (requiere 3+ miembros). Los círculos pueden generar NPCs.

### Presión

Sistema de presión que mide la tensión del mundo basándose en actividad de facciones, eventos y estabilidad del sistema.

### Eventos Narrativos

Cada 5 turnos se genera un evento narrativo. Con MiniMax, los eventos son únicos y contextuales.

### Autoplay

Motor con 5 modos:
- `manual` — sin autoplay
- `suggest` — sugiere acciones
- `autoplay` — ejecuta automáticamente
- `director` — guía la narrativa
- `replay` — reproduce una simulación

5 estilos que afectan scoring de acciones.

---

## Output

**Consola:** Resumen con emojis (futuro: spec-25)

**Logs:** `game_core/runs/run_YYYYMMDD_HHMMSS/simulation.jsonl`

```json
{"turn": 5, "event_type": "event", "data": {"title": "El Consejo de Barrias...", "choices": [...]}}
```

**Snapshots:** `game_core/runs/run_*/snapshots/snapshot_N.json`

---

## Roadmap MVP → Visión Completa

| Componente | MVP | Futuro |
|-----------|-----|--------|
| Echo attributes | essence | clarity, resonance, presence, memory, will, shadow |
| Deriva ideológica | affinity | mutación, institucionalización, degradación |
| Facciones | estáticas | semi-autonomous, reclutan, fragmentan |
| Presión civilizacional | basic | comida, infraestructura, energía, desigualdad |
| Reincarnación temporal | ❌ | Eco reencarna en distintos hosts |
| Simulación civilizacional | ❌ | Condiciones materiales + reacción |
| Replay determinista | logs | replay engine completo |
| Visualización | ❌ | Godot integration |

---

## Specs

| # | Spec | Estado |
|---|------|--------|
| 00 | Index | ✅ |
| 19 | MVP Implementation | ✅ |
| 21 | Testing Coverage | draft |
| 22 | AI Manifesto | draft |
| 23 | i18n | draft |
| 24 | Configuration | implemented |
| 25 | Console Logging | draft |

Ver `specs/` para detalles.

---

## Licencia

ECOL © 2026