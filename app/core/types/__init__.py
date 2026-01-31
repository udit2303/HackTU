"""
Core types and enums for the EWS (Early Warning System).

All shared types and enums used across modules.
"""

from app.core.types.enums import (
    RiskLevel,
    HazardType,
    TimeHorizon,
    HeatmapLayer,
    HeatmapResolution,
    SimulationType,
)

__all__ = [
    "RiskLevel",
    "HazardType",
    "TimeHorizon",
    "HeatmapLayer",
    "HeatmapResolution",
    "SimulationType",
]
