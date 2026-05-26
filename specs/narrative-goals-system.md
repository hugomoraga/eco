# Narrative Log + Goals System Spec

## Overview

Transform the turn log from a flat event list into a **narrative story** where player and NPC goals create tension and competition. At game start, player picks from 3 goal options. NPCs get individual goals. At game end, whoever is closest to their goal wins.

---

## 0. Narrative Arc: Intro + Story Beats + Finale

The game follows a **three-act narrative structure**:

### Act I: El Despertar (Turno 0-5)
### Act II: La Efervescencia (Turno 6-14)
### Act III: El Cruce (Turno 15-20)

### 0.1 Opening Narrative (Game Start)

Before goal selection, show a **narrative introduction** based on the Echo's archetype and stats:

```
═══════════════════════════════════════════════════════
              ★ ECO DE LA REVOLUCIÓN ★
═══════════════════════════════════════════════════════

  [Narrative intro based on archetype]

  El Echo de [archetype] se manifiesta con claridad [X]%.
  Su esencia irradia: [essence_name].
  La ciudad tiembla ante la posibilidad del cambio.

  [Based on legitimacy stat]
  • Si legitimacy < 40: "El pueblo aún no confía en ti.
    Las viejas estructuras se mantienen erguidas."
  • Si legitimacy 40-70: "Hay ojos que te observan con esperanza.
    Algunos susurran tu nombre en las sombras."
  • Si legitimacy > 70: "Las calles murmuran tu llegada.
    El cambio parece inevitable."

  [Based on pressure stat]
  • Si pressure < 30: "La calma precede a la tormenta.
    Los poderosos duermen tranquilos... por ahora."
  • Si pressure 30-60: "La tensión se siente en el aire.
    Las reuniones secretas se multiplican."
  • Si pressure > 60: "La revolución late en cada esquina.
    El pueblo está listo para actuar."

  Presiona ENTER para elegir tu destino...
```

**Echo Archetype Intros:**

| Archetype | Intro Flavor |
|-----------|--------------|
| `artisan` | "Eres la voz de los artesanos, los makers, los que construyen con sus manos." |
| `merchant` | "De las transacciones surge el poder. Tu riqueza es tu arma." |
| `warrior` | "La fuerza bruta abre caminos que la palabra no puede." |
| `leader` | "Los demás te siguen. Tu palabra mueve multitudes." |
| `scholar` | "El conocimiento es poder. Y tú posees verdades peligrosas." |
| `artist` | "El arte desafía. Tu creación agita almas dormidas." |
| `mystic` | "Ves lo que otros no pueden. Tus visiones son profecías." |
| `wanderer` | "Llegas de donde nadie te espera. Tu libertad es tu mensaje." |

### 0.2 Mid-Game Story Beats

Every 5 turns, insert a **narrative beat** summarizing the state:

```
═══════════════════════════════════════════════════════
              ★ ACTO I: EL DESPERTAR ★
═══════════════════════════════════════════════════════

  Los primeros círculos comienzan a formarse.
  La semilla de la revolución echa raíces.

  ★ Progreso: Has fundado 2 círculos
  ★ La ciudad reacciona: 3 facciones aliadas
  ★ El regime responde con [response_type]

  ────────────────────────────────────────────────────
```

### 0.3 End of Game Narrative Summary

At game end, generate a **narrative summary** based on what happened:

```
═══════════════════════════════════════════════════════
              ★ EPÍLOGO ★
═══════════════════════════════════════════════════════

  [Bittersweet/Victory/Defeat narrative based on outcome]

  Turno 20. El sol se pone sobre la ciudad que cambió.

  Tu Eco resonó durante 20 turnos.
  Los círculos que fundaste: [X]. Permanecen en pie: [Y].
  Las ideas que sembraste no moririeron con tu partida.

  [Victory]
  "La revolución no terminó. Cambiaste el destino de esta ciudad.
   Tu nombre será recordado en los anales de los libres."

  [Close Defeat]
  "Por poco. El cambio estaba tan cerca que podías tocarlo.
   Pero las estructuras resistieron. Habrá otra oportunidad."

  [Total Defeat]
  "El viejo orden prevalece. Tu eco se desvanece sin eco.
   Pero las semillas de la duda ya fueron plantadas..."

  ★ Estadísticas Finales:
  ────────────────────────────────────────────────────
  Legitimacy final: [X]/100
  Círculos restantes: [Y]
  Facciones aliadas: [Z]
  NPCs que apoyaron tu causa: [W]

  ★ Tu Goal: [description] - [X]% completado
  ★ Mejor Goal Rival: [name] - [Y]%

  🏆 RESULTADO: [Victoria/Derrota] por [X]%
═══════════════════════════════════════════════════════
```

### 0.4 Narrative Tone

- **Writing style**: Second person ("Tú convocaste..."), poetic but readable
- **Emotional arc**: Hope → Tension → Climax → Resolution
- **NPC contribution to story**: Their actions feed into the narrative beats
- **Crisis as plot twists**: Each crisis changes the story direction

---

## 1. Narrative Turn Log

### Format

```
— Turno 3 —

  ▸ Hassan Al-Rashid convocó una reunión secreta en el sótano de la taberna.
  ▸ Scout Sven distribuyó panfletos en el mercado del distrito norte.
  ▸ Firebrand Orator predicó ante una multitud en la plaza central.

  ◆ Crisis: Escasez de alimentos
    Los mercados están vacíos. El pueblo tiene hambre.
    (-5 legitimacy, -3 resources this turn)

  ★ Tu Goal: Fundar 3 círculos       [██░░░░] 1/3 círculos
  ★ Goal Rivales:
    • Artisan Guild: Impedir círculos (2/5 turnos bloqueados)
    • Scholar Circle: Alcanzar 80 legitimacy

  ─────────────────────────────────────────
  Legitimacy: 65    Presión: 82    Recursos: 45
  Círculos: 1       Turnos restantes: 17
  ─────────────────────────────────────────

  + Escribiste un manifesto sobre sindicalismo
```

### Flavor Actions (Aleatorio por ahora)

Cada acción NPC tiene un **verbo + ubicación + detalle**:

| Base Action | Flavor (varies by location) |
|-------------|------------------------------|
| `conversar` | "conversó con vecinos en el mercado" / "tuvo una reunión secreta" |
| `propagar` | "distribuyó ideas en el distrito norte" / "colgó pancartas en la plaza" |
| `predicar` | "predicó ante una multitud en la catedral" / "darció un sermón en la taberna" |
| `organizar` | "fundó un círculo de trabajadores" / "creó una red de apoyo mutuo" |
| `sabotear` | "sabotó los suministros del distrito industrial" / "destruyó archivos del régimen" |
| `reclutar` | "reclutó 3 nuevos miembros" / "convenció a un comerciante local" |
| `negociar` | "negoció con los merchants del barrio" / "llegó a un acuerdo con los artesanos" |

Locations rotate: mercado, plaza central, taberna, catedral, distrito industrial, distrito norte, sótano.

---

## 2. Goals System

### Architecture

```
Goal (abstract)
├── ProgressGoal      # Reach X before Y turn
├── MaintainGoal      # Keep X below/above Y
├── AccumulateGoal    # Gather X resources/circles
└── SurviveGoal       # Stay alive for X turns
```

### Goal Interface

```python
class Goal(ABC):
    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def owner_id(self) -> str: ...  # "player" or npc_id

    @property
    @abstractmethod
    def owner_name(self) -> str: ...

    @property
    @abstractmethod
    def is_player(self) -> bool: ...

    @abstractmethod
    def evaluate(self, state: GameState) -> float:  # 0.0 to 1.0

    @abstractmethod
    def remaining_turns(self, current_turn: int) -> int: ...

    def progress_bar(self, state: GameState) -> str:  # "██░░░" style
```

### Player Goal Options (3 choices at game start)

Example options presented at game start:

```
Elige tu meta para esta partida:

  [1] ★ Círculos Libres
      "Fundar 5 círculos autónomos antes del turno 20"
      Necesitas: crear 5 círculos
      Dificultad: ████░ (4/5)

  [2] ★ Revolución Popular
      "Alcanzar 100 de legitimidad manteniendo la presión bajo 50"
      Necesitas: 100 legitimacy, presión < 50
      Dificultad: ███░░ (3/5)

  [3] ★ Auto-suficiencia
      "Acumular 100 recursos y sobrevivir 20 turnos"
      Necesitas: 100 recursos, no perder
      Dificultad: ██░░░ (2/5)
```

### NPC Goals (Individual, assigned at spawn)

Each NPC gets a goal based on archetype and randomness:

| Archetype | Goal Type | Example |
|-----------|-----------|---------|
| `artisan` | `AccumulateGoal` | "Acumular 50 recursos" |
| `merchant` | `AccumulateGoal` | "Acumular 80 recursos" |
| `warrior` | `MaintainGoal` | "Mantener presión > 90" |
| `leader` | `ProgressGoal` | "Fundar 2 círculos" |
| `scholar` | `ProgressGoal` | "Alcanzar 70 legitimidad" |
| `artist` | `ProgressGoal` | "Crear 3 eventos culturales" |
| `mystic` | `MaintainGoal` | "Mantener claridad > 60" |
| `wanderer` | `SurviveGoal` | "Sobrevivir 15 turnos" |

### Goal Factory

```python
class GoalFactory:
    @staticmethod
    def create_player_goal(options: list[Goal]) -> Goal:
        # Player picks from 3 pre-generated options

    @staticmethod
    def create_npc_goal(npc: Person, turn_limit: int) -> Goal:
        # Assign goal based on archetype + randomness
        archetype = npc.role or "neutral"
        goal_class = ARCHETYPE_GOAL_MAP.get(archetype, SurviveGoal)
        return goal_class(npc_id=npc.id, turn_limit=turn_limit)
```

### NPC Goal Assignment Rules

1. Top 3 NPCs (by influence) get **active competitive goals**
2. Other NPCs get `SurviveGoal` or simple `ProgressGoal`
3. NPC goals are **visible** from the start
4. Goals regenerate if NPC is replaced (new NPC gets new goal)

---

## 3. Crisis Dynamic System

### Crisis Types

| Crisis | Narrative | Effect |
|--------|-----------|--------|
| `food_shortage` | "Los mercados están vacíos" | -5 legitimacy, -3 resources |
| `communication_failure` | "La red de información cayó" | -10 to propagation |
| `protest` | "Manifestaciones en las calles" | -8 legitimacy |
| `disease` | "Una plaga azota la ciudad" | -15 vitality |
| `repression` | "El régimen envía tropas" | +15 pressure, -10 legitimacy |
| `prosperity` | "Buena cosecha este año" | +5 resources, +3 legitimacy |

### Crisis Trigger

- Check every 3-5 turns
- Based on current state thresholds
- New crisis replaces old one
- Narrative description + mechanical effect

---

## 4. Game End & Victory

### End Condition
- Turn reaches limit (default 20)
- Player vitality reaches 0

### Scoring

```python
def calculate_scores(player_goal: Goal, npc_goals: list[Goal], state: GameState) -> dict:
    player_progress = player_goal.evaluate(state)
    npc_progress = [g.evaluate(state) for g in npc_goals]

    return {
        "player": player_progress,
        "npcs": {g.owner_name: progress for g in npc_goals},
        "winner": "player" if player_progress >= max(npc_progress) else "npc"
    }
```

### End Screen

```
═══════════════════════════════════════════
              FIN DE LA PARTIDA
═══════════════════════════════════════════

  ★ Tu Goal: Fundar 5 círculos     [█████] 4/5 (80%)

  ★ Goal Rivales:
    • Hassan Al-Rashid: 100 legitimacy [███░░] 75%
    • Firebrand Orator: 2 círculos      [███░░] 67%

  🏆 VICTORIA: ¡Los círculos prevalecen!
     Llegaste al 80% de tu meta.

═══════════════════════════════════════════
```

---

## 5. Implementation Plan

### Phase 1: Goal System (Core)
- [ ] `game_core/domain/goals.py` - Goal abstract class + implementations
- [ ] `game_core/domain/goal_factory.py` - Factory for creating goals
- [ ] `game_core/domain/game_state.py` - State snapshot for evaluation
- [ ] Update `Person` entity to include `goal: Goal`
- [ ] `game_core/systems/simulation.py` - Goal evaluation each turn

### Phase 2: Narrative Actions
- [ ] `game_core/shared/narrative_actions.py` - Flavor text generator
- [ ] Update `_process_npc_turns()` to use flavor text
- [ ] Update TUI to render narrative format

### Phase 3: Dynamic Crisis
- [ ] `game_core/domain/crisis.py` - Crisis types + effects
- [ ] Crisis trigger system in simulation
- [ ] Update UI to show crisis narrative

### Phase 4: Game Flow
- [ ] Goal selection screen at start
- [ ] Goal display in turn log
- [ ] End game scoring + victory screen

### Phase 5: Integration
- [ ] NPC goal assignment at spawn
- [ ] Goal progress tracking
- [ ] Tests for goal evaluation

### Phase 6: Narrative Arc
- [ ] `game_core/domain/narrative_generator.py` - Generate intro, beats, finale
- [ ] Echo archetype intro templates
- [ ] Mid-game story beats every 5 turns
- [ ] End game narrative summary
- [ ] TUI integration for narrative screens

---

## 6. File Structure

```
game_core/
├── domain/
│   ├── goals.py           # Goal classes (abstract + implementations)
│   ├── goal_factory.py    # Factory for creating goals
│   ├── crisis.py          # Crisis types and effects
│   ├── game_state.py      # State snapshot for goal evaluation
│   └── narrative_generator.py  # Intro, beats, finale generator
└── shared/
    └── narrative_actions.py  # Flavor text for actions

adapter_core/
└── autoplayer/
    └── npc_engine.py      # Update to use narrative actions
```

---

## 7. Design Patterns Used

1. **Strategy Pattern** - `Goal` implementations (Progress, Maintain, Accumulate, Survive)
2. **Factory Pattern** - `GoalFactory` creates appropriate goal by archetype
3. **Observer Pattern** - Goals observe game state changes
4. **Template Method** - Base `Goal.evaluate()` defines skeleton, subclasses override metrics
5. **Null Object** - `SurviveGoal` as default for NPCs without specific goal

---

## 8. Key Constants

```python
# game_core/shared/constants.py
MAX_TURNS_DEFAULT = 20
NPC_GOAL_CHANCE_ACTIVE = 0.3  # 30% of NPCs get competitive goal
TOP_NPCS_WITH_GOALS = 3       # Only top 3 NPCs show their goals
CRISIS_CHECK_INTERVAL = 3     # Check for crisis every N turns
```
