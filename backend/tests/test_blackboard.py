import asyncio
import unittest
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.orchestration.blackboard import Blackboard
from app.database import init_db

class TestBlackboard(unittest.TestCase):
    def setUp(self):
        init_db()
        self.bb = Blackboard.get_instance()

    def test_post_and_retrieve(self):
        async def run_test():
            req_id = "test-req-101"
            sample_data = {"temperature": 25.0, "condition": "Sunny"}
            
            entry = await self.bb.post(
                request_id=req_id,
                agent_name="weather_agent",
                category="weather",
                output_data=sample_data,
                status="COMPLETED"
            )
            
            self.assertEqual(entry["request_id"], req_id)
            self.assertEqual(entry["agent_name"], "weather_agent")
            
            # Read back
            entries = self.bb.get_entries(req_id)
            self.assertTrue(len(entries) >= 1)
            
            weather_out = self.bb.get_agent_output(req_id, "weather_agent")
            self.assertIsNotNone(weather_out)
            self.assertEqual(weather_out["temperature"], 25.0)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
