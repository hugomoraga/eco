# 47. Essence System v2

**Supersedes:** spec-04 (essences)
**Status:** active
**Dependencies:** 01-architecture

---

## 47.1 Modelo de Esencias

### 47.1.1 EssenceProfile

Cada entity (Host, Person, Civ) tiene un perfil de esencias:

```python
class EssenceScore:
    essence: str          # id de esencia
    value: int            # 0-100

class EssenceProfile:
    dominant: List[EssenceScore]  # 1-3 esencias dominantes, suma ~100
    underlying: List[EssenceScore]  # resto de esencias, 0-100 c/u, pueden ser 0
```

**Reglas:**
- Dominant: exactamente 1-3 esencias con peso significativo (≥15?)
- Underlying: todas las demás esencias, pueden estar en 0
- Una esencia puede estar en dominant O underlying, no ambos

### 47.1.2 Compatibilidad

```yaml
affinity_levels:
  CONFIRMED:      # fusion natural, colaboración estable
  HIGH_AFFINITY:  # aliados naturales, fricción mínima
  MEDIUM_AFFINITY:# pueden cooperar con esfuerzo
  NEUTRAL:        # sin opinión marcada
  MEDIUM_TENSION: # disagreement marcado, cooperar es difícil
  HIGH_TENSION:   # adversarios naturales, conflicto probable
  INCOMPATIBLE:   # fusión muy difícil, mutuamente excluyentes
```

### 47.1.3 Cálculo de alineación Civ vs Person

```
alignment_score = weighted_average(
    dominant_person vs dominant_civ,
    compatibilities
)
```

- score ≥ 60 → alineado (loyalty bonus)
- score ≤ 40 → disidente (resistance +)
- Target Civ: 70% persons alineadas, 30% disidentes

---

## 47.2 Las 20 Essencias

| ID | Nombre | Descripción corta | Atributos clave |
|----|--------|-------------------|-----------------|
| thelema | Thelema | "Mi voluntad es ley" | will: 25, individualism: 20, cult_risk: 15 |
| monoteism | Monoteísmo | Un dios, un camino | order: 20, obedience: 20, symbolic_unity: 20 |
| polytheism | Politeísmo | Muchos dioses, muchas verdades | tolerance: 20, diversity: 20, complexity: 15 |
| animism | Animismo | Todo tiene espíritu | spirituality: 25, nature_respect: 20, mysticism: 15 |
| atheism | Ateísmo | No hay trascendencia | rationalism: 20, independence: 15, nihilism: 10 |
| absurdism | Absurdismo | Crear sentido del caos | creativity: 25, meaning_stability: -20, individualism: 15 |
| nihilism | Nihilismo | Nada tiene valor | apathy: 20, meaning_stability: -25, drift_risk: 15 |
| existentialism | Existencialismo | Existencia precede esencia | autonomy: 25, meaning_stability: 15, individualism: 20 |
| humanism | Humanismo | El humano como centro | empathy: 25, social_cohesion: 15, rationalism: 10 |
| pragmatism | Pragmatismo | Lo que funciona es lo vrai | efficiency: 25, adaptability: 20, realpolitik: 15 |
| ecology | Ecología | La naturaleza es sagrada | extraction: -20, resilience: 20, nature_respect: 25 |
| technocracy | Tecnocracia | Los técnicos gobiernan | efficiency: 25, surveillance: 20, institutional_stability: 15 |
| anarchism | Anarquismo | Sin gobierno, auto-organización | autonomy: 30, institutional_stability: -20, innovation: 15 |
| feudalism | Feudalismo | Jerarquía natural | order: 25, obedience: 25, inequality: 15 |
| socialism | Socialismo | Lo común sobre lo individual | social_cohesion: 25, equality: 20, collectivism: 20 |
| capitalism | Capitalismo | El mercado libre es sagrado | competition: 25, growth: 25, inequality: 15 |
| mysticism | Misticismo | Experiencia directa de lo divino | spirituality: 30, mysticism: 25, intuition: 20 |
| rationalism | Racionalismo | La razón sobre todo | rationalism: 30, order: 15, skepticism: 15 |
| romanticism | Romanticismo | Emoción, pasión, natura | creativity: 25, emotion: 25, nature_respect: 15 |
| stoicism | Estoicismo | Virtud, autocontrol, aceptar | order: 20, resilience: 20, obedience: 15 |

---

## 47.3 Matriz de Compatibilidades

```
affinity_matrix:
  thelema:
    absurdism: CONFIRMED
    existentialism: HIGH_AFFINITY
    anarchism: MEDIUM_TENSION
    monoteism: HIGH_TENSION
    socialism: INCOMPATIBLE

  monoteism:
    stoicism: HIGH_AFFINITY
    feudalism: HIGH_AFFINITY
    rationalism: MEDIUM_AFFINITY
    thelema: MEDIUM_TENSION
    atheism: INCOMPATIBLE

  polytheism:
    animism: HIGH_AFFINITY
    romanticism: HIGH_AFFINITY
    mysticism: MEDIUM_AFFINITY
    monoteism: HIGH_TENSION

  animism:
    ecology: CONFIRMED
    mysticism: HIGH_AFFINITY
    romanticism: MEDIUM_AFFINITY
    technocracy: HIGH_TENSION

  atheism:
    rationalism: CONFIRMED
    existentialism: HIGH_AFFINITY
    nihilism: MEDIUM_TENSION
    mysticism: INCOMPATIBLE

  absurdism:
    thelema: CONFIRMED
    existentialism: HIGH_AFFINITY
    romanticism: MEDIUM_AFFINITY
    stoicism: HIGH_TENSION
    monoteism: INCOMPATIBLE

  nihilism:
    absurdism: HIGH_AFFINITY
    existentialism: MEDIUM_AFFINITY
    stoicism: HIGH_TENSION
    humanism: INCOMPATIBLE

  existentialism:
    absurdism: HIGH_AFFINITY
    humanism: HIGH_AFFINITY
    thelema: MEDIUM_AFFINITY
    nihilism: MEDIUM_TENSION

  humanism:
    existentialism: HIGH_AFFINITY
    socialism: HIGH_AFFINITY
    rationalism: MEDIUM_AFFINITY
    feudalism: HIGH_TENSION

  pragmatism:
    capitalism: HIGH_AFFINITY
    technocracy: HIGH_AFFINITY
    socialism: MEDIUM_TENSION
    romanticism: NEUTRAL

  ecology:
    animism: CONFIRMED
    socialism: HIGH_AFFINITY
    romanticism: MEDIUM_AFFINITY
    capitalism: HIGH_TENSION

  technocracy:
    pragmatism: HIGH_AFFINITY
    capitalism: HIGH_AFFINITY
    rationalism: MEDIUM_AFFINITY
    anarchism: HIGH_TENSION

  anarchism:
    socialism: CONFIRMED
    ecology: HIGH_AFFINITY
    absurdism: MEDIUM_AFFINITY
    feudalism: INCOMPATIBLE

  feudalism:
    monoteism: HIGH_AFFINITY
    stoicism: HIGH_AFFINITY
    socialism: HIGH_TENSION
    anarchism: INCOMPATIBLE

  socialism:
    anarchism: CONFIRMED
    humanism: HIGH_AFFINITY
    ecology: MEDIUM_AFFINITY
    capitalism: INCOMPATIBLE

  capitalism:
    pragmatism: HIGH_AFFINITY
    technocracy: HIGH_AFFINITY
    feudalism: MEDIUM_TENSION
    socialism: INCOMPATIBLE

  mysticism:
    animism: CONFIRMED
    polytheism: MEDIUM_AFFINITY
    romanticism: MEDIUM_AFFINITY
    rationalism: HIGH_TENSION

  rationalism:
    atheism: CONFIRMED
    technocracy: HIGH_AFFINITY
    existentialism: MEDIUM_AFFINITY
    mysticism: HIGH_TENSION

  romanticism:
    animism: HIGH_AFFINITY
    existentialism: MEDIUM_AFFINITY
    polytheism: MEDIUM_AFFINITY
    rationalism: HIGH_TENSION

  stoicism:
    monoteism: HIGH_AFFINITY
    feudalism: MEDIUM_AFFINITY
    rationalism: MEDIUM_AFFINITY
    absurdism: HIGH_TENSION
```

---

## 47.4 Mutación de Esencias

### 47.4.1 Cómo mutan

Las acciones del Host (y NPCs) influyen en los perfiles de esencia:

```
action_type → essence_modification

e.g.:
"write_manifesto" → thelema +5, monoteism -2
"donate_resources" → socialism +5, capitalism -2
"destroy_institution" → anarchism +7, feudalism -5
"perform_ritual" → mysticism +5, or respective essence
```

### 47.4.2 Reglas de mutación

- Solo dominant puede aumentar (por acciones)
- Si dominant supera 80 → puede "cristalizar" consumiendo otra
- Underlying puede pasar a dominant si supera threshold (≥30?) y hay espacio
- Si una dominant baja de 20 → se mueve a underlying
- Máximo 1 mutación por tick por entity

### 47.4.3 Drift acumulativo

```
drift_pressure = sum(compatibility_in_contexto) / num_essences
```

Civs con drift_pressure alto → más resistencia al cambio, más riesgo de cisma/fusión

---

## 47.5 Efectos Mecánicos

### 47.5.1 Alineación Civ vs Person

```python
def calculate_alignment(person: Person, civ: Civ) -> float:
    """Returns 0-100 alignment score"""
    score = 0
    for pd in person.essence.dominant:
        for cd in civ.essence.dominant:
            score += affinity_matrix[pd.essence][cd.essence] * (pd.value * cd.value / 10000)
    return min(100, max(0, score))
```

- ≥70: alineado → loyalty +10, acciones tienen efecto positivo
- ≤40: disidente → resistance +10, acciones tienen fricción
- 40-70: neutral, sin bonus

### 47.5.2 Formación de Círculos

- Persona necesita affinity ≥60 con host para ser invitada
- Círculo tiene esencia propia (promedio de miembros)
- Círculo puede entrar en tensión si su esencia se aliena de la Civ

### 47.5.3 Facciones

- Essenencias similares → facciones aliadas
- Esencias en HIGH_TENSION/INCOMPATIBLE → facciones adversarias
- Civs пытаются mantener balance (70/30)

---

## 47.6 API

```python
class EssenceSystem:
    def affinity(e1: str, e2: str) -> AffinityLevel
    def alignment(person: Person, civ: Civ) -> float
    def mutate(entity: Entity, action: Action) -> EssenceProfile
    def compatible(person: Person, host: Host) -> bool  # for circle formation
    def suggest_faction(entity: Entity) -> Faction
```

---

## 47.7 Deprecación

Este spec reemplaza y extiende `spec-04-essences.md`. El contenido antiguo de 04 se mantiene como referencia histórica pero está obsoleto.

---

## Metadata

- Supersedes: 04-essences
- State: active
- Created: 2025-05-24