# 12. AI Integration

## 12.1 Visión

La IA puede generar: personajes, diálogos, eventos narrativos, rumores, descripciones, dilemas, interpretación histórica.

La IA NO debe decidir directamente: economía, colapso, guerra, muerte, efectos finales, victoria o derrota.

Toda respuesta de IA debe validarse contra un esquema.

## 12.2 Roles de IA

Para el MVP, usar IA en cinco áreas:

```txt
1. Cronista histórico
   - resume eventos por año
   - describe transformaciones
   - interpreta causalidad

2. Generador de NPCs importantes
   - nombres, historias, motivaciones
   - conflictos internos
   - conexiones con otras entidades

3. Generador de eventos narrativos
   - dilemas emergentes
   - eventos menores
   - rumores

4. Generador de dilemas
   - situaciones morales/ideológicas
   - opciones con consecuencias

5. Intérprete de consecuencias históricas
   - análisis de deriva
   - impacto de doctrinas
   - narrativa de transformación
```

## 12.3 Salida estructurada

La IA debe responder en JSON.

```json
{
  "event_title": "La Huelga del Silencio",
  "summary": "Los obreros dejaron de hablar durante siete días.",
  "causes": [
    "labor_unrest",
    "absurdism",
    "surveillance"
  ],
  "choices": [
    {
      "label": "Apoyar el silencio",
      "effect_tags": [
        "increase_absurdism",
        "lower_productivity"
      ]
    },
    {
      "label": "Convertirlo en ritual",
      "effect_tags": [
        "increase_thelema",
        "increase_cult_risk"
      ]
    }
  ]
}
```

## 12.4 Validación de effect_tags

Sistema de tres capas:

### 12.4.1 Canonical System (capa oficial)

Solo estos tags modifican estado real, afectan replay oficial y participan en balance sistémico:

```yaml
allowed_effect_tags:
  - increase_unrest
  - increase_technocracy
  - increase_cult_risk
  - increase_memory_decay
  - increase_ideological_drift
  - increase_absurdism
  - increase_thelema
  - lower_productivity
  - increase_surveillance
  - spawn_faction
```

### 12.4.2 Emergent Layer (capa experimental)

Si la IA genera un tag desconocido (ej: `collective_memory_bleeding`, `ritualized_algorithms`):

1. NO ejecutar directamente
2. Registrar en emergent registry
3. Generar warning
4. Asociar contexto narrativo
5. Buscar similitud semántica

```yaml
emergent_phenomenon:
  id: "shared_temporal_echo"
  origin_event_id: evt_044
  semantic_neighbors:
    - memory
    - ideological_drift
    - identity_fragmentation
  stability: low
  canonical: false
```

### 12.4.3 Developer Approved Layer

Si un fenómeno reaparece, produce narrativa interesante y encaja sistémicamente, el diseñador puede promoverlo manualmente:

```yaml
shared_temporal_echo → approved
→ nuevo tag oficial: increase_temporal_fragmentation
```

## 12.5 Regla central

La IA puede: expandir imaginario, proponer símbolos, crear anomalías, introducir lenguaje nuevo, generar interpretaciones inesperadas.

La IA NO puede: modificar schemas, alterar fórmulas, crear stats automáticamente, cambiar causalidad del engine, alterar replay oficial.

## 12.6 Adaptadores

```yaml
adapter:
  OpenAIAdapter:
    model: "gpt-4"
    use_case: "producción"
    config:
      temperature: 0.7
      max_tokens: 500

  OllamaAdapter:
    model: "llama3"
    use_case: "desarrollo local"
    config:
      temperature: 0.8
      max_tokens: 500

  MockAdapter:
    use_case: "testing, CI"
    responses:
      predefined:
        npc_generation:
          - name: "Dra. Maela Ruun"
            role: "investigadora disidente"
            archetype: "scientist"
        event_description:
          - "Un silencio inhabitual se extendió por el laboratorio."
        historical_summary:
          - "Año 47: La idea de la Voluntad Colectiva Calculada comenzó a gestarse."
```

**Implementación de MockAdapter:**

El MockAdapter debe retornar respuestas predefinidas o generadas proceduralmente sin llamar a API externa:

```yaml
MockAdapter:
  behavior:
    sequential: true  # usa respuestas en orden
    random: false     # o selecciona aleatoriamente
    loop: true        # vuelve al inicio si se agotan

  # Para desarrollo inicial, el mock puede:
  # - retornar respuestas empty válidas
  # - usar templates con variables
  # - generar datos procedurales simples
```

## 12.7 Semantic neighbors

Cuando un tag es desconocido, se buscan neighbors semánticos para clasificación:

```yaml
semantic_neighbors_lookup:
  threshold: 0.6  # minimum similarity to assign neighbor

  # Basado en keywords compartidas
  collective_memory_bleeding:
    neighbors:
      - memory_decay: 0.8
      - ideological_drift: 0.6
      - identity_fragmentation: 0.7

  ritualized_algorithms:
    neighbors:
      - technocracy: 0.7
      - cult_risk: 0.6
      - institutional_drift: 0.5

  shared_temporal_echo:
    neighbors:
      - memory: 0.7
      - ideological_drift: 0.6
      - identity_fragmentation: 0.5
```

**Proceso:**
1. IA genera tag desconocido → `unknown_tag_log`
2. Sistema busca en semantic_neighbors_lookup
3. Si similarity > threshold → asocia neighbors
4. Emergent phenomenon creado con neighbors
5. No se ejecuta efecto hasta approval manual

## 12.7 KISS

**NO:**
- self-modifying engine
- runtime schema mutation
- ontology generation
- AI-driven rule synthesis
- auto-balancing procedural systems

**SÍ:**
- unknown_tag logging
- emergent registry
- manual approval
- semantic neighbors simples
- replay compatible

---

## Metadata

- Origen: secciones 10.1-10.3 del spec.md original
- Dependencias: 01-architecture.md, 06-ideological-drift.md
- Notas: MockAdapter definido, semantic neighbors con thresholds
- Estado: 🔄 En desarrollo