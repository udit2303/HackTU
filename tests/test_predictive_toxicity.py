import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, UTC

import sys
import os
sys.path.append(os.getcwd())

from app.modules.predictive_toxicity.service import PredictiveToxicityService
from app.modules.predictive_toxicity.schemas import (
    ToxicitySimulationCreate,
    SimulationStatus,
)
from app.modules.predictive_toxicity.models import (
    PredictiveToxicitySimulation,
    PredictiveToxicityMetrics,
)


class TestPredictiveToxicityService(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.service = PredictiveToxicityService(self.db)
        self.user_id = uuid4()

    @patch("app.modules.predictive_toxicity.service.repository")
    def test_create_simulation(self, mock_repo):
        payload = ToxicitySimulationCreate(
            site_id="SITE_001",
            calamity_type="flood",
            magnitude=7.5,
            unit="meters",
        )

        sim_id = uuid4()
        mock_sim = PredictiveToxicitySimulation(
            simulation_id=sim_id,
            user_id=self.user_id,
            site_id="SITE_001",
            calamity_type="flood",
            magnitude=7.5,
            unit="meters",
            status=SimulationStatus.QUEUED,
            engine_name=self.service.ENGINE_NAME,
            engine_version=self.service.ENGINE_VERSION,
            parameter_hash="abc",
            created_at=datetime.now(UTC),
        )

        mock_repo.create_simulation.return_value = mock_sim

        result = self.service.create_simulation(self.user_id, payload)

        mock_repo.create_simulation.assert_called_once()
        self.assertEqual(result.simulation_id, sim_id)
        self.assertEqual(result.status, SimulationStatus.QUEUED)
        self.assertEqual(result.engine, self.service.ENGINE_NAME)

    @patch("app.modules.predictive_toxicity.service.repository")
    def test_get_simulation_status(self, mock_repo):
        sim_id = uuid4()

        mock_sim = PredictiveToxicitySimulation(
            simulation_id=sim_id,
            user_id=self.user_id,
            site_id="SITE_001",
            calamity_type="flood",
            magnitude=7.5,
            unit="meters",
            status=SimulationStatus.RUNNING,
            engine_name="PredictiveToxicityEngine",
            engine_version="1.0.0",
            parameter_hash="abc",
            created_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
        )

        mock_repo.get_simulation_by_id.return_value = mock_sim

        status = self.service.get_simulation_status(sim_id, self.user_id)

        self.assertEqual(status.simulation_id, sim_id)
        self.assertEqual(status.status, SimulationStatus.RUNNING)
        self.assertEqual(status.progress, 0.5)

    @patch("app.modules.predictive_toxicity.service.repository")
    def test_get_risk_profile_completed(self, mock_repo):
        sim_id = uuid4()

        mock_sim = PredictiveToxicitySimulation(
            simulation_id=sim_id,
            user_id=self.user_id,
            site_id="SITE_001",
            calamity_type="flood",
            magnitude=7.5,
            unit="meters",
            status=SimulationStatus.COMPLETED,
            engine_name="PredictiveToxicityEngine",
            engine_version="1.0.0",
            parameter_hash="abc",
            created_at=datetime.now(UTC),
        )

        mock_metrics = PredictiveToxicityMetrics(
            simulation_id=sim_id,
            critical_radius_km=3.8,
            estimated_population=14500,
            affected_agri_land_acres=1200.0,
            primary_toxins=["Lead", "Chromium VI"],
            health_risks=["Neurological issues"],
            metrics_blob={
                "confidence_score": 0.92,
                "dataset_versions": {"CPCB": "2024-01"},
            },
        )

        mock_repo.get_simulation_by_id.return_value = mock_sim
        mock_repo.get_simulation_metrics.return_value = mock_metrics

        result, error_code = self.service.get_simulation_risk_profile(
            sim_id, self.user_id
        )

        self.assertIsNone(error_code)
        self.assertEqual(result.simulation_id, sim_id)
        self.assertEqual(result.critical_radius_km, 3.8)
        self.assertIn("Lead", result.affected_metrics.primary_toxins)

    @patch("app.modules.predictive_toxicity.service.repository")
    def test_get_risk_profile_not_completed(self, mock_repo):
        sim_id = uuid4()

        mock_sim = PredictiveToxicitySimulation(
            simulation_id=sim_id,
            user_id=self.user_id,
            site_id="SITE_001",
            calamity_type="flood",
            magnitude=7.5,
            unit="meters",
            status=SimulationStatus.RUNNING,
            engine_name="PredictiveToxicityEngine",
            engine_version="1.0.0",
            parameter_hash="abc",
            created_at=datetime.now(UTC),
        )

        mock_repo.get_simulation_by_id.return_value = mock_sim

        result, error_code = self.service.get_simulation_risk_profile(
            sim_id, self.user_id
        )

        self.assertIsNone(result)
        self.assertEqual(error_code, 202)


if __name__ == "__main__":
    unittest.main()
