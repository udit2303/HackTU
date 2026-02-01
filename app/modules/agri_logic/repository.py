from sqlalchemy.orm import Session
from sqlalchemy import func
from app.modules.agri_logic.models import Area, SoilMeasurement
from app.modules.agri_logic.schemas import AreaCreate, AreaUpdate, SoilMeasurementCreate
from geoalchemy2.elements import WKTElement

def get_area_by_id(db: Session, area_id: int):
    return db.query(Area).filter(Area.id == area_id).first()

def get_user_areas(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Area).filter(Area.user_id == user_id).offset(skip).limit(limit).all()

def create_area(db: Session, area: AreaCreate, user_id: int):
    # Convert WKT string to WKTElement with SRID 4326
    # We assume validation happens before or we catch DB errors
    geom = WKTElement(area.geometry, srid=4326)
    
    db_area = Area(
        user_id=user_id,
        name=area.name,
        geometry=geom,
        area_size=area.area_size,
        soil_type=area.soil_type,
        crop_type=area.crop_type
    )
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

def update_area(db: Session, area_id: int, area_update: AreaUpdate):
    db_area = get_area_by_id(db, area_id)
    if not db_area:
        return None
    
    update_data = area_update.dict(exclude_unset=True)
    if 'geometry' in update_data:
        update_data['geometry'] = WKTElement(update_data['geometry'], srid=4326)
        
    for key, value in update_data.items():
        setattr(db_area, key, value)
    
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

def delete_area(db: Session, area_id: int):
    db_area = get_area_by_id(db, area_id)
    if db_area:
        db.delete(db_area)
        db.commit()
    return db_area

# Soil Measurement Logic

def create_measurement(db: Session, measurement: SoilMeasurementCreate, area_id: int):
    db_measurement = SoilMeasurement(
        area_id=area_id,
        nitrogen=measurement.nitrogen,
        phosphorus=measurement.phosphorus,
        potassium=measurement.potassium,
        ph=measurement.ph,
        source=measurement.source
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def get_measurements_by_area(db: Session, area_id: int, skip: int = 0, limit: int = 100):
    return db.query(SoilMeasurement).filter(SoilMeasurement.area_id == area_id)\
        .order_by(SoilMeasurement.timestamp.desc())\
        .offset(skip).limit(limit).all()

def get_area_analytics(db: Session, area_id: int):
    # Calculate averages
    stats = db.query(
        func.avg(SoilMeasurement.nitrogen).label('avg_n'),
        func.avg(SoilMeasurement.phosphorus).label('avg_p'),
        func.avg(SoilMeasurement.potassium).label('avg_k'),
        func.avg(SoilMeasurement.ph).label('avg_ph'),
        func.count(SoilMeasurement.id).label('count'),
        func.min(SoilMeasurement.ph).label('min_ph'),
        func.max(SoilMeasurement.ph).label('max_ph')
    ).filter(SoilMeasurement.area_id == area_id).first()
    
    return stats
