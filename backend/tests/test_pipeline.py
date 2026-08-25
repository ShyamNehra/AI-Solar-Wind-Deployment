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
"""
Unit & Integration Tests for Deployment Optimization Pipeline.
Tests Module 1, 2, 3, 4, 5, and 6.
"""

import pytest
from app.services.deployment_optimization_service import DeploymentOptimizationService
from app.services.forecasting_service import ForecastingService
from app.services.investment_recommendation_service import InvestmentRecommendationService
from app.services.workflow_pipeline_service import WorkflowPipelineService


def test_deployment_optimization_service_basic():
    service = DeploymentOptimizationService()
    res = service.optimize_deployment(
        overall_suitability_score=82.5,
        solar_resource=6.2,
        wind_resource=7.1,
        installed_capacity=1000.0,
        deployment_type="Hybrid"
    )

    assert "optimal_installed_capacity" in res
    assert "recommended_deployment_type" in res
    assert "renewable_mix" in res
    assert "overall_optimization_score" in res
    assert "constraint_satisfaction_score" in res
    assert res["feasible"] is True
    assert res["optimization_status"] == "Optimal"
    assert res["optimal_installed_capacity"] == 1000.0
    assert res["best_capacity"] == 1000.0
    assert res["renewable_mix"]["solar_pct"] + res["renewable_mix"]["wind_pct"] == 100.0


def test_deployment_optimization_constraints_grid_and_budget():
    service = DeploymentOptimizationService()
    # Apply strict grid capacity (e.g., max 0.5 MW = 500 kW) and budget constraint
    res = service.optimize_deployment(
        overall_suitability_score=75.0,
        solar_resource=5.5,
        wind_resource=6.0,
        installed_capacity=2000.0,  # 2000 kW target
        deployment_type="Hybrid",
        constraints={
            "grid_capacity": 0.5,  # 0.5 MW -> 500 kW max
            "budget_limit": 800000.0  # $800,000 max budget
        }
    )

    assert res["optimal_installed_capacity"] <= 500.0
    assert len(res["constraint_violations"]) > 0
    assert res["optimization_status"] in ["Feasible", "Sub-optimal"]


def test_forecasting_service():
    service = ForecastingService()
    forecast = service.generate_forecast(
        installed_capacity=1000.0,
        solar_capacity=600.0,
        wind_capacity=400.0,
        deployment_type="Hybrid",
        solar_capacity_factor=20.0,
        wind_capacity_factor=35.0,
        tariff_rate=0.08
    )

    assert forecast["annual_energy_forecast"] > 0
    assert len(forecast["monthly_energy_forecast"]) == 12
    assert "spring_kwh" in forecast["seasonal_forecast"]
    assert "summer_kwh" in forecast["seasonal_forecast"]
    assert "monsoon_kwh" in forecast["seasonal_forecast"]
    assert "winter_kwh" in forecast["seasonal_forecast"]
    assert forecast["revenue_forecast"]["annual_revenue"] > 0


def test_investment_recommendation_service():
    service = InvestmentRecommendationService()
    inv = service.calculate_investment_metrics(
        annual_energy_kwh=2500000.0,
        installed_capacity=1000.0,
        deployment_type="Hybrid",
        tariff_rate=0.08,
        project_lifetime_years=25,
        discount_rate=0.08
    )

    assert inv["capex"] > 0
    assert inv["opex"] > 0
    assert inv["annual_revenue"] > 0
    assert inv["payback_period"] > 0
    assert inv["roi"] > 0
    assert "investment_risk" in inv
    assert inv["investment_recommendation"] in ["Recommended", "Conditionally Recommended", "Not Recommended"]


def test_workflow_pipeline_service_integration():
    pipeline = WorkflowPipelineService()
    res = pipeline.run_pipeline(
        latitude=13.6288,
        longitude=79.4192,
        target_capacity=1000.0,
        preferred_deployment_type="Hybrid"
    )

    assert "assessment_result" in res
    assert "candidate_ranking" in res
    assert "deployment_optimization" in res
    assert "forecasting" in res
    assert "investment_recommendation" in res

    # Verify chain: Assessment -> Optimization -> Forecasting -> Investment
    opt = res["deployment_optimization"]
    forecast = res["forecasting"]
    investment = res["investment_recommendation"]

    assert opt["optimal_installed_capacity"] > 0
    assert forecast["annual_energy_forecast"] > 0
    assert investment["capex"] > 0
