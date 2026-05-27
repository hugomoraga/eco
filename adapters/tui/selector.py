import io
from collections.abc import Callable

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style


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
                lines.append(("selected", f"  ▶ {text}"))
            else:
                lines.append(("", f"    {text}"))

        lines.append(("", ""))
        lines.append(("dim", "  [↑↓/ws] navegar · [Enter] seleccionar · [q] cancelar"))
        return lines

    def run(self) -> str | None:
        """Run selector with keyboard navigation."""
        import sys

        if sys.stdin.isatty() and not self._is_piped_input():
            return self._interactive_select()

        return self._numbered_select()

    def _is_piped_input(self) -> bool:
        """Check if stdin has piped input (not a real TTY)."""
        import sys

        try:
            return not sys.stdin.isatty() or sys.stdin.seekable() is False
        except (AttributeError, io.UnsupportedOperation):
            return False

    def _numbered_select(self) -> str | None:
        """Simple numbered selection (works without TTY)."""
        import re

        print(f"\n  {self.title}")
        print("  " + "─" * 40)
        for i, opt in enumerate(self.options, 1):
            print(f"  {i}. {self.format_func(opt)}")
        print("  (escribe el numero)")

        try:
            raw_input = input("\n  Tu eleccion: ")
            clean_input = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", raw_input).strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if not clean_input:
            return self.options[self.selected] if self.options else None
        if clean_input == "q":
            return None
        if clean_input.isdigit():
            idx = int(clean_input) - 1
            if 0 <= idx < len(self.options):
                return self.options[idx]
        if clean_input in self.options:
            return clean_input

        return self.options[self.selected] if self.options else None

    def _interactive_select(self) -> str | None:
        """Interactive selection with arrow keys (requires TTY)."""
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
            self.selected = (self.selected + 1) % len(self.options) if self.options else 0
            event.app.invalidate()

        @kb.add("w", eager=True)
        @kb.add(Keys.Up, eager=True)
        def up(event: object) -> None:
            self.selected = (self.selected - 1) % len(self.options) if self.options else 0
            event.app.invalidate()

        @kb.add(Keys.Enter, eager=True)
        def select(event: object) -> None:
            if self.options:
                self._result = self.options[self.selected]
            event.app.exit()

        @kb.add("1")
        @kb.add("2")
        @kb.add("3")
        @kb.add("4")
        @kb.add("5")
        @kb.add("6")
        @kb.add("7")
        @kb.add("8")
        def number(event: object) -> None:
            key_char = event.key_sequence[-1].key.text if event.key_sequence else ""
            num = int(key_char) if key_char.isdigit() else 0
            if 0 < num <= len(self.options):
                self._result = self.options[num - 1]
                event.app.exit()

        style = Style.from_dict(
            {
                "selected": "#00D4FF bold",
                "dim": "#666666 dim",
            }
        )

        text_control = FormattedTextControl(
            text=lambda: self._build_text(),
            focusable=False,
        )

        window = Window(content=text_control)

        app = Application(
            key_bindings=kb,
            layout=Layout(window),
            style=style,
            full_screen=False,
            erase_when_done=True,
        )

        try:
            app.run()
        except Exception:
            return self._numbered_select()

        return self._result
