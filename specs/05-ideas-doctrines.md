# 5. Ideas y Doctrinas

## 5.1 Idea

Una idea es una semilla memética.

```yaml
idea:
  id: "idea_collective_will_calculation"
  name: "La Voluntad Colectiva Calculada"
  essences:
    - technocracy
    - thelema
  clarity: 61
  virality: 44
  stability: 28
  mutation_risk: 72
  origin:
    actor_id: "player_echo"
    city_id: "karax"
    year: 47
```

### 5.1.1 Atributos de idea

| Atributo | Descripción |
|----------|-------------|
| clarity | coherencia, precisión conceptual, resistencia a distorsión |
| virality | capacidad de propagación, expansión social |
| stability | resistencia a mutación, persistencia temporal |
| mutation_risk | probabilidad de transformación no controlada |

### 5.1.2 Mecanismo de virality

La virality determina cómo una idea se propaga:

```yaml
virality_thresholds:
  0-20:   "insular" - apenas se difunde
  21-40:  "local" - alcanza círculo inmediato
  41-60:  "regional" - afecta neighborhoods/distritos
  61-80:  "mass" - atraviesa ciudades
  81-100: "pandemic" - spread rapido, difícil controlar

virality_calculation:
  base = idea.virality
  modifiers:
    speaker_resonance: +resonance * 0.2
    compatible_essence: +10 per matching essence in listeners
    institutional_access: +15 if speaker has institutional access
    opposite_essence_pressure: -20 per opposing essence dominant
```

### 5.1.3 Ciclo de vida

1. **Germinación**: el jugador planta idea en NPC/facción
2. **Expansión**: virality permite propagación
3. **Estabilización**: puede convertirse en doctrina
4. **Mutación**: mutation_risk alto → deriva
5. **Muerte**: claridad cero → desaparece o se transforma

## 5.2 Doctrina

Una doctrina es una idea estabilizada en texto, escuela, culto, institución o tradición.

```yaml
doctrine:
  id: "doctrine_protocolos_autonomos"
  name: "Protocolos Autónomos"
  source_ideas:
    - "idea_collective_will_calculation"
  institutionalization: 62
  distortion: 31
  branches:
    - "rama_libertaria"
    - "rama_algoritmica"
```

### 5.2.1 Atributos de doctrina

| Atributo | Descripción |
|----------|-------------|
| institutionalization | grado de integración en instituciones |
| distortion | alejamiento de intención original |

### 5.2.2 Ramas

Las doctrinas pueden fracturarse en ramas, cada una con interpretación distinta:

```yaml
doctrine:
  id: "doctrine_protocolos_autonomos"
  branches:
    rama_libertaria:
      id: "rama_libertaria"
      name: "Rama Libertaria"
      emphasis: "autonomía individual"
      distortion: 18
      core_essence: "anarchism"
      secondary_essence: "thelema"
      followers: 34
      stability: 72

    rama_algoritmica:
      id: "rama_algoritmica"
      name: "Rama Algorítmica"
      emphasis: "coordinación centralizada"
      distortion: 44
      core_essence: "technocracy"
      secondary_essence: "absurdism"
      followers: 67
      stability: 51
```

**Estructura de rama:**
- `id`: identificador único
- `name`: nombre legible
- `emphasis`: interpretación principal de la doctrina
- `distortion`: alejamiento de la intención original (0-100)
- `core_essence`: esencia dominante de la rama
- `secondary_essence`: esencia secundaria
- `followers`: cantidad de seguidores (afecta poder político)
- `stability`: estabilidad interna de la rama (0-100)

## 5.3 Genealogía memética

Toda idea y doctrina mantiene ancestros. La genealogía permite rastrear mutaciones.

```txt
Voluntad sin Amo
  → Protocolos Autónomos
    → Consenso Algorítmico
      → Ministerio Predictivo
```

### 5.3.1 Herencia

Las nuevas doctrinas heredan parcialmente:
- esencias
- símbolos
- instituciones
- enemigos
- traumas
- sesgos
- narrativa histórica

### 5.3.2 Degradación generacional

Cada generación:
- degrada claridad
- aumenta reinterpretación
- puede radicalizar aspectos parciales

## 5.4 Filosofía

Las ideas son semillas. Las doctrinas son sistemas organizados. La genealogía es la historia de cómo las ideas sobreviven, mutan o mueren.

## 5.5 KISS

**NO implementar:**
- ontologías meméticas complejas
- tracking detallado de cada mutación
- simulación de transmisión cultural granular

**SÍ implementar:**
- genealogía básica con ancestros
- tracking de claridad/distorsión
- ramas simples

---

## Metadata

- Origen: secciones 7.1, 7.2 del spec.md original
- Dependencias: 04-essences.md
- Notas: agregado mecanismo de virality, estructura completa de branches
- Estado: 🔄 En desarrollo