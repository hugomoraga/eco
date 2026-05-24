# 9. Economy

## 9.1 Visión

La economía NO es un juego de gestión de recursos tradicional. Existe para generar tensiones históricas y presión estructural.

El juego NO trata sobre administrar dinero. Trata sobre cómo las ideas sobreviven o se deforman al chocar con realidad material.

## 9.2 Economía estructural del mundo

Cada ciudad/distrito tiene estado material simplificado. Estos valores NO son recursos del jugador, pertenecen al mundo, generan presión estructural y afectan deriva ideológica.

### 9.2.1 Estructura de economía local

```yaml
city:
  id: "karax"
  economy:
    food: 62
    infrastructure: 48
    energy: 71
    housing: 39
    logistics: 52
    inequality: 67
    production: 58
    stability: 44
```

### 9.2.2 Atributos económicos

| Atributo | Descripción |
|----------|-------------|
| food | disponibilidad alimentaria |
| infrastructure | estado de obras, transporte, servicios |
| energy | acceso a energía, electricidad |
| housing | vivienda disponible, calidad |
| logistics | capacidad de distribución, comercio |
| inequality | brecha entre grupos |
| production | capacidad productiva industrial |
| stability | estabilidad general del sistema |

### 9.2.3 Relación con esencias

```txt
infraestructura baja + anarquismo alto → aumenta presión tecnocrática
desigualdad alta + capitalismo extremo → aumenta radicalización social
escasez energética + aceleracionismo → riesgo de colapso industrial
```

La economía genera presión material, no decide resultados directamente.

## 9.3 Coste social/contextual del jugador

El Player Echo no "paga dinero". Las acciones requieren: acceso, legitimidad, relaciones, presencia institucional, tiempo, resonancia, confianza.

### 9.3.1 Ejemplos de costes

```yaml
fund_circle:
  requires:
    - trusted_npc: true
    - safe_location: true
    - ideological_alignment: 0.6

write_manifesto:
  requires:
    - archive_access: true
    - literacy_network: true
    - free_time: true

infiltrate_institution:
  requires:
    - shadow: 20
    - insider_contact: true
    - low_suspicion: true

sabotage:
  requires:
    - shadow: 30
    - technical_access: true
    - low_security: true
```

## 9.4 Instituciones y recursos

Las instituciones consumen recursos del mundo:

```yaml
institution:
  type: "distributed_archive"
  upkeep:
    infrastructure: 5    # unidades de infraestructura por mes
    energy: 3              # unidades de energía por mes
    social_trust: 8       # unidades de confianza social por mes
```

**Unidades de upkeep:**
- `infrastructure`: puntos de infraestructura
- `energy`: puntos de energía
- `social_trust`: puntos de cohesión social

**Verificación mensual:**
```yaml
city:
  economy:
    infrastructure: 48   # disponible
    energy: 71             # disponible
    social_trust: 60      # disponible

institution_upkeep_total:
  infrastructure: 12       # suma de todas las instituciones
  energy: 8
  social_trust: 15

balance:
  infrastructure: 48 - 12 = 36  # surplus → ok
  energy: 71 - 8 = 63            # surplus → ok
  social_trust: 60 - 15 = 45    # surplus → ok
```

Si el mundo no sostiene eso:
- infraestructura < 0 → instituciones degradan, posible colapso
- energía < 0 → instituciones funcionales al 50%
- social_trust < 0 → instituciones pierden legitimidad, riesgo de captura

**Thresholds críticos:**
```yaml
critical_thresholds:
  infrastructure:
    danger: < 20
    collapse: < 5
  energy:
    danger: < 25
    collapse: < 10
  social_trust:
    danger: < 30
    collapse: < 10
```

## 9.5 Integración con derive_pressure

La economía es input directo al sistema de presión estructural:

```yaml
economy_to_pressure_mapping:
  food_low:
    threshold: < 30
    pressure_type: "material"
    pressure_value: +25

  infrastructure_low:
    threshold: < 35
    pressure_type: "material"
    pressure_value: +20

  energy_critical:
    threshold: < 20
    pressure_type: "material"
    pressure_value: +30

  inequality_high:
    threshold: > 70
    pressure_type: "social"
    pressure_value: +15

  production_low:
    threshold: < 40
    pressure_type: "material"
    pressure_value: +15

  stability_low:
    threshold: < 35
    pressure_type: "social"
    pressure_value: +20
```

**Ejemplo de cálculo:**

```yaml
city.karax:
  food: 22        → food_low → +25 material_pressure
  infrastructure: 28 → infrastructure_low → +20 material_pressure
  energy: 18      → energy_critical → +30 material_pressure
  inequality: 71  → inequality_high → +15 social_pressure

total_derive_pressure_contribution:
  material: +75
  social: +15

→ Estos valores se incorporan al cálculo de derive_pressure
  en la fórmula definida en spec-06
```

## 9.5 Eventos económicos

Los eventos económicos disparan presión estructural:

```yaml
famine:
  effects:
    food: -30
    unrest: +20
    technocracy_pressure: +15

infrastructure_collapse:
  effects:
    infrastructure: -25
    logistics: -20
    production: -15

energy_crisis:
  effects:
    energy: -35
    production: -20
    stability: -15
```

## 9.6 KISS

**NO implementar:**
- simulación de mercado
- oferta/demanda profunda
- inflación
- cadenas logísticas complejas
- comercio granular
- workers individuales
- pathfinding económico
- simulación industrial detallada

**SÍ implementar:**
- pocos indicadores
- valores agregados
- no simulación granular
- pocas fórmulas
- efectos visibles
- causalidad clara

---

## Metadata

- Origen: sección 7.5 del spec.md original
- Dependencias: 01-architecture.md, 02-domain.md
- Notas: agregadas unidades de upkeep, thresholds críticos, integración con derive_pressure
- Estado: 🔄 En desarrollo