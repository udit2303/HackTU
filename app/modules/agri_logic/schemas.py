from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator
# We might need a way to handle Geometry input. 
# For simplicity, we'll accept WKT (Well-Known Text) strings or GeoJSON dictionaries.
# app/modules/agri_logic/schemas.py

class SoilMeasurementBase(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    source: Optional[str] = "manual"

class SoilMeasurementCreate(SoilMeasurementBase):
    pass

class SoilMeasurementResponse(SoilMeasurementBase):
    id: int
    area_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AreaBase(BaseModel):
    name: str
    area_size: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None

class AreaCreate(AreaBase):
    # Geometry input as WKT string (e.g., "POINT(30 10)")
    # In a real app, we might use pydantic-geojson or specific validators
    geometry: str 

class AreaUpdate(BaseModel):
    name: Optional[str] = None
    area_size: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    geometry: Optional[str] = None

class AreaResponse(AreaBase):
    id: int
    user_id: int
    # We will return WKT or handle serialization in the router/service
    # For now, let's assume we return it as a string (WKT) or we map it before response
    geometry: Any 
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    area_id: int
    predicted_nitrogen: float
    predicted_phosphorus: float
    predicted_potassium: float
    predicted_ph: float
    health_score: float
    deficiency_indicators: List[str]

class AnalyticsResponse(BaseModel):
    area_id: int
    avg_nitrogen: float
    avg_phosphorus: float
    avg_potassium: float
    avg_ph: float
    measurement_count: int
    min_ph: float
    max_ph: float
