# 28 - Turn System + NPC Templates

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 07, 08  

---

## 1. Sistema de Turnos

El turno SIEMPRE pertenece al jugador. Los NPCs no consumen turnos propios — actúan en el mundo entre turnos del jugador, generando actividad que se resume al inicio del siguiente turno.

```
FLUJO POR TURNO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Turn N:
  1. [Sistema] Calcular actividad mundial (NPCs acted desde último turno)
  2. [Sistema] Generar summary de actividad
  3. [UI] Mostrar summary al jugador
  4. [Jugador] Elige acción
  5. [Motor] Ejecutar acción del jugador
  6. [Sistema] World tick: NPCs actúan, eventos trigger, etc.
  7. Repetir

```

**Principios:**
- El jugador NUNCA pierde su turno por acción de NPC
- Resumen de actividad es informativo, no blocking
- NPCs afectan el estado del mundo, no el turno del jugador

---

## 2. NPC World Activity Summary

Al inicio de cada turno del jugador, el sistema muestra 0-3 líneas de actividad mundial:

```
═══════════════════════════════════════════
TURN 7 — WORLD ACTIVITY
═══════════════════════════════════════════
• Brother Simón joined the Circle of First Garden
• Sister Elena spreads collectivist ideas in the eastern quarter
• Crisis: Authority banned public assembly
───────────────────────────────────────────
Your action:
```

**Reglas de generación:**
- Máx 3 líneas por turno
- 0 líneas si no hubo actividad relevante
- Líneas son hechos, no descripciones — formato: "[NPC name] [verbo] [descripción]"
- Si actividad contradice estado actual del mundo, se descarta

---

## 3. NPC Templates

Los NPCs se crean a partir de templates pre-generados. Esto permite:
- Carga rápida en runtime
- Templates diversos sin repetir personalización
- Base sólida para que la IA genere diálogos contextuales

### 3.1 Tipos de Template

```
TYPES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCHOLAR     → Philosopher, speaks in riddles, REFLECT behavior
ZEALOUS     → Ideologue, preaches, converts, EXPAND behavior  
PRAGMATIC   → Realist, calculates, survives, MANAGE behavior
MYSTIC      → Dreamer, sees visions, cryptic, RECEIVE behavior
REBEL       → Outlaw, acts doesn't explain, ATTACK behavior
CARETAKER   → Nurturer, feeds heals protects, SUPPORT behavior
```

### 3.2 Estructura del Template

```yaml
# data/npc_templates/scholar.yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

type: SCHOLAR
esencia_base: 1.0

comportamiento:
  en_evento: REFLECT    # Cómo reacciona a eventos del mundo
  en_interaccion: ASK_QUESTIONS  # Cómo interactúa con player
  accion_frecuente: WRITE  # Qué acción ejecuta con más frecuencia

dialogos:
  ASK_MEANING:
    es: "¿Qué es la libertad sino la elección de cadenas?"
    en: "What is freedom but the choice of chains?"
    fr: "Qu'est-ce que la liberté sinon le choix des chaînes?"
  REACT_CRISIS:
    es: "Incluso el fuego refina el oro."
    en: "Even fire refines gold."
  NPC_CONVERTS:
    es: "La luz pasa de lámpara en lámpara."
    en: "Light passes from lamp to lamp."
  GAINS_INFLUENCE:
    es: "El conocimiento crece cuando se comparte."
    en: "Knowledge grows when shared."
```

**Keys de diálogos en INGLÉS** — código limpio, sin inconsistencias. Valores en todos los idiomas soportados (es, en, fr, etc.).

### 3.3 Instanciación en Runtime

```
NPC INSTANCE = Template + Runtime Overrides
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

template: scholar.yaml
runtime:
  name: "Hermano Simón"       # Nombre generado
  circulo: "Circle of First Garden"  # Círculo actual o null
  esencia: 1.3                # Nivel actual (varía con el tiempo)
  estado: ACTIVE              # ACTIVE | SILENT | HIDDEN
  turn_activo: 5              # Turno de última actividad
```

### 3.4 Diálogos Pre-hechos

Cada template incluye 4-8 contextos de diálogo, cada uno con 2-4 respuestas pre-escritas:

```
CONTEXTOS:
━━━━━━━━━━━━

ASK_MEANING      → Qué dice cuando player pregunta sobre significado
REACT_CRISIS     → Qué dice cuando ocurre evento negativo
REACT_HOPE       → Qué dice cuando ocurre evento positivo
NPC_CONVERTS     → Qué dice cuando otro NPC se une a su causa
GAINS_INFLUENCE  → Qué dice cuando gana influencia
LOSES_INFLUENCE  → Qué dice cuando pierde influencia
PLAYER_ARRIVES   → Qué dice cuando player llega a su ubicación
PLAYER_ASKS      → Qué dice cuando player le hace pregunta directa
```

---

## 4. Carga de Templates

```
STARTUP:
━━━━━━━━━━━

1. Cargar todos los .yaml de data/npc_templates/
2. Parsear y validar estructura
3. Guardar en memoria como dict estático
4. En juego, instanciar desde dict — no leer archivos

Runtime instance:
  1. Seleccionar template aleatorio (o por contexto)
  2. Aplicar overrides de runtime
  3. Guardar referencia al template original
  4. Para diálogos, usar LanguageSystem para traducir
```

**Cantidad recomendada:** 20-30 templates para diversidad sin saturar.

---

## 5. Sistema de Lenguaje

### 5.1 Separación de Responsabilidades

Existen DOS sistemas de traducción en el proyecto:

**Sistema Global (spec-23):** `game_core/i18n/`
- Traduce eventos, acciones, messages del sistema
- Keys estilo `events:la_huelga_del_silencio:title`
- Archivoscentralizados: `es.yaml`, `en.yaml`

**NPC Templates:** Self-contained
- Cada template tiene sus diálogos inline
- Keys en inglés (ASK_MEANING, REACT_CRISIS, etc.)
- Valores en todos los idiomas dentro del mismo YAML
- No depende de i18n/ centralizado

```yaml
# NPC template: self-contained, inline i18n
dialogos:
  ASK_MEANING:
    es: "¿Qué es la libertad?"
    en: "What is freedom?"
```

**No se mixturan.** NPC templates son independientes del sistema de i18n de spec-23.

### 5.2 Obtención de Diálogo

```python
# Acceso directo al template (no pasa por i18n central)
dialogo = template["dialogos"][context_id][idioma_actual]
# Ejemplo: scholar["dialogos"]["ASK_MEANING"]["es"]
```

El `LanguageSystem` de spec-23 solo se usa para eventos, acciones, messages del sistema. Los diálogos de NPCs se leen directo del template.

---

## 6. Notas de Implementación

- Los templates se generan una vez (offline) y se guardan como YAML estáticos
- La IA solo interviene para generar diálogos contextuales cuando player interactúa con NPC existente, usando los pre-diálogos como base
- El summary de actividad mundial se calcula en WorldTick, no en PlayerTurn
- El turno del jugador siempre tiene exactamente una acción posible