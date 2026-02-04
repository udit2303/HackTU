from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry, Raster
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class SimulationStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    POSTPROCESSING = "POSTPROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CalamityType(str, enum.Enum):
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"


class ZoneType(str, enum.Enum):
    FALLOUT = "FALLOUT"
    CRITICAL_RADIUS = "CRITICAL_RADIUS"
    SECONDARY_SPREAD = "SECONDARY_SPREAD"


class PredictiveToxicitySimulation(Base):
    __tablename__ = "predictive_toxicity_simulations"

    simulation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    site_id = Column(String, nullable=False)
    calamity_type = Column(SQLEnum(CalamityType), nullable=False)
    magnitude = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    status = Column(SQLEnum(SimulationStatus), nullable=False, default=SimulationStatus.QUEUED)
    engine_name = Column(String, nullable=False)
    engine_version = Column(String, nullable=False)
    parameter_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)


class PredictiveToxicityMetrics(Base):
    __tablename__ = "predictive_toxicity_metrics"

    simulation_id = Column(UUID(as_uuid=True), primary_key=True)
    critical_radius_km = Column(Float, nullable=False)
    estimated_population = Column(Integer, nullable=False)
    affected_agri_land_acres = Column(Float, nullable=False)
    primary_toxins = Column(JSON, nullable=False)
    health_risks = Column(JSON, nullable=False)
    metrics_blob = Column(JSON, nullable=True)


class PredictiveToxicityImpactZone(Base):
    __tablename__ = "predictive_toxicity_impact_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    zone_type = Column(SQLEnum(ZoneType), nullable=False)
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    area_sq_km = Column(Float, nullable=False)
    properties = Column(JSON, nullable=True)


class PredictiveToxicityRaster(Base):
    __tablename__ = "predictive_toxicity_rasters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    raster_type = Column(String, nullable=False)
    raster = Column(Raster, nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    raster_metadata = Column(JSON, nullable=True)
