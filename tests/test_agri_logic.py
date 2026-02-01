import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Adjust path to import app modules if needed, or assume running from root
import sys
import os

sys.path.append(os.getcwd())

from app.modules.agri_logic.service import (
    AreaService,
    PredictionService,
    AnalyticsService,
)
from app.modules.agri_logic.schemas import AreaCreate, AreaUpdate, SoilMeasurementCreate
from app.modules.agri_logic.models import Area, SoilMeasurement


class TestAgriLogic(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()

    @patch("app.modules.agri_logic.service.repository")
    def test_create_area(self, mock_repo):
        # Arrange
        area_create = AreaCreate(
            name="Test Field",
            geometry="POINT(30 10)",
            area_size=10.5,
            soil_type="Loam",
            crop_type="Wheat",
        )
        user_id = 1
        expected_area = Area(id=1, name="Test Field", user_id=1)
        mock_repo.create_area.return_value = expected_area

        # Act
        result = AreaService.create_area(self.db, area_create, user_id)

        # Assert
        mock_repo.create_area.assert_called_once_with(self.db, area_create, user_id)
        self.assertEqual(result, expected_area)

    @patch("app.modules.agri_logic.service.repository")
    def test_predict_nutrition(self, mock_repo):
        # Arrange
        area_id = 1
        mock_area = Area(id=area_id, name="Test Field")
        mock_repo.get_area_by_id.return_value = mock_area

        # Act
        prediction = PredictionService.predict_nutrition(self.db, area_id)

        # Assert
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.area_id, area_id)
        self.assertTrue(0 <= prediction.predicted_ph <= 14)
        self.assertTrue(len(prediction.deficiency_indicators) >= 0)

    @patch("app.modules.agri_logic.service.repository")
    def test_get_area_analytics(self, mock_repo):
        # Arrange
        area_id = 1
        mock_area = Area(id=area_id)
        mock_repo.get_area_by_id.return_value = mock_area

        mock_stats = MagicMock()
        mock_stats.avg_n = 50.0
        mock_stats.avg_p = 30.0
        mock_stats.avg_k = 200.0
        mock_stats.avg_ph = 6.5
        mock_stats.count = 10
        mock_stats.min_ph = 6.0
        mock_stats.max_ph = 7.0

        mock_repo.get_area_analytics.return_value = mock_stats

        # Act
        result = AnalyticsService.get_area_analytics(self.db, area_id)

        # Assert
        self.assertEqual(result.avg_nitrogen, 50.0)
        self.assertEqual(result.measurement_count, 10)


if __name__ == "__main__":
    unittest.main()
