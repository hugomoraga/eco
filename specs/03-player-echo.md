# 3. Player Echo

## 3.1 Visión

El jugador no es solo un personaje físico. Es una influencia persistente con atributos persistentes de identidad.

El Eco:
- sobrevive;
- pero las encarnaciones no.

Cada cuerpo tiene contexto, límites, relaciones, traumas, mortalidad. La muerte debe importar.

## 3.2 Atributos del Eco

Los atributos son **modificadores sistémicos de identidad**, no recursos consumibles.

```yaml
player_echo:
  clarity: 50      # coherencia ideológica, precisión conceptual
  resonance: 50    # capacidad de propagación, viralidad memética
  presence: 50     # impacto interpersonal, carisma
  memory: 50       # continuidad entre encarnaciones
  will: 50         # resistencia a presión externa
  shadow: 0        # manipulación, coerción, influencia oscura
```

### 3.2.1 Efectos de cada atributo

| Atributo | Efectos |
|----------|---------|
| **clarity** | reduce distorsión doctrinal, mejora manifiestos, reduce mutación caótica, aumenta estabilidad memética |
| **resonance** | ideas se expanden rápido, NPCs recuerdan al Eco, doctrinas sobreviven generaciones |
| **presence** | conversaciones efectivas, liderazgo, reclutamiento, negociación, intimidación, persuasión |
| **memory** | recordar doctrinas antiguas, detectar patrones históricos, acceso a eventos previos, reconocer mutaciones |
| **will** | resistencia a corrupción, preservación de atributos entre vidas |
| **shadow** | sabotaje, infiltración, propaganda, radicalización, creación de cultos coercitivos |

### 3.2.2 Efectos contextuales

- **Baja clarity:** doctrinas ambiguas, reinterpretaciones extremas, cultos deformados, pérdida de significado original
- **Alta resonance:** expansión rápida, mayor riesgo de pérdida de control, más reinterpretaciones
- **Alta shadow:** acciones encubiertas fuertes, mayor riesgo de deformación histórica, doctrinas más peligrosas

## 3.3 Evolución de atributos

Los atributos cambian según comportamiento:

```yaml
Escribir doctrinas coherentes: +clarity
Manipular facciones excesivamente: +shadow, -clarity
Sobrevivir crisis ideológicas: +will
Crear movimientos culturales masivos: +resonance
Explorar ruinas históricas: +memory
Resolver conflictos directamente: +presence
```

## 3.4 Sistema híbrido de encarnación

### 3.4.1 Capas

1. **Host Layer** (encarnación actual)
2. **Echo Layer** (persistencia memética)
3. **Temporal Pressure**
4. **Transition States**
5. **Reincarnation Selection**

### 3.4.2 Host Layer

El jugador controla una encarnación concreta.

```yaml
host:
  id: "host_044"
  name: "Saira Vel"
  age: 31
  role: "underground_archivist"
  location: "karax"
  lifespan_estimate: 62
  vulnerabilities:
    - disease
    - political_persecution
```

El host: puede morir, enfermar, envejecer, radicalizarse, ser capturado y formar relaciones.

### 3.4.3 Echo Layer

El Eco persiste entre hosts. Mantiene: memoria parcial, atributos, doctrinas, traumas históricos, resonancia y fragmentos identitarios.

```yaml
echo:
  memory: 62
  will: 48
  resonance: 71
  clarity: 39
```

Al morir: parte persiste, parte se degrada, parte se transforma.

### 3.4.4 Temporal Pressure

El Eco NO puede permanecer indefinidamente en el mismo host. Cada host acumula `temporal_strain`:

- aging (acumula cada año)
- ideological burden (por doctrina del host)
- trauma (por eventos negativos)
- contradiction (conflicto entre valores Eco y host)
- institutionalization (captura por instituciones)

**Thresholds de presión temporal:**

```yaml
temporal_strain_thresholds:
  degradation_start: 40   # inicio de penalizaciones
  fragmentation_risk: 60   # riesgo de fragmentación de identidad
  collapse_risk: 80        # riesgo de colapso mental del host
  mandatory_transition: 100 # forzar transición
```

Cuando supera thresholds: degradación, fragmentación, pérdida de clarity, mutaciones, riesgo de colapso personal.

### 3.4.5 Muerte y Transición

La transición puede ocurrir por:
- muerte natural
- asesinato
- guerra
- enfermedad
- colapso mental
- sacrificio
- salto voluntario
- ruptura ideológica
- evento histórico mayor

NO solo por tiempo fijo.

### 3.4.6 Saltos Voluntarios

El jugador PUEDE abandonar un host, pero tiene coste, riesgo y pérdida.

```yaml
leave_host():
  costs:
    memory: -8
    clarity: -5
  risks:
    identity_fragmentation: 21
```

Esto evita: hopping constante, minmaxing absurdo, abuso estratégico.

### 3.4.7 Reencarnación Contextual

El jugador NO elige libremente. Las nuevas encarnaciones dependen de:
- resonancia del Eco
- doctrinas activas
- regiones influenciadas
- memoria histórica
- facciones conectadas
- instituciones existentes
- eventos históricos

```yaml
Possible Hosts:
  - archivist
  - dissident engineer
  - ritual leader
  - military defector
  - orphan raised by doctrine
```

### 3.4.8 Reencarnación Explícita Parcial

El jugador puede elegir entre opciones e influir el destino, pero NO tiene control absoluto.

**Selección de candidatos:**

El engine genera candidatos basándose en:
- Resonancia del Eco en la región (0-100)
- Afinidad doctrinaria (0-100)
- Estabilidad del host候选 (0-100)
- Riesgo de captura institucional (0-100)

**Fórmula de selección:**
```yaml
candidate_score =
  (resonance * 0.3) +
  (doctrinal_affinity * 0.3) +
  (host_stability * 0.2) +
  (100 - institutional_capture_risk * 0.2)
```

**Ejemplo:**

```yaml
Reincarnation Candidates:
  1:
    name: "Iria Sol"
    role: "Technocratic medic"
    affinity: "High memory retention"
    resonance_in_region: 72
    doctrinal_affinity: 65
    host_stability: 58
    institutional_capture_risk: 35
    score: 64.5

  2:
    name: "Taren Voss"
    role: "Border smuggler"
    affinity: "High shadow growth"
    resonance_in_region: 45
    doctrinal_affinity: 38
    host_stability: 42
    institutional_capture_risk: 15
    score: 43.8

  3:
    name: "Unnamed child"
    role: "Unknown"
    affinity: "Potentially high resonance"
    resonance_in_region: 20
    doctrinal_affinity: 55
    host_stability: 85
    institutional_capture_risk: 60
    score: 47.0
```

### 3.4.9 El Eco fuera de cuerpos

En ciertos casos, doctrinas, archivos, IA, cultos, instituciones o mitos pueden preservar fragmentos del Eco.

> "El Archivo de Kárax contiene patrones lingüísticos idénticos a los manifiestos del Eco hace 200 años."

### 3.4.10 Relación con HistoricalTicks

Los saltos históricos largos suelen ocurrir tras muerte, transición, colapso civilizacional, pérdida de host o avance de era.

## 3.5 Herencia entre encarnaciones

Al morir/reencarnar, parte de atributos persiste:

```yaml
new_memory = old_memory * persistence_factor
persistence_factor = 0.4 + (will * 0.003)
```

## 3.6 Filosofía

Los atributos representan **cómo el mundo recuerda e interpreta al Eco**, no "qué tan fuerte es el jugador".

El juego trata sobre cómo las ideas sobreviven a las personas. El Eco persiste. Los cuerpos no.

## 3.7 Debugging obligatorio

Toda transición debe ser explicable:

```txt
ECHO TRANSITION

Previous Host: Saira Vel
Cause: Political assassination
Memory retained: 62%
Clarity retained: 41%
New Host Selection Reason:
  - doctrine influence in region high
  - archival institutions active
  - resonance nearby
Time Passed: 14 years
```

Si las transiciones no pueden explicarse causalmente, la implementación es incorrecta.

---

## Metadata

- Origen: secciones 5.2, 5.3 del spec.md original
- Dependencias: 01-architecture.md, 02-domain.md
- Notas: agregados thresholds de temporal_strain y fórmula de selección de candidatos
- Estado: 🔄 En desarrollo