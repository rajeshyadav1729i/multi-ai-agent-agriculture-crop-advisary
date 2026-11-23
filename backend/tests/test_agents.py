import asyncio
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import init_db
from app.orchestration.blackboard import Blackboard
from app.models.advisory import FarmerInput
from app.agents.intake_agent import IntakeAgent
from app.agents.crop_agent import CropAgent
from app.agents.market_agent import MarketAgent
from app.agents.scheme_agent import SchemeAgent
from app.agents.risk_alert_agent import RiskAlertAgent

class TestAgents(unittest.TestCase):
    def setUp(self):
        init_db()
        self.bb = Blackboard.get_instance()

    def test_intake_and_crop_agents(self):
        async def run_test():
            req_id = "test-agent-flow-1"
            farmer_in = FarmerInput(
                farmer_name="Test Farmer",
                crop_name="Wheat",
                location="Ludhiana, Punjab",
                crop_stage="Flowering",
                land_area=5.0,
                irrigation_type="Tubewell"
            )
            
            # 1. Intake Agent
            intake = IntakeAgent()
            intake.set_input(farmer_in)
            out_intake = await intake.execute(req_id, self.bb)
            self.assertEqual(out_intake["crop_name"], "Wheat")
            self.assertEqual(out_intake["validation_status"], "VALIDATED")

            # Seed fake weather on blackboard
            await self.bb.post(req_id, "weather_agent", "weather", {
                "temperature": 24.0,
                "humidity": 60,
                "wind_speed_kmh": 12.0,
                "max_rain_prob_next_5_days": 10,
                "total_expected_rain_mm": 0.0,
                "has_threats": False
            })

            # 2. Crop Agent
            crop_agent = CropAgent()
            out_crop = await crop_agent.execute(req_id, self.bb)
            self.assertIn("irrigation_action", out_crop)
            self.assertIn("fertilizer_action", out_crop)

            # 3. Market Agent
            mkt_agent = MarketAgent()
            out_mkt = await mkt_agent.execute(req_id, self.bb)
            self.assertIn(out_mkt["recommendation"], ["SELL", "HOLD", "MONITOR", "HOLD / SELL TO FCI/GOVT"])

            # 4. Scheme Agent (RAG)
            scheme_agent = SchemeAgent()
            out_scheme = await scheme_agent.execute(req_id, self.bb)
            self.assertIsNotNone(out_scheme.get("selected_scheme"))
            self.assertTrue(len(out_scheme.get("eligibility_conditions")) > 0)

            # 5. Risk Alert Agent
            risk_agent = RiskAlertAgent()
            out_risk = await risk_agent.execute(req_id, self.bb)
            self.assertIn(out_risk["risk_level"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
