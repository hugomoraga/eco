# 52 - Person/Host/Echo Architecture

Refactor del modelo `Person ↔ Host ↔ Echo` para seguir OOP limpio con herencia.

**Status**: draft
**Created**: 2026-05-26
**Depends on**: 51-code-patterns.md

---

## 1. Modelo Actual (Problema)

```
Person (BaseModel)
├── id, name, role, archetype
├── type: "npc" | "player"
├── echo_id (historical link)
├── essence_profile
├── vitality, coherence
├── faction_id, loyalty, influence
└── take_damage(), heal()

Host (BaseModel) ← "pegado" a Person con type="player"
├── id, person_id, echo_id
├── will, presence
├── action_history, last_action_turn
├── active_circle_id, actions_this_turn
├── is_active
└── record_action(), reset_turn_actions()

Echo (BaseModel) = "alma"
├── id, name, essence_profile
├── phase, attributes
├── genealogical_lineage
├── reincarnation_count
├── known_tags, ideas, manifestos, circles
└── get_attribute(), has_tag()
```

**Problemas:**
1. `Host` tiene `will` y `presence` pero `Person` tiene `vitality` y `coherence` —语义不一致
2. `Host.action_history` duplica `Person.action_history` (aunque Person no lo tiene definido)
3. `Person.type="player"` es un flag que controla si está "habitada" — mélange de estado
4. `Echo.reincarnation_count` vive en Echo, pero la lógica de reencarnación está en `reincarnation.py`
5. Mucha indirección: `World` → `hosts` → `persons` → `echoes`

---

## 2. Modelo Propuesto

```
Entity (ABC - abstract base)
└── Person (BaseModel)
    ├── id, name, role, archetype
    ├── essence_profile
    ├── vitality: float = 100.0
    ├── coherence: float = 50.0
    ├── faction_id, loyalty, influence
    ├── take_damage(), heal()
    │
    ├── PlayerPerson (hereda de Person)
    │   ├── echo_id: str
    │   ├── will: float = 50.0
    │   ├── presence: float = 50.0
    │   ├── action_history, last_action_turn
    │   ├── active_circle_id, actions_this_turn
    │   ├── reincarnation_count: int = 0
    │   ├── previous_echo_ids: list[str] = []
    │   ├── record_action()
    │   └── reset_turn_actions()
    │
    └── NPCPerson (hereda de Person)
        └── (sin campos extra por ahora)

Echo (BaseModel) = identidad/alma
├── id, name, essence_profile
├── phase, attributes
├── genealogical_lineage
├── shadow_coherence
├── known_tags, ideas, manifestos, circles
└── get_attribute(), has_tag()

# Ya NO existe Host como entidad separada
```

---

## 3. Cambios Clave

### 3.1 Eliminar `Host` como entidad

`Host` deja de existir. Su funcionalidad pasa a `PlayerPerson`:

| Host campo | PlayerPerson campo | Notes |
|------------|-------------------|-------|
| `id` | heredado de Person | |
| `person_id` | YA NO EXISTE | Se referencia por `PlayerPerson.id` |
| `echo_id` | `echo_id` | Link al Echo |
| `will` | `will` | |
| `presence` | `presence` | |
| `action_history` | `action_history` | |
| `last_action_turn` | `last_action_turn` | |
| `active_circle_id` | `circles[0]` | Simplificado |
| `actions_this_turn` | `actions_this_turn` | |
| `is_active` | `is_active` | |
| `reincarnation_count` | `reincarnation_count` | Movido de Echo |
| `previous_hosts` | `previous_echo_ids` | Renombrado para claridad |

### 3.2 Renombrar `Echo.reincarnation_count`

`Echo.reincarnation_count` → `PlayerPerson.reincarnation_count`

El conteo de reencarnaciones es del recipiente físico, no del alma. El Echo (alma) puede habitar muchos recipientes, el conteo es del recipiente.

### 3.3 Simplificar `World`

```python
# ANTES:
class World:
    echoes: list[Echo]
    hosts: list[Host]      # ←多余的 indirección
    persons: list[Person]

# DESPUÉS:
class World:
    echoes: list[Echo]
    persons: list[Person]  # Incluye PlayerPerson y NPCPerson
    # NO más hosts! Se accede via:
    # - get_player_person() → filter persons where isinstance(..., PlayerPerson)
    # - get_echoes_in_circle(circle_id) → todos los Echo de members
```

### 3.4 Métodos de PlayerPerson

```python
class PlayerPerson(Person):
    def link_echo(self, echo_id: str) -> None:
        """Vincular un Echo a este recipiente."""
        if self.echo_id and self.echo_id != echo_id:
            self.previous_echo_ids.append(self.echo_id)
        self.echo_id = echo_id

    def unlink_echo(self) -> None:
        """Desvincular Echo (por muerte)."""
        self.echo_id = None
        self.is_active = False

    def reincarnate(self, new_echo_id: str) -> None:
        """Reiniciar para nuevo Echo."""
        self.reincarnation_count += 1
        self.link_echo(new_echo_id)
        self.is_active = True
        self.vitality = 100.0
        self.action_history.clear()
        self.last_action_turn.clear()

    def is_available_for_reincarnation(self) -> bool:
        """Verificar si puede recibir un Echo."""
        return not self.is_active and self.vitality > 0
```

---

## 4. Migración Paso a Paso

### Fase 1: Añadir nuevos modelos (sin romper existentes)

1. Crear `PlayerPerson(Person)` con campos de Host
2. Crear `NPCPerson(Person)` como clase marker
3. Mantener `Host` funcionando параллельно

### Fase 2: Migrar Factory

1. `factory/host.py` → crea `PlayerPerson` en vez de `Host`
2. Actualizar `create_host()` → `create_player_person()`
3. Actualizar `create_host_for_echo()` → `create_player_person_for_echo()`

### Fase 3: Migrar Systems

1. `simulation.py`: usar `PlayerPerson` en vez de `Host`
2. `reincarnation.py`: actualizar para usar `PlayerPerson`
3. `World.get_host_for_echo()` → `World.get_player_person_by_echo()`

### Fase 4: Remover Host

1. Eliminar clase `Host` de `entities.py`
2. Eliminar `hosts` de `World`
3. Actualizar todos los imports

---

## 5. API Changes

| Antes | Después |
|-------|---------|
| `create_host(echo_id, world)` | `create_player_person(echo_id, world)` |
| `create_host_for_echo(echo, world)` | `create_player_person_for_echo(echo, world)` |
| `world.hosts` | `world.persons` (filtrar `isinstance(p, PlayerPerson)`) |
| `world.get_host_for_echo(id)` | `world.get_player_person_by_echo(id)` |
| `host.reincarnation_count` (en Echo) | `player_person.reincarnation_count` |

---

## 6. Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `domain/entities.py` | Añadir PlayerPerson, NPCPerson; marcar Host como deprecated |
| `factory/host.py` | Renombrar funciones, retornar PlayerPerson |
| `systems/reincarnation.py` | Usar PlayerPerson |
| `systems/simulation.py` | Remover Host, usar PlayerPerson |
| `factory/__init__.py` | Actualizar exports |
| `domain/__init__.py` | Exports de las nuevas clases |

---

## 7. Open Questions

1. **¿Mantener `Person.type`?** Con herencia, `type` es redundante. Solo usar `isinstance(p, PlayerPerson)`.

2. **¿Qué pasa con NPC spawning?** ¿NPCPerson necesita métodos de spawn o se mantiene como marker class?

3. **¿Migración de datos existente?** Los saves viejos con `Host` necesitarán migración.

---

## 8. Alternativa: Composition over Inheritance

Si la herencia se complica demasiado, considerar composición:

```python
class PlayerPerson(Person):
    incarnation: IncarnationContext  # Envuelve campos de Host

@dataclass
class IncarnationContext:
    echo_id: str
    will: float = 50.0
    presence: float = 50.0
    action_history: list[str] = Field(default_factory=list)
    # ...
```

Esto evita el problema de "diamond inheritance" si PlayerPerson y NPCPerson necesitan divergir.

**Recomendación**: Empezar con herencia simple. Si se complica, migrar a composición.

---

## 9. Metadatos

| Campo | Valor |
|-------|-------|
| Created | 2026-05-26 |
| Status | draft |
| Deps | 51-code-patterns.md |
| Breaking changes | Sí — requiere migración de datos |
| Related | spec-47 (essence system v2) |
