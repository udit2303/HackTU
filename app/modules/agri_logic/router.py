from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
# Assuming auth is set up as per guidelines, though I don't see exact auth import in my list_dir earlier.
# I will check 'app/core/security.py' or similar if it exists, or just use a placeholder dependency if not strictly enforced yet.
# The guideline said "Step 7: Authentication (JWT) ... Depends(get_current_user)".
# I'll try to import get_current_user from app.modules.auth.dependencies or app.core.security
# Let me check where get_current_user usually lives in this repo structure.
# Based on guidelines: "JWT logic lives in app/core/security.py".
# But I saw `app/modules/auth` folder. I'll guess `app.modules.auth.dependencies` or similar.
# For now, to be safe and strictly follow the file structure I saw, I'll assume `app.deps` or similar if `app/deps.py` existed (it does).
from app.deps import get_current_user 
from app.modules.users.models import User

from app.modules.agri_logic.schemas import (
    AreaCreate, AreaResponse, AreaUpdate, 
    SoilMeasurementCreate, SoilMeasurementResponse, 
    PredictionResponse, AnalyticsResponse
)
from app.modules.agri_logic.service import AreaService, PredictionService, AnalyticsService

router = APIRouter(prefix="/agri", tags=["Agri Logic"])

@router.post("/areas", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
def create_area(
    area: AreaCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return AreaService.create_area(db, area, current_user.id)

@router.get("/areas", response_model=List[AreaResponse])
def get_my_areas(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return AreaService.get_user_areas(db, current_user.id, skip, limit)

@router.get("/areas/{area_id}", response_model=AreaResponse)
def get_area(
    area_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this area")
    return area

@router.put("/areas/{area_id}", response_model=AreaResponse)
def update_area(
    area_id: int, 
    area_update: AreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Authorization check inside Service or here?
    # Better here to fail fast.
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this area")
    
    updated_area = AreaService.update_area(db, area_id, area_update)
    return updated_area

@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(
    area_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this area")
    
    AreaService.delete_area(db, area_id)
    return None

@router.post("/areas/{area_id}/measurements", response_model=SoilMeasurementResponse)
def add_measurement(
    area_id: int, 
    measurement: SoilMeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add measurements to this area")
        
    return AreaService.add_measurement(db, area_id, measurement)

@router.get("/areas/{area_id}/measurements", response_model=List[SoilMeasurementResponse])
def get_measurements(
    area_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view measurements for this area")
        
    return AreaService.get_measurements(db, area_id)

@router.post("/areas/{area_id}/predict", response_model=PredictionResponse)
def predict_nutrition(
    area_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    current_user: User = Depends(get_current_user)
):
    area = AreaService.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    if area.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return AnalyticsService.get_area_analytics(db, area_id)
