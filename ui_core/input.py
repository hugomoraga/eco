from typing import Callable
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

COMMANDS: dict[str, Callable] = {}


def command(name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        COMMANDS[name] = func
        return func
    return decorator


class CommandInput:
    _session: PromptSession | None = None

    @classmethod
    def get_session(cls) -> PromptSession:
        if cls._session is None:
            cls._session = PromptSession(
                history=InMemoryHistory(),
                vi_mode=False,
                enable_history_search=True,
                message="► ",
            )
        return cls._session

    @classmethod
    def get_command(cls, prompt: str = "► ") -> str:
        session = cls.get_session()
        try:
            return session.prompt(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    @classmethod
    def get_number(cls, prompt: str = "► ") -> int | None:
        cmd = cls.get_command(prompt)
        try:
            return int(cmd)
        except ValueError:
            return None

    @classmethod
    def get_choice(cls, options: list[str], prompt: str = "► ") -> int | None:
        cmd = cls.get_command(prompt)
        if not cmd:
            return None
        try:
            idx = int(cmd) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        return None


@command("help")
def cmd_help(interface: object, args: list[str]) -> str:
    lines = ["[cyan]Comandos disponibles:[/cyan]", ""]
    for name, func in COMMANDS.items():
        doc = func.__doc__ or ""
        lines.append(f"  [yellow]{name}[/yellow] - {doc.strip()}")
    return "\n".join(lines)


@command("quit")
def cmd_quit(interface: object, args: list[str]) -> str:
    if hasattr(interface, "running"):
        interface.running = False
    return "[yellow]Saliendo...[/yellow]"


@command("save")
def cmd_save(interface: object, args: list[str]) -> str:
    if hasattr(interface, "session"):
        path = args[0] if args else None
        return interface.session.save(path)
    return "[red]Session no disponible[/red]"


@command("load")
def cmd_load(interface: object, args: list[str]) -> str:
    if hasattr(interface, "session"):
        path = args[0] if args else None
        return interface.session.load(path)
    return "[red]Session no disponible[/red]"


@command("history")
def cmd_history(interface: object, args: list[str]) -> str:
    if hasattr(interface, "history"):
        return interface.history.format()
    return "[dim]Sin historial[/dim]"


@command("replay")
def cmd_replay(interface: object, args: list[str]) -> str:
    if not hasattr(interface, "history"):
        return "[dim]Sin historial[/dim]"
    try:
        n = int(args[0]) if args else 1
    except ValueError:
        return "[red]Uso: replay [n][/red]"
    return interface.history.replay(n)