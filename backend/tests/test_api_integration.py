import asyncio
import os
import sys
import unittest
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import init_db

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_health_check(self):
        async def run():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/health")
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data["status"], "healthy")
                self.assertEqual(data["group"], "Group 20 – Multi-Agent AI System")
        asyncio.run(run())

    def test_schemes_endpoint(self):
        async def run():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/schemes")
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertTrue(data["total"] >= 5)

                search_res = await client.get("/api/schemes/search?q=insurance")
                self.assertEqual(search_res.status_code, 200)
                self.assertTrue(len(search_res.json()["results"]) > 0)
        asyncio.run(run())

    def test_history_and_stats(self):
        async def run():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/history")
                self.assertEqual(res.status_code, 200)

                stats = await client.get("/api/history/stats")
                self.assertEqual(stats.status_code, 200)
                s_data = stats.json()
                self.assertEqual(s_data["active_agents"], 7)
        asyncio.run(run())

    def test_full_advisory_lifecycle(self):
        async def run():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Post farmer input
                farmer_payload = {
                    "farmer_name": "Sardar Gurpreet Singh",
                    "crop_name": "Wheat",
                    "location": "Ludhiana, Punjab",
                    "crop_stage": "Flowering",
                    "land_area": 8.0,
                    "irrigation_type": "Tubewell"
                }
                gen_res = await client.post("/api/advisory/generate", json=farmer_payload)
                self.assertEqual(gen_res.status_code, 200)
                req_id = gen_res.json()["request_id"]
                self.assertTrue(req_id)

                # 2. Wait and poll for completion
                completed = False
                for _ in range(30):
                    await asyncio.sleep(0.4)
                    status_res = await client.get(f"/api/agents/status/{req_id}")
                    self.assertEqual(status_res.status_code, 200)
                    st_data = status_res.json()
                    if st_data.get("workflow_status") == "COMPLETED":
                        completed = True
                        break

                self.assertTrue(completed, "Workflow did not complete within timeout")

                # 3. Fetch Blackboard entries
                bb_res = await client.get(f"/api/blackboard/{req_id}")
                self.assertEqual(bb_res.status_code, 200)
                bb_data = bb_res.json()
                self.assertTrue(bb_data["total_entries"] >= 6)

                # 4. Fetch final advisory
                adv_res = await client.get(f"/api/advisory/{req_id}")
                self.assertEqual(adv_res.status_code, 200)
                adv_data = adv_res.json()
                final_adv = adv_data["final_advisory"]
                self.assertIsNotNone(final_adv)
                self.assertIn("weather_overview", final_adv)
                self.assertIn("risk_alert", final_adv)
                self.assertIn("field_actions", final_adv)
                self.assertIn("mandi_analysis", final_adv)
                self.assertIn("recommended_scheme", final_adv)

                # 5. Fetch PDF download
                pdf_res = await client.get(f"/api/advisory/{req_id}/pdf")
                self.assertEqual(pdf_res.status_code, 200)
                self.assertEqual(pdf_res.headers["content-type"], "application/pdf")
                self.assertTrue(len(pdf_res.content) > 1000)

        asyncio.run(run())

if __name__ == "__main__":
    unittest.main()
