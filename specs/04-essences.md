# 4. Essences

## 4.1 Definición

Las esencias son marcos de percepción y organización del mundo. No son solo ideologías políticas.

Representan formas de entender: el orden, la libertad, la eficiencia, el significado, la voluntad, la naturaleza, el progreso, lo sagrado.

## 4.2 Ejemplos iniciales

```yaml
essences:
  anarchism:
    order: -15
    autonomy: 25
    institutional_stability: -10
    innovation: 10
    drift_risk: 15

  technocracy:
    efficiency: 25
    autonomy: -10
    surveillance: 20
    institutional_stability: 15
    empathy: -8

  absurdism:
    meaning_stability: -20
    creativity: 20
    obedience: -10
    drift_risk: 25

  thelema:
    will: 25
    cult_risk: 20
    individualism: 15
    institutional_drift: 15

  ecology:
    extraction: -20
    resilience: 20
    growth: -10
    territorial_balance: 25

  capitalism:
    growth: 25
    inequality: 20
    competition: 20
    social_cohesion: -10

  monotheism:
    symbolic_unity: 25
    heresy_pressure: 20
    order: 15

  progressivism:
    identity_fluidity: 20
    tradition_continuity: -15
    inclusion: 25
    narrative_conflict: 15

  transhumanism:
    technology_acceptance: 30
    human_enhancement: 25
    mortality_rejection: 20
    artificial_integration: 25
    institutional_drift: 15
    empathy: -5
```

## 4.3 Atributos de esencia

Cada esencia tiene valores que representan su afinidad con ciertos aspectos sociales:

| Atributo | Descripción |
|----------|-------------|
| order | Preferencia por estructura vs caos |
| autonomy | Valoración de la libertad individual |
| institutional_stability | Preferencia por permanencia institucional |
| innovation | Apertura al cambio |
| drift_risk | Tendencia a mutar con el tiempo |
| efficiency | Orientación a resultados óptimos |
| surveillance | Aceptación de control/monitorización |
| empathy | Consideración por el otro |
| meaning_stability | Estabilidad del sentido vital |
| creativity | Orientación a lo nuevo |
| obedience | Respeto a autoridad/tradición |
| will | Énfasis en la voluntad personal/colectiva |
| cult_risk | Peligro de formación de culto |
| individualism | Énfasis en el individuo vs grupo |
| institutional_drift | Tendencia a capturar instituciones |
| extraction | Orientación a usar recursos |
| resilience | Capacidad de recuperación |
| growth | Valoración de expansión/acrecentamiento |
| territorial_balance | Equilibrio territorial |
| inequality | Tolerancia a la desigualdad |
| competition | Orientación competitiva |
| social_cohesion | Valoración de unity social |
| symbolic_unity | Unidad mediante símbolos/compartida |
| heresy_pressure | Presión contra disidencia religiosa/ideológica |
| identity_fluidity | Flexibilidad identitaria |
| tradition_continuity | Valoración de continuidad |
| inclusion | Orientación a incluir |
| narrative_conflict | Conflicto interno en narrativas |

## 4.4 Matriz de afinidades

Las esencias tienen compatibilidades y tensiones. La matriz NO controla deriva, solo modifica: velocidad, estabilidad, radicalización, probabilidad de fusión/cisma.

```yaml
affinity_matrix:
  anarchism:
    technocracy: medium_tension
    absurdism: high_affinity
    thelema: medium_tension
    ecology: high_affinity
    capitalism: low_tension

  technocracy:
    anarchism: medium_tension
    absurdism: medium_tension
    thelema: medium_affinity
    ecology: low_tension
    capitalism: high_affinity

  absurdism:
    anarchism: high_affinity
    technocracy: medium_tension
    thelema: high_affinity
    ecology: low_tension
    capitalism: low_tension

  thelema:
    anarchism: medium_tension
    technocracy: medium_affinity
    absurdism: high_affinity
    individualism: high_affinity
    cult_risk: high_risk

  ecology:
    anarchism: high_affinity
    technocracy: low_tension
    transhumanism: high_tension
    extraction: negative_20

  capitalism:
    technocracy: high_affinity
    accelerationism: high_affinity
    social_cohesion: negative_10

  monotheism:
    order: 15
    heresy_pressure: 20
    symbolic_unity: 25

  progressivism:
    identity_fluidity: 20
    tradition_continuity: -15
    inclusion: 25
    narrative_conflict: 15
```

## 4.5 Composición de civilizaciones

Una civilización no tiene una sola esencia. Tiene mezcla.

```yaml
civilization:
  id: "karax"
  name: "Nodo Libre Kárax"
  essences:
    anarchism: 65
    technocracy: 35
    absurdism: 20
```

Esto permite sociedades contradictorias:

```txt
Anarquismo federado + facciones tecnocráticas + cultos absurdistas.
```

## 4.6 Esencias como presión estructural

Las esencias dominan en una civilización según proporción y contexto:

```txt
Domina anarquismo 65% + tecnocracia 35%:
→ gobierno algorítmico informal emerge
→ vigilancia aumentada
→ libertad individual en tensión
```

## 4.7 KISS

**NO implementar:**
- taxonomías exhaustivas de ideologías
- árboles de esencias
- alineamientos morales rígidos

**SÍ implementar:**
- valores simples por esencia
- matriz de afinidades básica
- proporciones dinámicas

---

## Metadata

- Origen: sección 6 del spec.md original
- Dependencias: 01-architecture.md
- Notas: agregada esencia transhumanism
- Estado: 🔄 En desarrollo