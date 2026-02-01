"""
Repository layer for the EWS (Early Warning System) module.

All database access using ORM only (no raw SQL).
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.modules.agri_logic.models import Area
from app.modules.ews.models import PredictionHistory, AnalyticsHistory

# ============================================================================
# Area Access
# ============================================================================


def get_area_by_id(db: Session, area_id: int) -> Optional[Area]:
    """
    Get an area by its ID.

    Args:
        db: Database session
        area_id: ID of the area

    Returns:
        Area model instance or None if not found
    """
    return db.query(Area).filter(Area.id == area_id).first()


def check_area_ownership(db: Session, area_id: int, user_id: int) -> bool:
    """
    Check if a user owns a specific area.

    Args:
        db: Database session
        area_id: ID of the area
        user_id: ID of the user

    Returns:
        True if user owns the area, False otherwise
    """
    area = db.query(Area).filter(Area.id == area_id, Area.user_id == user_id).first()
    return area is not None


# ============================================================================
# Prediction History
# ============================================================================


def save_prediction(
    db: Session,
    area_id: int,
    hazard: str,
    horizon: str,
    risk_score: float,
    risk_level: str,
    confidence: float,
    expected_window_from: Optional[datetime] = None,
    expected_window_to: Optional[datetime] = None,
) -> PredictionHistory:
    """
    Save a prediction to history.

    Args:
        db: Database session
        area_id: ID of the area
        hazard: Hazard type (enum value)
        horizon: Time horizon (enum value)
        risk_score: Risk score (0.0 to 1.0)
        risk_level: Risk level (enum value)
        confidence: Confidence score (0.0 to 1.0)
        expected_window_from: Start of expected event window (optional)
        expected_window_to: End of expected event window (optional)

    Returns:
        Created PredictionHistory instance
    """
    prediction = PredictionHistory(
        area_id=area_id,
        hazard=hazard,
        horizon=horizon,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        expected_window_from=expected_window_from,
        expected_window_to=expected_window_to,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def get_prediction_history(
    db: Session,
    area_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[PredictionHistory]:
    """
    Get prediction history for an area.

    Args:
        db: Database session
        area_id: ID of the area
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of PredictionHistory instances
    """
    return (
        db.query(PredictionHistory)
        .filter(PredictionHistory.area_id == area_id)
        .order_by(PredictionHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_prediction_history_count(db: Session, area_id: int) -> int:
    """
    Get total count of predictions for an area.

    Args:
        db: Database session
        area_id: ID of the area

    Returns:
        Total number of predictions
    """
    return (
        db.query(PredictionHistory).filter(PredictionHistory.area_id == area_id).count()
    )


def get_prediction_history_by_hazard(
    db: Session,
    area_id: int,
    hazard: str,
    skip: int = 0,
    limit: int = 100,
) -> List[PredictionHistory]:
    """
    Get prediction history for an area filtered by hazard type.

    Args:
        db: Database session
        area_id: ID of the area
        hazard: Hazard type to filter by
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of PredictionHistory instances
    """
    return (
        db.query(PredictionHistory)
        .filter(
            PredictionHistory.area_id == area_id, PredictionHistory.hazard == hazard
        )
        .order_by(PredictionHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============================================================================
# Analytics History
# ============================================================================


def save_analytics(
    db: Session,
    area_id: int,
    stability_index: float,
    confidence: float,
    soil_moisture_avg: float,
    displacement_trend_mm_per_month: float,
    rainfall_accumulation_mm: float,
    time_range_from: datetime,
    time_range_to: datetime,
) -> AnalyticsHistory:
    """
    Save analytics results to history.

    Args:
        db: Database session
        area_id: ID of the area
        stability_index: Stability index (0.0 to 1.0)
        confidence: Confidence score (0.0 to 1.0)
        soil_moisture_avg: Average soil moisture
        displacement_trend_mm_per_month: Displacement trend
        rainfall_accumulation_mm: Rainfall accumulation
        time_range_from: Start of analyzed time range
        time_range_to: End of analyzed time range

    Returns:
        Created AnalyticsHistory instance
    """
    analytics = AnalyticsHistory(
        area_id=area_id,
        stability_index=stability_index,
        confidence=confidence,
        soil_moisture_avg=soil_moisture_avg,
        displacement_trend_mm_per_month=displacement_trend_mm_per_month,
        rainfall_accumulation_mm=rainfall_accumulation_mm,
        time_range_from=time_range_from,
        time_range_to=time_range_to,
    )
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics


def get_analytics_history(
    db: Session,
    area_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[AnalyticsHistory]:
    """
    Get analytics history for an area.

    Args:
        db: Database session
        area_id: ID of the area
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of AnalyticsHistory instances
    """
    return (
        db.query(AnalyticsHistory)
        .filter(AnalyticsHistory.area_id == area_id)
        .order_by(AnalyticsHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
