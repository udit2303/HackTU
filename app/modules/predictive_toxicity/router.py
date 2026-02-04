from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db.session import get_db
from app.core.security import get_current_user
from .schemas import (
    ToxicitySimulationCreate, ToxicitySimulationCreateResponse, 
    ToxicitySimulationStatusResponse, ToxicityRiskProfileResponse, 
    ToxicityGeometryResponse, ToxicitySimulationListResponse
)
from .service import PredictiveToxicityService


router = APIRouter(prefix="/predictive-toxicity", tags=["predictive-toxicity"])


def get_service(db: Session = Depends(get_db)) -> PredictiveToxicityService:
    """Dependency to get service instance"""
    return PredictiveToxicityService(db)


@router.post("", response_model=ToxicitySimulationCreateResponse, status_code=status.HTTP_201_CREATED)
def create_simulation(
    data: ToxicitySimulationCreate,
    current_user: dict = Depends(get_current_user),
    service: PredictiveToxicityService = Depends(get_service)
):
    """
    Create a new predictive toxicity simulation.
    Queued for asynchronous execution.
    """
    return service.create_simulation(current_user["user_id"], data)


@router.get("/{simulation_id}/status", response_model=ToxicitySimulationStatusResponse)
def get_simulation_status(
    simulation_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: PredictiveToxicityService = Depends(get_service)
):
    """Fetch current lifecycle state of a simulation"""
    result = service.get_simulation_status(simulation_id, current_user["user_id"])
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    return result


@router.get("/{simulation_id}/risk-profile", response_model=ToxicityRiskProfileResponse)
def get_simulation_risk_profile(
    simulation_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: PredictiveToxicityService = Depends(get_service)
):
    """
    Fetch computed toxicity risk metrics.
    Returns 202 if simulation is not completed.
    Returns 422 if simulation failed.
    """
    result, error_code = service.get_simulation_risk_profile(
        simulation_id, 
        current_user["user_id"]
    )
    
    if error_code == 202:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Simulation is still processing"
        )
    
    if error_code == 422:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Simulation failed or metrics not available"
        )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    return result


@router.get("/{simulation_id}/geometry", response_model=ToxicityGeometryResponse)
def get_simulation_geometry(
    simulation_id: UUID,
    bbox: Optional[str] = Query(None, description="Spatial bounding box (minx,miny,maxx,maxy)"),
    simplify: Optional[float] = Query(None, description="Simplification tolerance"),
    current_user: dict = Depends(get_current_user),
    service: PredictiveToxicityService = Depends(get_service)
):
    """Fetch geospatial fallout zones as GeoJSON in EPSG:4326"""
    result = service.get_simulation_geometry(
        simulation_id, 
        current_user["user_id"], 
        bbox, 
        simplify
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation or geometry not found"
        )
    return result


@router.get("", response_model=ToxicitySimulationListResponse)
def list_simulations(
    site_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    calamity_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: PredictiveToxicityService = Depends(get_service)
):
    """Paginated discovery and filtering of user's simulations"""
    return service.list_simulations(
        user_id=current_user["user_id"],
        site_id=site_id,
        status=status,
        calamity_type=calamity_type,
        limit=limit,
        offset=offset
    )