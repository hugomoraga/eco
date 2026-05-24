# 8. Temporal System

## 8.1 Tres escalas temporales

```txt
ActionTick   → segundos/minutos/horas (tiempo local/táctico)
WorldTick    → días/semanas/meses (simulación global)
HistoricalTick → años/décadas (cambio histórico)
```

## 8.2 WorldClock

El engine mantiene un reloj global:

```yaml
WorldClock:
  current_year: 47
  current_day: 284
  current_minute: 0
  accumulated_minutes_since_world_tick: 0
  accumulated_days_since_historical_check: 0
```

## 8.3 Duración por acción

Cada acción declara duración narrativa:

```yaml
walk_to_location: +10-30 minutos
talk_to_npc: +30-120 minutos
inspect_location: +15-60 minutos
write_manifesto: +3-7 días
found_circle: +2-8 semanas
travel_city: días/semanas
advance_era: +10-30 años
```

## 8.4 Procesamiento

Al aplicar una acción:
1. Se valida y ejecuta efecto inmediato
2. Se suma duración al WorldClock
3. Si cruza threshold diario/semanal → WorldTick
4. Si cruza threshold histórico o jugador elige `advance_era` → HistoricalTick

## 8.5 WorldTick triggers

**Por tiempo acumulado (NO por cantidad de acciones):**

| Frecuencia | Tick | Contenido |
|-------------|------|-----------|
| Diario | WorldTick-1d | necesidades locales, rumores, desplazamientos NPC |
| Semanal | WorldTick-7d | facciones reaccionan |
| Mensual | WorldTick-30d | instituciones progresan |
| Anual | WorldTick-365d | presión histórica menor |

## 8.6 HistoricalTick triggers

- `advance_era` ejecutado por jugador
- Autoplayer decide avanzar era
- Evento histórico mayor (guerra, colapso)
- Por threshold acumulado de presión histórica

## 8.7 Bloques explícitos

```yaml
wait_hours:
  duration: "+horas específicas"
  effect: "solo avanza ActionTick local"

sleep:
  duration: "+8 horas"
  effect: "recuperacion parcial, avanza ActionTick"

wait_days:
  duration: "+días específicos"
  effect: "WorldTick procesados sin acción del jugador"

travel:
  duration: "+días/semanas según distancia"
  effect: "cambio de ubicación, eventos en ruta"

advance_months:
  duration: "+meses específicos"
  effect: "varios WorldTick, no HistoricalTick"

advance_era:
  duration: "+10-30 años"
  effect: "HistoricalTick forzado, simulación de décadas"
```

## 8.8 Autoplayer y tiempo

El autoplayer usa el mismo sistema, sin privilegios especiales:

```yaml
AutoplayerDecision:
  action: "talk"
  target: "npc_maela"
  duration: "+1 hora"
  next_action_delay: "wait_days(7)"
```

El autoplayer puede:
- elegir acciones con duración
- usar bloques explícitos (`wait_days`, `advance_era`)
- encadenar secuencias de acciones
- esperar entre acciones

## 8.9 Godot y tiempo

Godot recibe en snapshots información temporal:

```yaml
Snapshot:
  meta:
    schema_version: "0.2.0"
    seed: 42
    turn: 14
    year: 47
    current_date: "Año 47, Día 284"
  player:
    current_mode: "autoplay"
    last_action_duration: "+3 días"
    accumulated_this_tick: 72  # días desde último WorldTick
  pending_events:
    - "faction_reunion_week_3"
    - "institutional_progress_check"
  next_tick_preview:
    next_world_tick: "7 días"
    next_historical_check: "90 días"
```

## 8.10 Ejemplo de flujo

```
Jugador ejecuta: talk_to_npc(Maela)
  → duración: +1 hora
  → WorldClock: minuto += 60
  → accumulated_minutes_since_world_tick: 60

Jugador ejecuta: inspect_lab
  → duración: +30 minutos
  → WorldClock: minuto += 30, día = 285

... (varias acciones)

WorldClock cruza threshold semanal (168 horas acumuladas)
  → WorldTick-7d dispara:
    - facciones procesan
    - rumores se propagan
    - algunos NPCs cambian ubicación

Jugador ejecuta: advance_era(20)
  → duración: +20 años
  → HistoricalTick dispara:
    - ideologías derivan
    - doctrinas mutan
    - civilizaciones cambian
    - posible muerte de host
```

## 8.11 KISS

**SÍ:**
- reloj simple con acumuladores
- thresholds fijos configurables
- acciones con duración fija o variable simple
- blocks explícitos claros

**NO:**
- scheduler complejo
- ECS temporal
- múltiples hilos de tiempo
- velocidad variable del tiempo en diferentes capas

---

## Metadata

- Origen: sección 2.5 del spec.md original
- Dependencias: 01-architecture.md, 07-actions.md
- Estado: incompleto - requiere revisión de todas las specs derivadas