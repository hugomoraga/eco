from __future__ import annotations

import os
from pathlib import Path

import yaml

LANGUAGE = os.getenv("ECO_LANG", "es")
SUPPORTED = ["es", "en"]

if LANGUAGE not in SUPPORTED:
    LANGUAGE = "es"

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