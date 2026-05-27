"""
Tests for adapters module - hexagonal architecture adapter layer.
"""
from __future__ import annotations

import pytest

from infra.ai.base import GameAdapter
from adapters.player_input.base import InputSource
from adapters.player_input.autoplay import AutoplayInputSource
from adapters.player_input.player import PlayerInputSource
from adapters.player_input.hybrid import HybridInputSource
from adapters.player_input.factory import (
    create_input_source,
    create_input_source_for_mode,
)
from infra.ai import HumanGameAdapter, AIGameAdapter
