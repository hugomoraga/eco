# 13. Events

## 13.1 Visión

Los eventos externos NO son completamente predefinidos ni totalmente emergentes ni generados por IA libremente.

Sistema: **plantillas sistémicas parametrizadas + emergencia desde simulación + narrativa IA opcional**.

La IA NO crea causalidad. La IA SOLO interpreta, dramatiza, contextualiza y humaniza.

## 13.2 Emergencia sistémica (núcleo)

El engine detecta presiones estructurales:

```yaml
# Material
famine
plague
blackout
ecological_collapse
industrial_accident
migration_wave

# Social
riots
revolutionary_wave
cult_emergence
institutional_fracture
mass_panic
labor_strike

# Ideological
doctrinal_schism
reinterpretation_movement
anti_technocratic_uprising
ritualization_wave
memetic_contamination

# Political
civil_war
secession
authoritarian_consolidation
alliance_collapse
```

Estas NO son todavía "eventos narrativos". Son tensiones, estados, acumuladores, riesgos históricos.

```yaml
karax:
  food: 21
  infrastructure: 33
  unrest: 72
  plague_risk: 61

→ event_pressure:
    famine: 78
    social_unrest: 64
    migration_wave: 42
```

## 13.3 Plantillas parametrizadas

Cuando un riesgo supera threshold, el engine selecciona plantilla compatible:

```yaml
event_templates:

  famine:
    triggers:
      - event_pressure.famine > 70
    possible_causes:
      drought: { weight: 20, conditions: { climate: "arid" } }
      logistics_collapse: { weight: 30, conditions: { logistics: "< 30" } }
      war_disruption: { weight: 25, conditions: { war_pressure: "> 60" } }
      ideological_mismanagement: { weight: 15, conditions: { anarquism: "> 70" } }
      infrastructure_failure: { weight: 35, conditions: { infrastructure: "< 25" } }
    parameters:
      severity:
        range: [1, 100]
        default: 50
        calculation: "avg(food_deficit, logistics_pressure)"
      duration_months:
        range: [1, 24]
        default: 6
      spread:
        range: [1, 5]  # 1=local, 5=regional
        default: 2
    effects:
      economy_food: "severity * -0.5"
      unrest: "severity * 0.3"
      migration: "severity * 0.2"
      technocracy_pressure: "severity * 0.15"
      legitimacy: "severity * -0.2"

  plague:
    triggers:
      - event_pressure.plague > 65
    possible_causes:
      disease_vector: { weight: 40 }
      sanitation_collapse: { weight: 35 }
      migration: { weight: 25 }
    parameters:
      severity: { range: [1, 100], default: 50 }
      duration_months: { range: [3, 18], default: 8 }
      spread: { range: [1, 5], default: 3 }
    effects:
      population: "severity * -0.3"
      production: "severity * -0.2"
      stability: "severity * -0.25"
      unrest: "severity * 0.2"
```

**Estructura de template:**
- `triggers`: conditions que disparan el evento
- `possible_causes`: causas con weight y conditions
- `parameters`: rangos y cálculos
- `effects`: fórmulas para modificar estado

Resultado:

```yaml
FamineEvent:
  location: karax
  severity: 71
  duration_months: 8
  cause: infrastructure_failure
  effects:
    +unrest
    +migration
    +technocracy_pressure
    -legitimacy
```

## 13.4 Narrativa IA (opcional)

La IA puede describir:

> "Los mercados de Kárax dejaron de recibir alimentos. Las cooperativas comenzaron a requisar bodegas privadas mientras los ingenieros exigían sistemas de distribución centralizados."

Pero la IA NO decide: cuándo ocurre, cuánto dura, efectos reales, causalidad.

## 13.5 Eventos completamente emergentes

Algunos eventos NO tienen plantilla fija. Emergen de la simulación:

```yaml
DomainEvent: DoctrineFragmented
DomainEvent: FactionRadicalized
DomainEvent: IdeologicalPressureCritical
```

## 13.6 Regla central

Los eventos NO deben sentirse "el juego tiró un dado". Deben sentirse "las condiciones históricas llevaron a esto".

## 13.7 Eventos predefinidos vs emergentes

| Tipo | Quién decide | Ejemplo |
|------|--------------|---------|
| Template | Engine + parámetros | famine, plague, war |
| Emerging | Engine + reglas | DoctrineFragmented, FactionRadicalized |
| Narrative | IA | descripción, dramatización |

## 13.8 Ejemplo completo

```yaml
Estado:
  food: 18
  infrastructure: 29
  war_pressure: 63

Engine detecta: famine_risk = 81

Threshold cruzado → selecciona plantilla: FamineEvent

Parámetros:
  cause: war_disruption
  severity: high
  duration: 6 months

Effects:
  +unrest
  +migration
  +technocracy_pressure
  -rural_stability

IA narra:
"Las caravanas dejaron de cruzar el corredor norte. En menos de dos meses, las plazas de distribución comenzaron a vaciarse. Los Protocolos Autónomos exigieron control centralizado de alimentos."
```

Todo reproducible, explicable, emergente, histórico.

## 13.9 KISS

**NO:**
- director narrativo complejo
- story manager tipo RimWorld avanzado
- simulación meteorológica profunda
- generación procedural total
- IA creando causalidad

**SÍ:**
- YAML templates
- thresholds simples
- modifiers contextuales
- eventos parametrizados
- replayable
- deterministic-friendly

---

## Metadata

- Origen: sección 10.4 del spec.md original
- Dependencias: 01-architecture.md, 02-domain.md, 09-economy.md, 12-ai-integration.md
- Notas: plantillas con estructura completa (triggers, causes, parameters, effects)
- Estado: 🔄 En desarrollo