# SPEC: Domain Entities — Essence, IdeologicalTag, Eco

## Status: Draft

---

## 1. Essence — entidad de identidad ideológica

### Problema actual
`Essence` es un `str` libre en todo el codebase:
```python
echo.essence = "anarchism"  # string
```

Se Valida en ningún lado. No hay autocompletado, no hay type safety.

### Solución
```python
class Essence(str, Enum):
    """Las 5 esencias canonicales del juego."""
    ANARCHISM    = "anarchism"
    TECHNOCRACY  = "technocracy"
    ABSURDISM    = "absurdism"
    THELEMA      = "thelema"
    ECOLOGY      = "ecology"

    @property
    def modifiers(self) -> dict[str, float]:
        """Devuelve los modificadores de gameplay de esta esencia."""
        return EssenceData.get_modifiers(self.value)

    @property
    def affinity_with(self, other: "Essence") -> float:
        return EssenceData.get_affinity(self.value, other.value)
```

### Datos asociados (lee de `essences.yaml`)
Cada `Essence` tiene:

| Campo | Descripción |
|---|---|
| `order` | Preferencia institucional (-20 a +20) |
| `affinities` | Afinidad con otras esencias |
| Modificadores | `autonomy`, `innovation`, `drift_risk`, etc. |

### Migración
- `echo.essence: str` → `echo.essence: Essence`
- `faction.essence: str` → `faction.essence: Essence`
- `npc.essence: str` → `npc.essence: Essence`
- Renombrar `EssenceRegistry` → `EssenceData` (evitar confusión con la entidad)
- Quitar `essences.yaml` y poner los datos inline como dictionary constant en `EssenceData`

---

## 2. IdeologicalTag — entidad de label doctrinal

### Problema actual
`IdeologicalTag` existe en `entities.py` pero no se usa consistentemente:
- `Echo.known_tags` es `list[IdeologicalTag]` ✓
- `Circle.ideology_tags` es `list[str]` ✗ (debería ser `list[IdeologicalTag]`)
- `Faction.ideology_tags` es `list[str]` ✗ (debería ser `list[IdeologicalTag]`)

### Modelo
```python
class IdeologicalTag(BaseModel):
    """Un tag doctrinal: 'concept:Consenso Horizontal'"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str          # "concept" | "practice" | "symbol"
    name: str              # "Consenso Horizontal"
    essence_weights: dict[str, float]  # {"anarchism": 0.9}

    def to_semantic_key(self) -> str:
        return f"{self.category}:{self.name}"

    @property
    def dominant_essence(self) -> str | None:
        if not self.essence_weights:
            return None
        return max(self.essence_weights, key=self.essence_weights.get)
```

### Migración
- `Circle.ideology_tags: list[str]` → `list[IdeologicalTag]`
- `Faction.ideology_tags: list[str]` → `list[IdeologicalTag]`

---

## 3. Eco — estado ecológico del mundo

### Problema actual
`World` mezcla dos conceptos:
- Estado político (`pressure`, `legitimacy`, population)
- Estado ecológico (sin entidad dedicada)

### Solución: nueva entidad `Eco`
```python
class Eco(BaseModel):
    """
    Estado ecológico global.

    Representa la salud del mundo como un organismo vivo:
    - balance territorial
    - extraction vs resilience
    - stability markers
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    balance: float = 50.0       # [-100, 100] — equilibrio territorial
    extraction: float = 0.0      # [+recursos, -salud]
    resilience: float = 50.0     # [ capacidad de recuperación ]
    stability: float = 50.0     # [0, 100]

    def is_in_crisis(self) -> bool:
        return self.balance < 20 or self.resilience < 20

    def apply_extraction(self, amount: float) -> None:
        self.balance += amount
        self.resilience = max(0, self.resilience - amount * 0.5)

    def apply_recovery(self, amount: float) -> None:
        self.resilience = min(100, self.resilience + amount)
        if self.resilience > 70:
            self.balance = min(100, self.balance + amount * 0.2)
```

### Rol en eldominio
- `World.eco: Eco` —替换 `world.balance` explícito
- Actions que extraen recursos llaman `eco.apply_extraction()`
- Events de disaster llaman `eco.apply_decay()`
- `World.is_crisis()` Consulta `world.eco.is_in_crisis()` AND `world.pressure > 70`

---

## 4. Manifesto — documento doctrinal

### Problema actual
`Echo.manifestos` es `list[str]` — el manifiesto completo en texto plano.

### Solución
```python
class Manifesto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    essence: Essence
    written_at_tick: int
    tags: list[IdeologicalTag] = Field(default_factory=list)
```

`Echo.manifestos: list[str]` → `Echo.manifestos: list[Manifesto]`

---

## 5. Resumen de cambios

| Entidad | Archivo | Cambio |
|---|---|---|
| `Essence` | `domain/essence.py` (nuevo) | Enum con `.modifiers` y `.affinity_with` |
| `EssenceData` | `domain/essence.py` | `EssenceRegistry` renombrado, datos inline |
| `IdeologicalTag` | `domain/entities.py` | Ya existe — ampliar `.dominant_essence` |
| `Circle.ideology_tags` | `domain/entities.py` | `list[str]` → `list[IdeologicalTag]` |
| `Faction.ideology_tags` | `domain/entities.py` | `list[str]` → `list[IdeologicalTag]` |
| `Eco` | `domain/eco.py` (nuevo) | Entidad ecológica del mundo |
| `Manifesto` | `domain/manifesto.py` (nuevo) | Reemplaza `list[str]` en `Echo.manifestos` |
| `echo.essence` | `domain/entities.py` | `str` → `Essence` |
| `faction.essence` | `domain/entities.py` | `str` → `Essence` |
| `npc.essence` | `domain/npc.py` | `str` → `Essence` |

---

## 6. Orden de implementación

1. **`Essence` + `EssenceData`** — sin esto todo lo demás no compila
2. **`IdeologicalTag.dominant_essence`** — property trivial
3. **`Manifesto`** — solo si hay tests
4. **`Eco`** — requiere cambiar `World.is_crisis()`
5. Migrar `Circle.ideology_tags` y `Faction.ideology_tags`
6. Migrar `echo.essence`, `faction.essence`, `npc.essence`
7. Migrar `Echo.manifestos`

**Nota:** Esta es una spec de trabajo. Cada entidad nueva tiene对应的factory en `game_core/factory/`.
