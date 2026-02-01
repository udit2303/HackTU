from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user
from app.modules.users.models import User

from app.modules.agri_logic.schemas import (
    AreaCreate,
    AreaResponse,
    AreaUpdate,
    SoilMeasurementCreate,
    SoilMeasurementResponse,
    PredictionResponse,
    AnalyticsResponse,
)
from app.modules.agri_logic.service import (
    AreaService,
    PredictionService,
    AnalyticsService,
)

router = APIRouter(prefix="/agri", tags=["Agri Logic"])


@router.post(
    "/areas",
    response_model=AreaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new area",
    response_description="The created area as a GeoJSON Feature object.",
    tags=["Agri Logic"],
)
def create_area(
    area: AreaCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new area.

    - **area**: GeoJSON Feature object representing the area geometry and properties. Example:
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[30, 10], [40, 40], [20, 40], [10, 20], [30, 10]]]
            },
            "properties": {}
        }
    - **Returns**: The created area as a GeoJSON Feature object.
    """
    return AreaService.create_area(db, area, current_user.id)


@router.get(
    "/areas",
    response_model=List[AreaResponse],
    summary="List all areas for the current user",
    response_description="A list of areas as GeoJSON Feature objects.",
    tags=["Agri Logic"],
)
def get_my_areas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all areas belonging to the current user.

    - **Returns**: List of areas, each as a GeoJSON Feature object.
    """
    return AreaService.get_user_areas(db, current_user.id, skip, limit)


@router.get(
    "/areas/{area_id}",
    response_model=AreaResponse,
    summary="Get a specific area",
    response_description="The area as a GeoJSON Feature object.",
    tags=["Agri Logic"],
)
def get_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific area by its ID.

    - **area_id**: ID of the area to retrieve.
    - **Returns**: The area as a GeoJSON Feature object.
    """
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this area"
        )
    return area


@router.put(
    "/areas/{area_id}",
    response_model=AreaResponse,
    summary="Update an area",
    response_description="The updated area as a GeoJSON Feature object.",
    tags=["Agri Logic"],
)
def update_area(
    area_id: int,
    area_update: AreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing area.

    - **area_id**: ID of the area to update.
    - **area_update**: Updated data for the area (GeoJSON Feature object for geometry).
    - **Returns**: The updated area as a GeoJSON Feature object.
    """
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this area"
        )
    updated_area = AreaService.update_area(db, area_id, area_update)
    return updated_area


@router.delete(
    "/areas/{area_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an area",
    response_description="Area deleted successfully.",
    tags=["Agri Logic"],
)
def delete_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an area by its ID.

    - **area_id**: ID of the area to delete.
    - **Returns**: 204 No Content if successful.
    """
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this area"
        )
    AreaService.delete_area(db, area_id)
    return None


@router.get(
    "/areas/{area_id}/measurements", response_model=List[SoilMeasurementResponse]
)
def get_measurements(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view measurements for this area"
        )

    return AreaService.get_measurements(db, area_id)


@router.post(
    "/areas/{area_id}/predict",
    response_model=PredictionResponse,
    summary="Predict soil nutrition for an area",
    response_description="Predicted soil nutrition and health score for the specified area.",
    tags=["Agri Logic"],
)
def predict_nutrition(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Predict soil nutrition and health score for a given area.

    - **area_id**: ID of the area to predict for (must belong to the current user).
    - **Returns**: Predicted nitrogen, phosphorus, potassium, pH, health score, and deficiency indicators for the area.
    """
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    prediction = PredictionService.predict_nutrition(db, area_id)
    if not prediction:
        raise HTTPException(status_code=400, detail="Could not generate prediction")
    return prediction


@router.get("/areas/{area_id}/analytics", response_model=AnalyticsResponse)
def get_area_analytics(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return AnalyticsService.get_area_analytics(db, area_id)
