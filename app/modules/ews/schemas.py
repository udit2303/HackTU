"""
Pydantic schemas for the EWS (Early Warning System) module.

All request and response contracts for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.core.types.enums import (
    RiskLevel,
    HazardType,
    TimeHorizon,
    HeatmapLayer,
    HeatmapResolution,
    SimulationType,
)

# ============================================================================
# Nested/Shared Schemas
# ============================================================================


class TimeRange(BaseModel):
    """Time range for analytics queries."""

    from_time: datetime = Field(..., description="Start of time range (ISO-8601)")
    to_time: datetime = Field(..., description="End of time range (ISO-8601)")


class Coordinate(BaseModel):
    """Geographic coordinate (lat/lon)."""

    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lon: float = Field(..., description="Longitude", ge=-180, le=180)


class ScenarioInput(BaseModel):
    """Input parameters for a scenario simulation."""

    type: SimulationType = Field(..., description="Type of scenario to simulate")
    total_mm: Optional[float] = Field(
        None, description="Total rainfall in mm (for RAINFALL scenarios)"
    )
    duration_hours: Optional[int] = Field(
        None, description="Duration in hours (for RAINFALL scenarios)"
    )
    rise_meters: Optional[float] = Field(
        None, description="Groundwater rise in meters (for GROUNDWATER_RISE scenarios)"
    )


class ExpectedWindow(BaseModel):
    """Expected time window for a hazard event."""

    from_time: datetime = Field(..., description="Start of expected window (ISO-8601)")
    to_time: datetime = Field(..., description="End of expected window (ISO-8601)")


class MetricsOutput(BaseModel):
    """Metrics from analytics computation."""

    soil_moisture_avg: float = Field(
        ..., description="Average soil moisture (0.0 to 1.0)"
    )
    displacement_trend_mm_per_month: float = Field(
        ..., description="Displacement trend in mm/month"
    )
    rainfall_accumulation_mm: float = Field(
        ..., description="Rainfall accumulation in mm"
    )


class ScenarioResult(BaseModel):
    """Result of a single scenario simulation."""

    scenario_type: SimulationType = Field(..., description="Type of scenario simulated")
    risk_score: float = Field(
        ..., description="Risk score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    risk_delta: float = Field(..., description="Change from baseline risk")


class GeoJSONGeometry(BaseModel):
    """GeoJSON geometry object."""

    type: str = Field(..., description="Geometry type (e.g., 'Polygon', 'LineString')")
    coordinates: List = Field(..., description="Coordinate array")


class HeatmapFeatureProperties(BaseModel):
    """Properties for a heatmap feature."""

    risk_score: float = Field(
        ..., description="Risk score for this cell (0.0 to 1.0)", ge=0.0, le=1.0
    )
    risk_level: RiskLevel = Field(..., description="Risk level classification")


class HeatmapFeature(BaseModel):
    """GeoJSON Feature for heatmap."""

    type: str = Field(default="Feature", description="Feature type")
    geometry: GeoJSONGeometry = Field(..., description="Polygon geometry")
    properties: HeatmapFeatureProperties = Field(..., description="Risk properties")


class EvacuationRoute(BaseModel):
    """Evacuation route with risk and timing information."""

    route_id: str = Field(..., description="Unique route identifier")
    risk_score: float = Field(
        ..., description="Risk score for this route (0.0 to 1.0)", ge=0.0, le=1.0
    )
    eta_minutes: int = Field(..., description="Estimated time of arrival in minutes")
    geometry: GeoJSONGeometry = Field(
        ..., description="LineString geometry of the route"
    )


# ============================================================================
# Request Schemas
# ============================================================================


class AnalyticsRequest(BaseModel):
    """Request for analytics computation."""

    area_id: int = Field(..., description="ID of the area to analyze")
    time_range: TimeRange = Field(..., description="Time range for analysis")


class PredictionRequest(BaseModel):
    """Request for hazard prediction."""

    area_id: int = Field(..., description="ID of the area to predict for")
    hazard: HazardType = Field(..., description="Type of hazard to predict")
    horizon: TimeHorizon = Field(..., description="Prediction time horizon")


class ScenarioRequest(BaseModel):
    """Request for scenario simulation."""

    area_id: int = Field(..., description="ID of the area to simulate")
    hazard: HazardType = Field(..., description="Type of hazard to simulate")
    scenarios: List[ScenarioInput] = Field(
        ..., description="List of scenarios to simulate"
    )


class HeatmapRequest(BaseModel):
    """Request for heatmap generation."""

    area_id: int = Field(..., description="ID of the area to generate heatmap for")
    hazard: HazardType = Field(..., description="Type of hazard to visualize")
    layer: HeatmapLayer = Field(..., description="Heatmap layer to generate")
    resolution: HeatmapResolution = Field(..., description="Resolution level")


class EvacuationRequest(BaseModel):
    """Request for evacuation route computation."""

    area_id: int = Field(..., description="ID of the area")
    start_points: List[Coordinate] = Field(
        ..., description="Starting points for evacuation"
    )


# ============================================================================
# Response Schemas
# ============================================================================


class AnalyticsResponse(BaseModel):
    """Response from analytics computation."""

    stability_index: float = Field(
        ..., description="Ground stability index (0.0 to 1.0)", ge=0.0, le=1.0
    )
    confidence: float = Field(
        ..., description="Confidence in the analysis (0.0 to 1.0)", ge=0.0, le=1.0
    )
    metrics: MetricsOutput = Field(..., description="Detailed metrics")


class PredictionResponse(BaseModel):
    """Response from hazard prediction."""

    hazard: HazardType = Field(..., description="Type of hazard predicted")
    risk_score: float = Field(
        ..., description="Risk score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    confidence: float = Field(
        ..., description="Confidence in prediction (0.0 to 1.0)", ge=0.0, le=1.0
    )
    expected_window: Optional[ExpectedWindow] = Field(
        None, description="Expected time window for event"
    )


class ScenarioResponse(BaseModel):
    """Response from scenario simulation."""

    baseline_risk: float = Field(
        ..., description="Baseline risk score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    results: List[ScenarioResult] = Field(..., description="Results for each scenario")


class HeatmapResponse(BaseModel):
    """Response from heatmap generation (GeoJSON FeatureCollection)."""

    type: str = Field(default="FeatureCollection", description="GeoJSON type")
    features: List[HeatmapFeature] = Field(..., description="List of heatmap features")


class EvacuationResponse(BaseModel):
    """Response from evacuation route computation."""

    routes: List[EvacuationRoute] = Field(..., description="List of evacuation routes")


class PredictionHistoryItem(BaseModel):
    """Single prediction history record."""

    id: int = Field(..., description="Prediction record ID")
    area_id: int = Field(..., description="Area ID")
    hazard: HazardType = Field(..., description="Hazard type")
    horizon: TimeHorizon = Field(..., description="Time horizon")
    risk_score: float = Field(..., description="Risk score (0.0 to 1.0)")
    risk_level: RiskLevel = Field(..., description="Risk level")
    confidence: float = Field(..., description="Confidence (0.0 to 1.0)")
    expected_window_from: Optional[datetime] = Field(
        None, description="Expected window start"
    )
    expected_window_to: Optional[datetime] = Field(
        None, description="Expected window end"
    )
    created_at: datetime = Field(..., description="When prediction was made")

    class Config:
        from_attributes = True


class PredictionHistoryResponse(BaseModel):
    """Response containing prediction history."""

    predictions: List[PredictionHistoryItem] = Field(
        ..., description="List of historical predictions"
    )
    total: int = Field(..., description="Total number of predictions")
