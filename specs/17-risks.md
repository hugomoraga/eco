# 17. Risks

## 17.1 Riesgo: IA demasiado libre

**Síntoma:** la IA genera eventos que rompen causalidad, introducen mecánicas no deseadas, alteran reglas del engine.

**Mitigación:**
- JSON schema
- effect tags permitidos (Canonical/Emergent/Approved)
- validación estricta
- MockAdapter para testing
- replay completo para verificar comportamiento

## 17.2 Riesgo: simulación aburrida

**Síntoma:** la simulación produce resultados predecibles, sin emergencia, sin historia interesante.

**Mitigación:**
- empezar con eventos humanos
- NPCs clave
- tensiones claras
- consecuencias históricas visibles
- presión estructural multicausal

## 17.3 Riesgo: arquitectura sobrecomplicada

**Síntoma:** el sistema se vuelve difícil de mantener, debuggear, extender.

**Mitigación:**
- primero archivos JSON
- no WebSocket al inicio
- no Godot hasta que el engine produzca runs interesantes
- KISS en cada decisión
- spec-driven development

## 17.4 Riesgo: el jugador no siente agencia

**Síntoma:** las acciones del jugador no tienen impacto visible, las ideas mutan sin relación con lo que hace.

**Mitigación:**
- acciones de influencia directa
- consecuencias visibles
- salto temporal
- deformación de ideas
- retorno a lugares transformados

## 17.5 Riesgo: deriva arbitraria

**Síntoma:** las transformaciones ideológicas no pueden explicarse, el jugador no entiende por qué pasó algo.

**Mitigación:**
- sistema de 4 capas (tensión estructural, genealogía, thresholds, matriz)
- debugging obligatorio
- logs que muestran causalidad
- toda transformación debe ser explicable

## 17.6 Riesgo: acoplamiento engine-Godot

**Síntoma:** cambios en el engine rompen el cliente Godot, o viceversa.

**Mitigación:**
- snapshots genéricos con tags abstractos
- VisualRegistry en Godot
- schema_version para evolución controlada
- separación clara de responsabilidades

## 17.7 Riesgo: autoplayer converge a estrategia única

**Síntoma:** sin importar seed o contexto, el autoplayer siempre hace lo mismo.

**Mitigación:**
- evaluación multiobjetivo
- personalidad estratégica
- presión adaptativa contextual
- métricas meméticas (no victoria absoluta)

## 17.8 Riesgo: proliferación de specs desconectadas

**Síntoma:** las specs evolucionan independently, el sistema se fragmenta.

**Mitigación:**
- índice con dependencias declaradas
- revisión periódica de consistencia
- mantener traceabilidad entre specs
- cada spec referencia sus dependencias

## 17.9 Tabla resumen

| Riesgo | Probabilidad | Impacto | Mitigación principal |
|--------|--------------|---------|----------------------|
| IA demasiado libre | Media | Alto | 3 capas de validación |
| Simulación aburrida | Media | Alto | Presión estructural multicausal |
| Arquitectura sobrecomplicada | Alta | Alto | KISS, MVP primero |
| Sin agencia | Media | Alto | Consecuencias visibles |
| Deriva arbitraria | Baja | Alto | Debugging obligatorio |
| Acoplamiento | Baja | Alto | Snapshots abstractos |
| Autoplayer converge | Media | Medio | Personalidad estratégica |
| Specs desconectadas | Baja | Medio | Índice y dependencias |

## 17.10 Review schedule

Para evitar specs desconectadas:

```yaml
review_cycle: "2 semanas"

review_checklist:
  - "Dependencies still valid?"
  - "Cross-spec references working?"
  - "State tracking updated?"
  - "New issues documented?"

escalation:
  - "Si riesgo crece → discutir en siguiente review"
  - "Si spec obsoleta → mark deprecated"
```

---

## Metadata

- Origen: sección 16 del spec.md original
- Dependencias: 01-architecture.md, todas las specs
- Notas: agregado review schedule para evitar specs desconectadas
- Estado: 🔄 En desarrollo