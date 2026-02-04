from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import hashlib
import json

from . import repository
from .schemas import (
    ToxicitySimulationCreate, ToxicitySimulationCreateResponse, 
    ToxicitySimulationStatusResponse, ToxicityRiskProfileResponse, 
    ToxicityGeometryResponse, ToxicitySimulationListResponse,
    AffectedMetrics, ImpactZone, ToxicitySimulationListItem
)
from .models import SimulationStatus, CalamityType


class PredictiveToxicityService:
    """Service layer for predictive toxicity business logic"""
    
    ENGINE_NAME = "PredictiveToxicityEngine"
    ENGINE_VERSION = "1.0.0"
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_simulation(
        self, 
        user_id: UUID, 
        data: ToxicitySimulationCreate
    ) -> ToxicitySimulationCreateResponse:
        """Create and queue a new simulation for authenticated user"""
        parameter_hash = self._generate_parameter_hash(
            data.site_id, data.calamity_type.value, data.magnitude, data.unit
        )
        
        simulation = repository.create_simulation(
            db=self.db,
            user_id=user_id,
            site_id=data.site_id,
            calamity_type=CalamityType(data.calamity_type.value),
            magnitude=data.magnitude,
            unit=data.unit,
            engine_name=self.ENGINE_NAME,
            engine_version=self.ENGINE_VERSION,
            parameter_hash=parameter_hash
        )
        
        self._queue_simulation_processing(simulation.simulation_id)
        
        return ToxicitySimulationCreateResponse(
            simulation_id=simulation.simulation_id,
            status=SimulationStatus.QUEUED,
            engine=self.ENGINE_NAME,
            engine_version=self.ENGINE_VERSION
        )
    
    def get_simulation_status(
        self, 
        simulation_id: UUID, 
        user_id: UUID
    ) -> Optional[ToxicitySimulationStatusResponse]:
        """Get current simulation lifecycle status with ownership check"""
        simulation = repository.get_simulation_by_id(self.db, simulation_id, user_id)
        if not simulation:
            return None
        
        progress = self._calculate_progress(simulation.status)
        
        return ToxicitySimulationStatusResponse(
            simulation_id=simulation.simulation_id,
            status=simulation.status,
            progress=progress,
            started_at=simulation.started_at,
            completed_at=simulation.completed_at,
            error_message=simulation.error_message
        )
    
    def get_simulation_risk_profile(
        self, 
        simulation_id: UUID,
        user_id: UUID
    ) -> tuple[Optional[ToxicityRiskProfileResponse], Optional[int]]:
        """
        Get computed risk metrics with ownership check
        Returns (response, status_code) where status_code indicates:
        - None: Success (200)
        - 202: Simulation not completed
        - 422: Simulation failed
        """
        simulation = repository.get_simulation_by_id(self.db, simulation_id, user_id)
        if not simulation:
            return None, None
        
        if simulation.status in [
            SimulationStatus.QUEUED, 
            SimulationStatus.RUNNING, 
            SimulationStatus.POSTPROCESSING
        ]:
            return None, 202
        
        if simulation.status == SimulationStatus.FAILED:
            return None, 422
        
        metrics = repository.get_simulation_metrics(self.db, simulation_id)
        if not metrics:
            return None, 422
        
        return self._build_risk_profile_response(simulation, metrics), None
    
    def get_simulation_geometry(
        self,
        simulation_id: UUID,
        user_id: UUID,
        bbox: Optional[str] = None,
        simplify: Optional[float] = None
    ) -> Optional[ToxicityGeometryResponse]:
        """Get geospatial impact zones with ownership check"""
        simulation = repository.get_simulation_by_id(self.db, simulation_id, user_id)
        if not simulation:
            return None
        
        zones = repository.get_impact_zones(self.db, simulation_id, bbox, simplify)
        
        impact_zones = []
        for zone in zones:
            # Use ORM to get GeoJSON
            geometry_result = self.db.query(
                func.ST_AsGeoJSON(zone.geometry)
            ).scalar()
            
            toxicity_range = None
            if zone.properties and "toxicity_ppm" in zone.properties:
                toxicity_range = zone.properties["toxicity_ppm"]
            
            impact_zones.append(ImpactZone(
                zone_type=zone.zone_type,
                geometry=json.loads(geometry_result) if geometry_result else {},
                area_sq_km=zone.area_sq_km,
                toxicity_range_ppm=toxicity_range
            ))
        
        return ToxicityGeometryResponse(
            simulation_id=simulation_id,
            zones=impact_zones
        )
    
    def list_simulations(
        self,
        user_id: UUID,
        site_id: Optional[str] = None,
        status: Optional[str] = None,
        calamity_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> ToxicitySimulationListResponse:
        """List simulations with filtering for authenticated user"""
        status_enum = SimulationStatus(status) if status else None
        calamity_enum = CalamityType(calamity_type) if calamity_type else None
        
        simulations, total = repository.list_simulations(
            db=self.db,
            user_id=user_id,
            site_id=site_id,
            status=status_enum,
            calamity_type=calamity_enum,
            limit=limit,
            offset=offset
        )
        
        items = [
            ToxicitySimulationListItem(
                simulation_id=sim.simulation_id,
                site_id=sim.site_id,
                calamity_type=sim.calamity_type.value,
                status=sim.status.value,
                created_at=sim.created_at
            )
            for sim in simulations
        ]
        
        return ToxicitySimulationListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items
        )
    
    def _generate_parameter_hash(
        self, 
        site_id: str, 
        calamity_type: str, 
        magnitude: float, 
        unit: str
    ) -> str:
        """Generate deterministic hash from simulation parameters"""
        params = f"{site_id}:{calamity_type}:{magnitude}:{unit}"
        return hashlib.sha256(params.encode()).hexdigest()
    
    def _queue_simulation_processing(self, simulation_id: UUID):
        """Queue simulation for background processing (Celery integration point)"""
        # Placeholder for Celery task dispatch
        pass
    
    def _calculate_progress(self, status: SimulationStatus) -> Optional[float]:
        """Calculate progress based on status"""
        progress_map = {
            SimulationStatus.RUNNING: 0.5,
            SimulationStatus.POSTPROCESSING: 0.9,
            SimulationStatus.COMPLETED: 1.0
        }
        return progress_map.get(status)
    
    def _build_risk_profile_response(
        self, 
        simulation, 
        metrics
    ) -> ToxicityRiskProfileResponse:
        """Build risk profile response from simulation and metrics"""
        return ToxicityRiskProfileResponse(
            simulation_id=simulation.simulation_id,
            critical_radius_km=metrics.critical_radius_km,
            affected_metrics=AffectedMetrics(
                estimated_population=metrics.estimated_population,
                affected_agri_land_acres=metrics.affected_agri_land_acres,
                primary_toxins=metrics.primary_toxins,
                health_risks=metrics.health_risks
            ),
            confidence_score=metrics.metrics_blob.get("confidence_score") if metrics.metrics_blob else None,
            dataset_versions=metrics.metrics_blob.get("dataset_versions", {}) if metrics.metrics_blob else {},
            engine_version=simulation.engine_version
        )