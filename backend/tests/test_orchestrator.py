import asyncio
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import init_db, get_advisory_db
from app.models.advisory import FarmerInput
from app.orchestration.orchestrator import ControlRoomOrchestrator

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        init_db()
        self.orchestrator = ControlRoomOrchestrator.get_instance()

    def test_full_pipeline(self):
        async def run_test():
            farmer_in = FarmerInput(
                farmer_name="Demo Sardar",
                crop_name="Wheat",
                location="Ludhiana, Punjab",
                crop_stage="Flowering",
                land_area=6.0,
                irrigation_type="Canal / Tubewell"
            )
            req_id = await self.orchestrator.run_workflow(farmer_in)
            self.assertIsNotNone(req_id)
            
            # Wait for workflow completion (simulated async pipeline)
            for _ in range(25):
                await asyncio.sleep(0.5)
                adv = get_advisory_db(req_id)
                if adv and adv["status"] == "COMPLETED":
                    break

            adv_final = get_advisory_db(req_id)
            self.assertIsNotNone(adv_final)
            self.assertEqual(adv_final["status"], "COMPLETED")
            self.assertIsNotNone(adv_final["final_advisory"])
            
            # Verify 5 mandatory sections
            final_obj = adv_final["final_advisory"]
            self.assertIn("weather_overview", final_obj)
            self.assertIn("risk_alert", final_obj)
            self.assertIn("field_actions", final_obj)
            self.assertIn("mandi_analysis", final_obj)
            self.assertIn("recommended_scheme", final_obj)
            self.assertIn("next_steps", final_obj)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
