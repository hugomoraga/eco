# 7. Actions

## 7.1 Acciones humanas

```yaml
actions:
  talk:
    label: "Hablar"
    scope: "npc"
    duration: "+30-120 minutos"
    effects:
      trust: 5

  write_manifesto:
    label: "Escribir manifiesto"
    scope: "city"
    duration: "+3-7 días"
    effects:
      idea_clarity: 10
      virality: 5
      surveillance_attention: 8

  found_circle:
    label: "Fundar círculo clandestino"
    scope: "district"
    duration: "+2-8 semanas"
    effects:
      institutionalization: 10
      repression_risk: 8

  sabotage:
    label: "Sabotear infraestructura"
    scope: "institution"
    duration: "+1-3 días"
    effects:
      stability: -12
      suspicion: 15

  ritualize:
    label: "Convertir idea en ritual"
    scope: "faction"
    duration: "+1-4 semanas"
    effects:
      symbolic_power: 15
      cult_risk: 12

  infiltrate:
    label: "Infiltrar institución"
    scope: "institution"
    duration: "+2-6 semanas"
    requires:
      - shadow: 20
      - insider_contact
      - low_suspicion

  recruit:
    label: "Reclutar para causa"
    scope: "npc"
    duration: "+1-7 días"
    effects:
      resonance: 5
      presence: 3

  travel:
    label: "Viajar entre ciudades"
    scope: "city"
    duration: "+días/semanas"
    effects:
      - (cambio de ubicación)
```

## 7.2 Estructura de acción

```yaml
action:
  id: "found_circle"
  label: "Fundar círculo clandestino"
  scope: "district"
  duration:
    min: "2 semanas"
    max: "8 semanas"
    variance: "depends on context"
  effects:
    immediate:
      institutionalization: 10
    delayed:
      repression_risk: 8
  requires:
    trusted_npc: true
    safe_location: true
    ideological_alignment: 0.6
  costs:
    resonance: -5
    shadow: 5
  risks:
    - "discovery"
    - "repression"
    - "cooptation"
```

## 7.3 Efectos por tipo

### Efectos inmediatos
Se aplican al momento de ejecutar la acción.

### Efectos demorados
Se aplican en siguientes ticks (WorldTick o HistoricalTick).

### Efectos persistentes
Modifican el estado del mundo permanentemente.

## 7.4 Costes sociales/contextuales

El Player Echo no "paga dinero". Las acciones requieren acceso, legitimidad, relaciones, presencia institucional, tiempo, resonancia, confianza.

```yaml
fund_circle:
  requires:
    - trusted_npc
    - safe_location
    - ideological_alignment

write_manifesto:
  requires:
    - archive_access
    - literacy_network
    - free_time

infiltrate_institution:
  requires:
    - shadow
    - insider_contact
    - low_suspicion
```

## 7.5 Acción serializada

Toda acción debe quedar en logs.

```json
{
  "turn": 14,
  "year": 47,
  "actor": "player_echo",
  "mode": "autoplayer",
  "action": "found_circle",
  "target": "district_open_labs_east",
  "payload": {
    "idea_id": "idea_collective_will_calculation"
  },
  "reason": "High local unrest and compatible technocratic minority.",
  "predicted_risks": [
    "algorithmic_governance",
    "anti_metric_revolt"
  ]
}
```

## 7.6 Acciones de salto temporal

```yaml
advance_era:
  label: "Avanzar era"
  duration: "+10-30 años"
  effects:
    - HistoricalTick triggered
    - faction ticks processed
    - ideological drift evaluated

wait_days:
  label: "Esperar días"
  duration: "+días específicos"
  effects:
    - WorldTick acelerado
    - eventos del mundo procesados

travel:
  label: "Viajar"
  duration: "+días/semanas según distancia"
  effects:
    - cambio de location
    - contexto social diferente
    - posibles eventos en ruta
```

## 7.7 Bloques explícitos

```yaml
wait_hours: "+horas específicas"
sleep: "+8 horas"
wait_days: "+días específicos"
travel: "+según distancia"
advance_months: "+meses específicos"
advance_era: "+10-30 años"
```

## 7.8 KISS

**SÍ:**
- acciones focalizadas
- efectos claros
- costes sociales
- duración narrativa

**NO:**
- cientos de acciones
- efectos granulares
- gestión de inventario
- complejidad de crafting

---

## Metadata

- Origen: secciones 8.1, 8.2 del spec.md original
- Dependencias: 01-architecture.md, 02-domain.md
- Estado: incompleto - requiere revisión de todas las specs derivadas