import random
from sqlalchemy.orm import Session
from app.modules.agri_logic import repository
from app.modules.agri_logic.schemas import AreaCreate, AreaUpdate, SoilMeasurementCreate, PredictionResponse, AnalyticsResponse

class AreaService:
    @staticmethod
    def create_area(db: Session, area: AreaCreate, user_id: int):
        return repository.create_area(db, area, user_id)

    @staticmethod
    def get_area(db: Session, area_id: int):
        return repository.get_area_by_id(db, area_id)

    @staticmethod
    def get_user_areas(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        # We might need to transform the geometry for the response if the model doesn't auto-convert
        # But usually Pydantic with from_attributes=True handles the basics, 
        # except GeoAlchemy2 elements might need stringification.
        return repository.get_user_areas(db, user_id, skip, limit)

    @staticmethod
    def update_area(db: Session, area_id: int, area_update: AreaUpdate):
        return repository.update_area(db, area_id, area_update)

    @staticmethod
    def delete_area(db: Session, area_id: int):
        return repository.delete_area(db, area_id)

    @staticmethod
    def add_measurement(db: Session, area_id: int, measurement: SoilMeasurementCreate):
        # Check if area exists first? 
        # For now, let DB FK handle it or check explicitly.
        # Checking explicitly is better for correct error message (404 vs 500 integrity error)
        area = repository.get_area_by_id(db, area_id)
        if not area:
            return None
        return repository.create_measurement(db, measurement, area_id)

    @staticmethod
    def get_measurements(db: Session, area_id: int):
        return repository.get_measurements_by_area(db, area_id)

class PredictionService:
    @staticmethod
    def predict_nutrition(db: Session, area_id: int) -> PredictionResponse:
        # Placeholder logic as requested
        # In a real app, this would fetch historical data, 
        # maybe call an external ML model or compute based on crop type
        
        area = repository.get_area_by_id(db, area_id)
        if not area:
            return None
            
        # Mock values
        pred_n = random.uniform(20, 100)
        pred_p = random.uniform(10, 80)
        pred_k = random.uniform(100, 300)
        pred_ph = random.uniform(5.5, 7.5)
        
        health_score = random.uniform(50, 95)
        
        deficiency = []
        if pred_n < 40: deficiency.append("Low Nitrogen")
        if pred_ph < 6.0: deficiency.append("Acidic Soil")
        
        return PredictionResponse(
            area_id=area_id,
            predicted_nitrogen=round(pred_n, 2),
            predicted_phosphorus=round(pred_p, 2),
            predicted_potassium=round(pred_k, 2),
            predicted_ph=round(pred_ph, 2),
            health_score=round(health_score, 1),
            deficiency_indicators=deficiency
        )

class AnalyticsService:
    @staticmethod
    def get_area_analytics(db: Session, area_id: int) -> AnalyticsResponse:
        stats = repository.get_area_analytics(db, area_id)
        
        if not stats or stats.count == 0:
            return AnalyticsResponse(
                area_id=area_id,
                avg_nitrogen=0,
                avg_phosphorus=0,
                avg_potassium=0,
                avg_ph=0,
                measurement_count=0,
                min_ph=0,
                max_ph=0
            )
            
        return AnalyticsResponse(
            area_id=area_id,
            avg_nitrogen=stats.avg_n or 0,
            avg_phosphorus=stats.avg_p or 0,
            avg_potassium=stats.avg_k or 0,
            avg_ph=stats.avg_ph or 0,
            measurement_count=stats.count,
            min_ph=stats.min_ph or 0,
            max_ph=stats.max_ph or 0
        )
