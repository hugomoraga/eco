"""
ECO theme system - configurable color palettes.
Copied from posting's theme architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EcoColors:
    primary: str = "#C45AFF"
    secondary: str = "#a684e8"
    background: str = "#0F0F1F"
    surface: str = "#1E1E3F"
    panel: str = "#2D2B55"
    accent: str = "#FF69B4"
    text: str = "#E0E0E0"
    text_primary: str = "#FFFFFF"
    text_muted: str = "#888888"
    text_accent: str = "#FF79C6"
    error: str = "#FF4500"
    warning: str = "#FFD700"
    success: str = "#00FA9A"


@dataclass
class EcoTheme:
    name: str = "galaxy"
    colors: EcoColors = field(default_factory=EcoColors)
    description: str = ""


DEFAULT_THEME = EcoTheme(name="galaxy", colors=EcoColors())


THEMES: dict[str, EcoTheme] = {
    "galaxy": EcoTheme(
        name="galaxy",
        colors=EcoColors(
            primary="#C45AFF",
            secondary="#a684e8",
            background="#0F0F1F",
            surface="#1E1E3F",
            panel="#2D2B55",
            accent="#FF69B4",
            text="#E0E0E0",
            text_primary="#FFFFFF",
            text_muted="#888888",
            text_accent="#FF79C6",
            error="#FF4500",
            warning="#FFD700",
            success="#00FA9A",
        ),
        description="Deep purple cosmic theme",
    ),
    "nebula": EcoTheme(
        name="nebula",
        colors=EcoColors(
            primary="#4A9CFF",
            secondary="#66D9EF",
            background="#0D2137",
            surface="#193549",
            panel="#1F4662",
            accent="#FF79C6",
            text="#E0E0E0",
            text_primary="#FFFFFF",
            text_muted="#888888",
            text_accent="#FF79C6",
            error="#FF5555",
            warning="#FFB454",
            success="#50FA7B",
        ),
        description="Blue nebula theme",
    ),
    "aurora": EcoTheme(
        name="aurora",
        colors=EcoColors(
            primary="#45FFB3",
            secondary="#A1FCDF",
            background="#0A1A2F",
            surface="#142942",
            panel="#1E3655",
            accent="#DF7BFF",
            text="#E0E0E0",
            text_primary="#FFFFFF",
            text_muted="#888888",
            text_accent="#DF7BFF",
            error="#FF6B6B",
            warning="#FFE156",
            success="#64FFDA",
        ),
        description="Vibrant aurora theme",
    ),
    "hacker": EcoTheme(
        name="hacker",
        colors=EcoColors(
            primary="#00FF00",
            secondary="#3A9F3A",
            background="#000000",
            surface="#0A0A0A",
            panel="#111111",
            accent="#00FF33",
            text="#00FF00",
            text_primary="#00FF00",
            text_muted="#008800",
            text_accent="#00FF33",
            error="#FF0000",
            warning="#00FF66",
            success="#00DD00",
        ),
        description="Classic hacker green",
    ),
    "sunset": EcoTheme(
        name="sunset",
        colors=EcoColors(
            primary="#FF7E5F",
            secondary="#FEB47B",
            background="#2B2139",
            surface="#362C47",
            panel="#413555",
            accent="#B983FF",
            text="#E0E0E0",
            text_primary="#FFFFFF",
            text_muted="#888888",
            text_accent="#B983FF",
            error="#FF5757",
            warning="#FFD93D",
            success="#98D8AA",
        ),
        description="Warm sunset tones",
    ),
}


def get_theme(name: str) -> EcoTheme:
    return THEMES.get(name, DEFAULT_THEME)