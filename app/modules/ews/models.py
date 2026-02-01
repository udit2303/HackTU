"""
Database models for the EWS (Early Warning System) module.

These models store historical data for predictions and analytics.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class PredictionHistory(Base):
    """
    Stores historical predictions for hazards.

    Tracks all predictions made by the system for auditing and accuracy analysis.
    """

    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False, index=True)

    # Prediction parameters
    hazard = Column(String, nullable=False)  # HazardType enum value
    horizon = Column(String, nullable=False)  # TimeHorizon enum value

    # Prediction results
    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_level = Column(String, nullable=False)  # RiskLevel enum value
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0

    # Expected event window (nullable if no specific window predicted)
    expected_window_from = Column(DateTime(timezone=True), nullable=True)
    expected_window_to = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship to Area (from agri_logic module)
    # Note: We don't import Area model directly to avoid circular dependency
    # The relationship is defined via foreign key only


class AnalyticsHistory(Base):
    """
    Stores historical analytics snapshots for areas.

    Tracks stability metrics and ground conditions over time.
    """

    __tablename__ = "analytics_history"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False, index=True)

    # Analytics results
    stability_index = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0

    # Metrics
    soil_moisture_avg = Column(Float, nullable=True)
    displacement_trend_mm_per_month = Column(Float, nullable=True)
    rainfall_accumulation_mm = Column(Float, nullable=True)

    # Time range analyzed
    time_range_from = Column(DateTime(timezone=True), nullable=False)
    time_range_to = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
