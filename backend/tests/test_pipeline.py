import unittest
import requests
import subprocess
import time
import sys

class TestPipelineAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Starting local test server process...")
        cls.server_process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd="/Users/priyadharshini/Desktop/infosys/solar-wind-deployment-intelligence/backend"
        )
        
        # Wait up to 15 seconds for server to be responsive
        success = False
        for i in range(15):
            try:
                res = requests.get("http://127.0.0.1:8000/health", timeout=1.0)
                if res.status_code == 200:
                    success = True
                    break
            except Exception:
                pass
            time.sleep(1.0)
            
        if not success:
            cls.server_process.terminate()
            raise RuntimeError("Uvicorn test server failed to start within 15 seconds.")

    @classmethod
    def tearDownClass(cls):
        print("Shutting down local test server process...")
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_health(self):
        res = requests.get("http://127.0.0.1:8000/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "Running")

    def test_successful_analysis(self):
        payload = {
            "latitude": 12.97,
            "longitude": 77.59,
            "area_sq_m": 80000.0,
            "electricity_tariff_inr_kwh": 5.5,
            "slope_deg": 2.0,
            "elevation_m": 920.0,
            "dist_grid_m": 1500.0,
            "dist_road_m": 300.0
        }
        res = requests.post("http://127.0.0.1:8000/api/analysis", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertTrue(data["technical_assessment"]["technical_feasibility"])
        self.assertIn("recommended_deployment", data["technical_assessment"])
        self.assertGreater(data["energy"]["annual_energy_yield_kwh"], 0)
        self.assertGreater(data["financials"]["annual_revenue_inr"], 0)
        
    def test_hard_constraint_failure(self):
        payload = {
            "latitude": 12.97,
            "longitude": 77.59,
            "area_sq_m": 80000.0,
            "electricity_tariff_inr_kwh": 5.5,
            "slope_deg": 25.0,  # exceeds 20 degree limit
            "elevation_m": 920.0,
            "dist_grid_m": 1500.0,
            "dist_road_m": 300.0
        }
        res = requests.post("http://127.0.0.1:8000/api/analysis", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertFalse(data["technical_assessment"]["technical_feasibility"])
        self.assertEqual(data["technical_assessment"]["recommended_deployment"], "None")
        self.assertEqual(data["financials"]["annual_revenue_inr"], 0)

if __name__ == "__main__":
    unittest.main()
