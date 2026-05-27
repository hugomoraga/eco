"""
resonance_score.py — ResonanceScore value object.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResonanceScore(BaseModel):
    """
    A single resonance (essence) with its weight value.

    Attributes:
        resonance_id: ID of the essence (thelema, anarchism, etc)
        value: Weight 0-100
    """
    resonance_id: str
    value: float = Field(ge=0, le=100)

    def to_key(self) -> str:
        return self.resonance_id