from __future__ import annotations

import os
from pathlib import Path

import yaml

SUPPORTED = ["es", "en"]

_language: str | None = None


def get_lang() -> str:
    """Get current language. Single source of truth."""
    global _language
    if _language is None:
        lang = os.getenv("ECO_LANG", "es")
        _language = lang if lang in SUPPORTED else "es"
    return _language


def set_lang(lang: str) -> None:
    """Set language (for testing or runtime changes)."""
    global _language
    _language = lang if lang in SUPPORTED else "es"


LANGUAGE = get_lang()

I18N_DIR = Path(__file__).parent
_strings = yaml.safe_load((I18N_DIR / f"{LANGUAGE}.yaml").read_text())


def t(key: str, **kwargs) -> str:
    """Get translation. Key format: 'section:subsection:key'"""
    keys = key.split(":")
    value = _strings

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return key

    if kwargs:
        return value.format(**kwargs)
    return value


LANG_PROMPT = {"es": "en español", "en": "in English"}[LANGUAGE]
