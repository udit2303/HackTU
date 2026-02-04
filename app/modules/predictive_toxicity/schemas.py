from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class CalamityType(str, Enum):
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"


class SimulationStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    POSTPROCESSING = "POSTPROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ZoneType(str, Enum):
    FALLOUT = "FALLOUT"
    CRITICAL_RADIUS = "CRITICAL_RADIUS"
    SECONDARY_SPREAD = "SECONDARY_SPREAD"


# Request Schemas
class ToxicitySimulationCreate(BaseModel):
    site_id: str
    calamity_type: CalamityType
    magnitude: float
    unit: str
    scenario_metadata: Optional[dict] = None


# Response Schemas
class ToxicitySimulationCreateResponse(BaseModel):
    simulation_id: UUID
    status: SimulationStatus
    engine: str
    engine_version: str


class ToxicitySimulationStatusResponse(BaseModel):
    simulation_id: UUID
    status: SimulationStatus
    progress: Optional[float] = Field(None, ge=0, le=1)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AffectedMetrics(BaseModel):
    estimated_population: int
    affected_agri_land_acres: float
    primary_toxins: List[str]
    health_risks: List[str]


class ToxicityRiskProfileResponse(BaseModel):
    simulation_id: UUID
    critical_radius_km: float
    affected_metrics: AffectedMetrics
    confidence_score: Optional[float] = None
    dataset_versions: dict
    engine_version: str


class ToxicityRange(BaseModel):
    min_ppm: float
    max_ppm: float


class ImpactZone(BaseModel):
    zone_type: ZoneType
    geometry: dict  # GeoJSON Polygon
    area_sq_km: float
    toxicity_range_ppm: Optional[ToxicityRange] = None


class ToxicityGeometryResponse(BaseModel):
    simulation_id: UUID
    zones: List[ImpactZone]


class ToxicitySimulationListItem(BaseModel):
    simulation_id: UUID
    site_id: str
    calamity_type: str
    status: str
    created_at: datetime


class ToxicitySimulationListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ToxicitySimulationListItem]