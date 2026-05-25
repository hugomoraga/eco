from typing import Callable

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import VSplit, Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.selection import SelectionType


class Selector:
    def __init__(
        self,
        title: str,
        options: list[str],
        format_func: Callable[[str], str] | None = None,
    ):
        self.title = title
        self.options = options
        self.format_func = format_func or (lambda x: x)
        self.selected = 0
        self._result: str | None = None

    def _build_text(self) -> list[tuple[str, str]]:
        lines: list[tuple[str, str]] = []
        lines.append(("", f"  {self.title}  "))
        lines.append(("", "  " + "─" * 40))

        for i, opt in enumerate(self.options):
            text = self.format_func(opt)
            if i == self.selected:
                lines.append(("class:selected", f"  ▶ {text}"))
            else:
                lines.append(("", f"    {text}"))

        lines.append(("", ""))
        lines.append(("class:dim", "  [↑↓] navegar · [Enter] seleccionar · [q] cancelar"))
        return lines

    def run(self) -> str | None:
        kb = KeyBindings()

        @kb.add("c-c", eager=True)
        def cancel(event: object) -> None:
            self._result = None
            event.app.exit()

        @kb.add("q", eager=True)
        def quit(event: object) -> None:
            self._result = None
            event.app.exit()

        @kb.add("s", eager=True)
        @kb.add(Keys.Down, eager=True)
        def down(event: object) -> None:
            if self.options:
                self.selected = (self.selected + 1) % len(self.options)

        @kb.add("w", eager=True)
        @kb.add(Keys.Up, eager=True)
        def up(event: object) -> None:
            if self.options:
                self.selected = (self.selected - 1) % len(self.options)

        @kb.add(Keys.Enter, eager=True)
        def select(event: object) -> None:
            if self.options:
                self._result = self.options[self.selected]
            event.app.exit()

        app = Application(
            key_bindings=kb,
            use_alternate_screen=False,
        )

        def get_style() -> str:
            return """
            class:selected { color: #00D4FF; bold: true; }
            class:dim { color: #666666; dim: true; }
            """

        from prompt_toolkit.styles import Style
        from prompt_toolkit.layout.containers import WindowAlign

        text_control = FormattedTextControl(
            text=self._build_text,
            focusable=False,
        )

        window = Window(
            content=text_control,
            style="class:selector",
        )

        app.layout = Layout(window)
        app.renderer.app = app

        style = Style.from_dict({
            "selector": "bg:#1a1a1a #e0e0e0",
            "selected": "#00D4FF bold",
            "dim": "#666666 dim",
        })

        try:
            app.run(styled_style=style)
        except Exception:
            return self._fallback_select()

        return self._result

    def _fallback_select(self) -> str | None:
        print(f"\n  {self.title}")
        print("  " + "─" * 40)
        for i, opt in enumerate(self.options):
            marker = "▶" if i == self.selected else " "
            print(f"  {marker} {self.format_func(opt)}")
        print("  [↑↓] navegar · [Enter] seleccionar · [q] cancelar")

        while True:
            try:
                key = input("\n  Tu eleccion: ")
                if key == "q":
                    return None
                elif key == "s" or key == "j":
                    self.selected = (self.selected + 1) % len(self.options)
                elif key == "w" or key == "k":
                    self.selected = (self.selected - 1) % len(self.options)
                elif key == "" or key == "\n":
                    return self.options[self.selected]
                elif key.isdigit():
                    idx = int(key) - 1
                    if 0 <= idx < len(self.options):
                        return self.options[idx]
                print(f"\n  {self.title}")
                print("  " + "─" * 40)
                for i, opt in enumerate(self.options):
                    marker = "▶" if i == self.selected else " "
                    print(f"  {marker} {self.format_func(opt)}")
                print("  [↑↓] navegar · [Enter] seleccionar · [q] cancelar")
            except (EOFError, KeyboardInterrupt):
                return None