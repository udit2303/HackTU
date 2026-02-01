"""
Central model registry.

All SQLAlchemy models must be imported here so Alembic can discover them.
"""

# Core models
from app.modules.users.models import User

# Add new modules here
# from app.modules.locations.models import Location
from app.modules.agri_logic.models import Area, SoilMeasurement
from app.modules.ews.models import PredictionHistory, AnalyticsHistory
