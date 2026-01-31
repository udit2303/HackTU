"""
Router layer for the EWS (Early Warning System) module.

Thin routers that expose HTTP endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.modules.users.models import User

from app.modules.ews.schemas import (
    AnalyticsRequest,
    AnalyticsResponse,
    PredictionRequest,
    PredictionResponse,
    ScenarioRequest,
    ScenarioResponse,
    HeatmapRequest,
    HeatmapResponse,
    EvacuationRequest,
    EvacuationResponse,
    PredictionHistoryResponse,
)
from app.modules.ews.service import (
    AnalyticsService,
    PredictionService,
    ScenarioService,
    HeatmapService,
    EvacuationService,
)
from app.modules.ews import repository

router = APIRouter(prefix="/ews", tags=["EWS"])


@router.post(
    "/analytics",
    response_model=AnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute ground stability analytics",
    response_description="Stability index and metrics for the specified area and time range.",
)
def compute_analytics(
    request: AnalyticsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compute ground stability analytics for an area.
    
    - **area_id**: ID of the area to analyze
    - **time_range**: Time range for analysis (from_time, to_time in ISO-8601 format)
    - **Returns**: Stability index, confidence, and detailed metrics
    """
    # Verify area ownership
    if not repository.check_area_ownership(db, request.area_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this area",
        )
    
    # Verify area exists
    area = repository.get_area_by_id(db, request.area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )
    
    # Compute analytics
    return AnalyticsService.compute_analytics(
        db=db,
        area_id=request.area_id,
        time_range_from=request.time_range.from_time,
        time_range_to=request.time_range.to_time,
    )


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict hazard risk",
    response_description="Risk score, level, and expected event window for the specified hazard.",
)
def predict_hazard(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Predict hazard risk for an area.
    
    - **area_id**: ID of the area to predict for
    - **hazard**: Type of hazard (landslide or subsidence)
    - **horizon**: Prediction time horizon (6h, 24h, 72h, 7d)
    - **Returns**: Risk score, risk level, confidence, and expected event window
    """
    # Verify area ownership
    if not repository.check_area_ownership(db, request.area_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this area",
        )
    
    # Verify area exists
    area = repository.get_area_by_id(db, request.area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )
    
    # Predict hazard
    return PredictionService.predict_hazard(
        db=db,
        area_id=request.area_id,
        hazard=request.hazard,
        horizon=request.horizon,
    )


@router.get(
    "/areas/{area_id}/predictions/history",
    response_model=PredictionHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get prediction history",
    response_description="Historical predictions for the specified area.",
)
def get_prediction_history(
    area_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get prediction history for an area.
    
    - **area_id**: ID of the area
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **Returns**: List of historical predictions with metadata
    """
    # Verify area ownership
    if not repository.check_area_ownership(db, area_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this area",
        )
    
    # Verify area exists
    area = repository.get_area_by_id(db, area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )
    
    # Get history
    return PredictionService.get_prediction_history(
        db=db,
        area_id=area_id,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/scenario",
    response_model=ScenarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Simulate scenarios",
    response_description="Baseline risk and scenario simulation results.",
)
def simulate_scenarios(
    request: ScenarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulate multiple scenarios for an area.
    
    - **area_id**: ID of the area to simulate
    - **hazard**: Type of hazard to simulate
    - **scenarios**: List of scenarios with parameters (e.g., rainfall amount, groundwater rise)
    - **Returns**: Baseline risk and results for each scenario with risk deltas
    """
    # Verify area ownership
    if not repository.check_area_ownership(db, request.area_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this area",
        )
    
    # Verify area exists
    area = repository.get_area_by_id(db, request.area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )
    
    # Simulate scenarios
    return ScenarioService.simulate_scenarios(
        db=db,
        area_id=request.area_id,
        hazard=request.hazard,
        scenarios=request.scenarios,
    )


@router.post(
    "/heatmap",
    response_model=HeatmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate risk heatmap",
    response_description="GeoJSON FeatureCollection with risk data for visualization.",
)
def generate_heatmap(
    request: HeatmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a risk heatmap for an area.
    
    - **area_id**: ID of the area
    - **hazard**: Type of hazard to visualize
    - **layer**: Heatmap layer (landslide_risk, subsidence_risk, soil_moisture, displacement_rate)
    - **resolution**: Resolution level (low, medium, high)
    - **Returns**: GeoJSON FeatureCollection with polygon features and risk properties
    """
    # Verify area ownership
    if not repository.check_area_ownership(db, request.area_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this area",
        )
    
    # Verify area exists
    area = repository.get_area_by_id(db, request.area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )
    
    # Generate heatmap
    return HeatmapService.generate_heatmap(
        db=db,
        area_id=request.area_id,
        hazard=request.hazard,
        layer=request.layer,
        resolution=request.resolution,
    )


@router.post(
    "/evacuation",
    response_model=EvacuationResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute evacuation routes",
    response_description="Safe evacuation routes with risk scores and ETAs.",
)
def compute_evacuation_routes(
    request: EvacuationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compute safe evacuation routes from start points.
    
    - **area_id**: ID of the area
    - **start_points**: List of starting coordinates (lat/lon)
    - **Returns**: List of evacuation routes with risk scores, ETAs, and LineString geometries
    """
    # Verify area ownership
    if not repository.check_area_ownership(db, request.area_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this area",
        )
    
    # Verify area exists
    area = repository.get_area_by_id(db, request.area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )
    
    # Compute routes
    return EvacuationService.compute_evacuation_routes(
        db=db,
        area_id=request.area_id,
        start_points=request.start_points,
    )
