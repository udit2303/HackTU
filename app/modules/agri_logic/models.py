from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.base import Base

class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    # Using Geometry type with SRID 4326 (WGS84)
    # spatial_index=True creates a GIST index automatically
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=4326, spatial_index=True), nullable=False)
    area_size = Column(Float, nullable=True)  # In hectares or acres
    soil_type = Column(String, nullable=True)
    crop_type = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # user = relationship("User", back_populates="areas") # Assuming User model has back_populates="areas" or we add it later
    soil_measurements = relationship("SoilMeasurement", back_populates="area", cascade="all, delete-orphan")

class SoilMeasurement(Base):
    __tablename__ = "soil_measurements"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    nitrogen = Column(Float, nullable=False)   # N
    phosphorus = Column(Float, nullable=False) # P
    potassium = Column(Float, nullable=False)  # K
    ph = Column(Float, nullable=False)
    
    source = Column(String, nullable=True) # e.g., "manual", "iot_sensor"

    # Relationships
    area = relationship("Area", back_populates="soil_measurements")
