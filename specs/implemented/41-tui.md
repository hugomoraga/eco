# 41 - TUI (Terminal UI)

**Estado:** deprecated → reemplazada por spec-43
**Creado:** 2026-05-24
**Última actualización:** 2026-05-24
**Dependencias:** 01, 02, 33
**Reemplazada por:** [spec-43](../43-ui.md)

---

## Contexto

Esta spec necesita actualizarse para reflejar la nueva arquitectura definida en spec-33. La implementación actual mezclaba input y display en las mismas clases.

## Arquitectura Actual (a corregir)

```
┌──────────────────────────────────────────────────────┐
│                   SimulationEngine                    │
│  (core, headless, observer-based)                    │
└────────────────────┬─────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
 ┌──────────┐  ┌───────────┐  ┌───────────┐
 │ DebugLog │  │  Input    │  │ Observers │
 │ (file)   │  │  Source   │  │ (display) │
 └──────────┘  └───────────┘  └───────────┘
```

## Problemas en la spec actual

1. **Mezcla display + input** — La spec sugiere que TUIRenderer maneja input, pero en la nueva arquitectura el input está en `TUIInputSource` y el display en `ConsoleDisplay`/`TUIRenderer`

2. **InteractiveMenu mal ubicado** — `InteractiveMenu` está en `tui.py` (display) pero debería estar en `input/tui.py` o ser parte de `TUIInputSource`

3. **Flujo incorrecto** — La spec dice "render_full() pinta el frame, luego InteractiveMenu.run()" pero el flujo correcto es:
   - Engine notifica observers (on_turn_start)
   - Observer (ConsoleDisplay) renderiza a stdout
   - Engine llama input_source.get_action()
   - TUIInputSource recibe input

4. **Colores duplicados** — La spec 41 lista colors, pero en spec-33 ya están definidos en `C` class de `tui.py`

## Items a Corregir

### 1. TUIRenderer → solo display, no input

```
game_core/engine/tui.py
├── C (color class — palette only)
├── EMOJIS, METRIC_NAMES, METRIC_EMOJI (constants)
├── TUIRenderer — renders to stdout, no input handling
└── InteractiveMenu → mover a input/tui.py
```

### 2. InteractiveMenu → pertenece a input

```
game_core/input/tui.py
├── TUIInputSource
│   ├── get_action() — returns action name string
│   ├── _renderer (TUIRenderer instance for display)
│   └── _menu (InteractiveMenu for arrow keys)
└── InteractiveMenu — arrow key capture, returns action name
```

### 3. Flujo correcto

```
run_turn():
  1. _notify("on_turn_start", turn, world)
     → ConsoleDisplay usa TUIRenderer.render_full()

  2. action_name = input_source.get_action(turn, world)
     → TUIInputSource:
        a. Render frame (TUIRenderer.render_full())
        b. Try InteractiveMenu.run() (arrow keys)
        c. Fallback to text input
        d. Return action name string

  3. execute action

  4. _notify("on_turn_end", ...)
```

### 4. Separar concerns

| Clase | Responsabilidad |
|-------|-----------------|
| `TUIRenderer` | Render frame, colors, box-drawing — no input |
| `ConsoleDisplay` | Observer que renderiza events a stdout |
| `TUIInputSource` | Captura input, devuelve action name |
| `InteractiveMenu` | Arrow key capture, menu navigation |

## Acciones

- [ ] Mover `InteractiveMenu` de `engine/tui.py` a `input/tui.py`
- [ ] Limpiar `engine/tui.py` — solo TUIRenderer + C class
- [ ] Actualizar TUIInputSource para usar InteractiveMenu desde su módulo
- [ ] Eliminar duplicación de colors (referenciar spec-33)
- [ ] Verificar que el flujo funciona en terminal real

## Status History

- 2026-05-24: draft created (before architecture refactor)
- 2026-05-24: marked for refactor — contradicts spec-33 decisions
- 2026-05-24: deprecated — reemplazada por spec-43

---

## Deprecación

Esta spec contenía notas de refactor para separar input de display, y lecciones aprendidas del sistema viejo con blessed. Esas decisiones fueron incorporadas en [spec-43](../43-ui.md).

El `game_core/engine/tui.py` que mencionaba sigue existiendo como código legacy. La implementación actual está en `ui_core/` según la spec-43.