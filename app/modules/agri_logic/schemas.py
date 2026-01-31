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
    """
    Input schema for creating an area. The geometry field expects a valid GeoJSON object as per RFC 7946.
    Example:
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[30, 10], [40, 40], [20, 40], [10, 20], [30, 10]]]
        },
        "properties": {}
    }
    """
    geometry: dict = Field(..., example={
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[30, 10], [40, 40], [20, 40], [10, 20], [30, 10]]]
        },
        "properties": {}
    })

class AreaUpdate(BaseModel):
    name: Optional[str] = None
    area_size: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    geometry: Optional[dict] = Field(None, example={
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[30, 10], [40, 40], [20, 40], [10, 20], [30, 10]]]
        },
        "properties": {}
    })

class AreaResponse(AreaBase):
    id: int
    user_id: int
    geometry: dict = Field(..., example={
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[30, 10], [40, 40], [20, 40], [10, 20], [30, 10]]]
        },
        "properties": {}
    })
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
