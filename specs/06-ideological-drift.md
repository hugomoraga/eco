# 6. ideological-drift

## 6.1 Visión

La deriva ideológica NO es random ni arbitraria. Debe sentirse emergente, explicable, históricamente plausible, parcialmente impredecible.

El jugador debe poder entender por qué ocurrió una transformación ideológica, aunque no pueda predecir exactamente el resultado final.

## 6.2 Sistema híbrido de cuatro capas

### 6.2.1 Tensión estructural (núcleo)

Toda civilización, facción, doctrina e institución acumula presión de deriva basada en:

**Presión material:**
- hambre, infraestructura, desigualdad, guerra, crisis energética, enfermedad

**Presión social:**
- unrest, polarización, fatiga cultural, pérdida de legitimidad, fragmentación

**Presión institucional:**
- burocratización, rigidez, centralización, corrupción, institucionalización excesiva

**Presión temporal:**
- distancia generacional, reinterpretación narrativa, pérdida de claridad original, traducciones, propaganda, mitificación

```yaml
derive_pressure =
  (material_pressure * 0.25) +
  (social_pressure * 0.25) +
  (institutional_pressure * 0.25) +
  (temporal_pressure * 0.25) +
  - compatibility_modifier
  + mutation_risk_bonus

# Donde:
# - material_pressure: 0-100
# - social_pressure: 0-100
# - institutional_pressure: 0-100
# - temporal_pressure: 0-100
# - compatibility_modifier: -30 a +30 (de matriz de afinidades)
#   (ej: high_affinity = -20, medium_tension = +10, high_tension = +20)
# - mutation_risk_bonus: 0 a +20 (basado en esencia dominante)
#
# Resultado: 0-100 (después de clamping)
```

### 6.2.2 Genealogía memética (continuidad)

Toda idea y doctrina mantiene ancestros:

```txt
Voluntad sin Amo
  → Protocolos Autónomos
    → Consenso Algorítmico
      → Ministerio Predictivo
```

Las nuevas doctrinas heredan parcialmente: esencias, símbolos, instituciones, enemigos, traumas, sesgos, narrativa histórica.

Cada generación: degrada claridad, aumenta reinterpretación, puede radicalizar aspectos parciales.

### 6.2.3 Thresholds + eventos (visibilidad)

Cuando `derive_pressure` supera thresholds: ocurre transformación doctrinal, cisma, radicalización, institucionalización, colapso o reforma.

El engine genera DomainEvents estructurados. La IA SOLO narra e interpreta, NO decide causalidad.

```json
{
  "event": "The Schism of Autonomous Protocols",
  "causality": {
    "infrastructure_collapsing": true,
    "coordination_need": "high",
    "technocratic_legitimacy": "growing",
    "anarchism_efficiency": "declining"
  },
  "narrative_ia": "Los ingenieros comenzaron a afirmar que la libertad sin métricas conducía inevitablemente al hambre."
}
```

### 6.2.4 Matriz de afinidades (modificador)

Las esencias tienen compatibilidades y tensiones. La matriz NO controla deriva, solo modifica: velocidad, estabilidad, radicalización, probabilidad de fusión/cisma.

```yaml
affinity_matrix:
  anarchism ↔ technocracy: medium_tension
  capitalism ↔ accelerationism: high_affinity
  ecology ↔ transhumanism: high_tension
  thelema ↔ individualism: high_affinity
```

## 6.3 Ejemplos de transformación

```txt
Anarquismo + Tecnocracia → Gobierno algorítmico informal
Ecología + Autoritarismo → Ecofascismo
Thelema + Institución rígida → Culto jerárquico de la voluntad
Absurdismo + Desesperación social → Nihilismo violento
```

## 6.4 Reglas

**NO implementar:**
- árbol ideológico rígido
- tech tree
- alineamientos morales
- ideologías estáticas

**SÍ implementar:**
- mutación histórica
- reinterpretación
- institucionalización deformante
- generaciones reinterpretando doctrinas
- tensión entre intención original y resultado histórico

## 6.5 KISS - Primera implementación

- Fórmulas simples
- Pocos modifiers
- Thresholds explícitos
- Genealogía básica
- Replay completo vía logs JSONL

**NO implementar inicialmente:**
- machine learning
- simulación sociológica compleja
- ontologías gigantes
- redes neuronales ideológicas

## 6.6 Debugging obligatorio

Toda deriva debe poder explicarse:

```txt
KÁRAX — Año 102

Transformación:
Protocolos Autónomos → Consenso Algorítmico

Causas:
+22 crisis infraestructura
+18 presión coordinación
+11 institucionalización
+9 guerra externa
-7 autonomía local

Mutaciones:
* libertad individual ↓
* eficiencia ↑
* vigilancia ↑

Distancia doctrinal: 37%
```

Si el engine no puede explicar causalmente una deriva, la implementación es incorrecta.

---

## Metadata

- Origen: sección 7.3 del spec.md original
- Dependencias: 04-essences.md, 05-ideas-doctrines.md
- Notas: corregida fórmula derive_pressure (evita overflow)
- Estado: 🔄 En desarrollo