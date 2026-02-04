from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from .models import (
    PredictiveToxicitySimulation, PredictiveToxicityMetrics, 
    PredictiveToxicityImpactZone, PredictiveToxicityRaster,
    SimulationStatus, CalamityType, ZoneType
)


def create_simulation(
    db: Session,
    user_id: UUID,
    site_id: str,
    calamity_type: CalamityType,
    magnitude: float,
    unit: str,
    engine_name: str,
    engine_version: str,
    parameter_hash: str
) -> PredictiveToxicitySimulation:
    simulation = PredictiveToxicitySimulation(
        user_id=user_id,
        site_id=site_id,
        calamity_type=calamity_type,
        magnitude=magnitude,
        unit=unit,
        engine_name=engine_name,
        engine_version=engine_version,
        parameter_hash=parameter_hash,
        status=SimulationStatus.QUEUED
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    return simulation


def get_simulation_by_id(
    db: Session, 
    simulation_id: UUID, 
    user_id: UUID
) -> Optional[PredictiveToxicitySimulation]:
    return db.query(PredictiveToxicitySimulation).filter(
        PredictiveToxicitySimulation.simulation_id == simulation_id,
        PredictiveToxicitySimulation.user_id == user_id
    ).first()


def update_simulation_status(
    db: Session,
    simulation_id: UUID,
    user_id: UUID,
    status: SimulationStatus,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    error_message: Optional[str] = None
) -> Optional[PredictiveToxicitySimulation]:
    simulation = get_simulation_by_id(db, simulation_id, user_id)
    if not simulation:
        return None
    
    simulation.status = status
    if started_at:
        simulation.started_at = started_at
    if completed_at:
        simulation.completed_at = completed_at
    if error_message:
        simulation.error_message = error_message
    
    db.commit()
    db.refresh(simulation)
    return simulation


def create_simulation_metrics(
    db: Session,
    simulation_id: UUID,
    critical_radius_km: float,
    estimated_population: int,
    affected_agri_land_acres: float,
    primary_toxins: List[str],
    health_risks: List[str],
    metrics_blob: Optional[dict] = None
) -> PredictiveToxicityMetrics:
    metrics = PredictiveToxicityMetrics(
        simulation_id=simulation_id,
        critical_radius_km=critical_radius_km,
        estimated_population=estimated_population,
        affected_agri_land_acres=affected_agri_land_acres,
        primary_toxins=primary_toxins,
        health_risks=health_risks,
        metrics_blob=metrics_blob
    )
    db.add(metrics)
    db.commit()
    db.refresh(metrics)
    return metrics


def get_simulation_metrics(
    db: Session, 
    simulation_id: UUID
) -> Optional[PredictiveToxicityMetrics]:
    return db.query(PredictiveToxicityMetrics).filter(
        PredictiveToxicityMetrics.simulation_id == simulation_id
    ).first()


def create_impact_zone(
    db: Session,
    simulation_id: UUID,
    zone_type: ZoneType,
    geometry: str,
    area_sq_km: float,
    properties: Optional[dict] = None
) -> PredictiveToxicityImpactZone:
    zone = PredictiveToxicityImpactZone(
        simulation_id=simulation_id,
        zone_type=zone_type,
        geometry=func.ST_GeomFromText(geometry, 4326),
        area_sq_km=area_sq_km,
        properties=properties
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


def get_impact_zones(
    db: Session,
    simulation_id: UUID,
    bbox: Optional[str] = None,
    simplify: Optional[float] = None
) -> List[PredictiveToxicityImpactZone]:
    query = db.query(PredictiveToxicityImpactZone).filter(
        PredictiveToxicityImpactZone.simulation_id == simulation_id
    )
    
    if bbox:
        bbox_coords = [float(x) for x in bbox.split(',')]
        query = query.filter(
            func.ST_Intersects(
                PredictiveToxicityImpactZone.geometry,
                func.ST_MakeEnvelope(*bbox_coords, 4326)
            )
        )
    
    return query.all()


def create_simulation_raster(
    db: Session,
    simulation_id: UUID,
    raster_type: str,
    raster_data: bytes,
    min_value: float,
    max_value: float,
    metadata: Optional[dict] = None
) -> PredictiveToxicityRaster:
    raster = PredictiveToxicityRaster(
        simulation_id=simulation_id,
        raster_type=raster_type,
        raster=raster_data,
        min_value=min_value,
        max_value=max_value,
        metadata=metadata
    )
    db.add(raster)
    db.commit()
    db.refresh(raster)
    return raster


def list_simulations(
    db: Session,
    user_id: UUID,
    site_id: Optional[str] = None,
    status: Optional[SimulationStatus] = None,
    calamity_type: Optional[CalamityType] = None,
    limit: int = 10,
    offset: int = 0
) -> tuple[List[PredictiveToxicitySimulation], int]:
    query = db.query(PredictiveToxicitySimulation).filter(
        PredictiveToxicitySimulation.user_id == user_id
    )
    
    if site_id:
        query = query.filter(PredictiveToxicitySimulation.site_id == site_id)
    if status:
        query = query.filter(PredictiveToxicitySimulation.status == status)
    if calamity_type:
        query = query.filter(PredictiveToxicitySimulation.calamity_type == calamity_type)
    
    total = query.count()
    items = query.order_by(
        PredictiveToxicitySimulation.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return items, total