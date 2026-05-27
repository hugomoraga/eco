"""
simulation.py — Backward compatibility alias.

Use core.systems.simulation_engine for new code.
This module re-exports SimulationEngine for backward compatibility.
"""

from core.application.processors.simulation_engine import SimulationEngine

__all__ = ["SimulationEngine"]
