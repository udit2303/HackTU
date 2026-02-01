"""
Enums for the EWS (Early Warning System).

All enums are string-based for JSON serialization compatibility.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classification for hazards."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class HazardType(str, Enum):
    """Types of hazards monitored by the system."""

    LANDSLIDE = "landslide"
    SUBSIDENCE = "subsidence"


class TimeHorizon(str, Enum):
    """Time horizons for predictions."""

    HOURS_6 = "6h"
    HOURS_24 = "24h"
    HOURS_72 = "72h"
    DAYS_7 = "7d"


class HeatmapLayer(str, Enum):
    """Available heatmap layers for visualization."""

    LANDSLIDE_RISK = "landslide_risk"
    SUBSIDENCE_RISK = "subsidence_risk"
    SOIL_MOISTURE = "soil_moisture"
    DISPLACEMENT_RATE = "displacement_rate"


class HeatmapResolution(str, Enum):
    """Resolution levels for heatmap generation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SimulationType(str, Enum):
    """Types of scenario simulations."""

    RAINFALL = "rainfall"
    SOIL_SATURATION = "soil_saturation"
    GROUNDWATER_RISE = "groundwater_rise"
    LOAD_INCREASE = "load_increase"
