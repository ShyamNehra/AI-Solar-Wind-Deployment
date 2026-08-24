"""
Module 10: Optimization Validation Tests

Deterministic test suite validating:
1. Different environmental conditions produce different deployment strategies.
2. Different land areas produce different recommended capacities.
3. Different constraints produce different optimization scores.
4. Different resource combinations produce Solar, Wind, or Hybrid recommendations.
5. Expansion status changes correctly.
6. Capacity Factor is calculated correctly using EnergyEstimationService.
7. Deployment Plan changes according to optimization parameters.
"""

import pytest
from app.services.deployment_optimization_service import DeploymentOptimizationService
from app.services.energy_estimation_service import EnergyEstimationService


@pytest.fixture
def opt_service():
    return DeploymentOptimizationService()


def test_different_resources_produce_different_technologies(opt_service):
    """
    Verify different resource combinations produce Solar, Wind, or Hybrid recommendations.
    """
    # High solar, Low wind -> Solar
    solar_res = opt_service.optimize_deployment(
        solar_resource=8.5, wind_resource=2.0, deployment_type="Hybrid"
    )
    assert solar_res["recommended_technology"] == "Solar"

    # Low solar, High wind -> Wind
    wind_res = opt_service.optimize_deployment(
        solar_resource=2.0, wind_resource=10.0, deployment_type="Hybrid"
    )
    assert wind_res["recommended_technology"] == "Wind"

    # High solar, High wind -> Hybrid
    hybrid_res = opt_service.optimize_deployment(
        solar_resource=7.5, wind_resource=8.0, deployment_type="Hybrid"
    )
    assert hybrid_res["recommended_technology"] == "Hybrid"


def test_different_land_areas_produce_different_capacities(opt_service):
    """
    Verify different land areas produce different recommended capacities.
    """
    large_land = opt_service.optimize_deployment(
        installed_capacity=5000.0,
        constraints={"max_land_area_sq_km": 10.0}
    )

    small_land = opt_service.optimize_deployment(
        installed_capacity=5000.0,
        constraints={"max_land_area_sq_km": 0.05}
    )

    assert small_land["recommended_installed_capacity"] < large_land["recommended_installed_capacity"]


def test_different_constraints_produce_different_scores(opt_service):
    """
    Verify different constraints produce different optimization scores.
    """
    unconstrained = opt_service.optimize_deployment(
        installed_capacity=1000.0,
        constraints={}
    )

    severely_constrained = opt_service.optimize_deployment(
        installed_capacity=5000.0,
        environmental_score=30.0,
        constraints={
            "grid_capacity": 500.0,
            "max_land_area_sq_km": 0.02,
            "environmental_restrictions": 80.0
        }
    )

    assert unconstrained["optimization_score"] > severely_constrained["optimization_score"]
    assert unconstrained["constraint_satisfaction_score"] > severely_constrained["constraint_satisfaction_score"]
    assert len(severely_constrained["constraint_violations"]) > 0


def test_expansion_status_changes_correctly(opt_service):
    """
    Verify expansion status changes correctly based on remaining land and grid capacity.
    """
    # Large land + high grid headroom + good env -> Expandable
    expandable = opt_service.optimize_deployment(
        installed_capacity=1000.0,
        land_area=20.0,
        grid_availability=10.0,
        environmental_score=85.0
    )
    assert expandable["expansion_status"] == "Expandable"

    # Tightly constrained land + zero grid headroom -> Not Expandable
    not_expandable = opt_service.optimize_deployment(
        installed_capacity=1000.0,
        land_area=0.035,
        grid_availability=1.0,
        environmental_score=40.0,
        constraints={"max_land_area_sq_km": 0.035, "grid_capacity": 1.0}
    )
    assert not_expandable["expansion_status"] == "Not Expandable"


def test_capacity_factor_calculated_correctly(opt_service):
    """
    Verify Capacity Factor is calculated correctly using EnergyEstimationService.
    """
    res = opt_service.optimize_deployment(
        installed_capacity=1000.0,
        solar_resource=6.0,
        wind_resource=6.0
    )

    rec_cap = res["recommended_installed_capacity"]
    max_possible_gen = rec_cap * 8760.0
    est_energy = res["estimated_annual_energy"]

    assert res["maximum_possible_generation"] == max_possible_gen
    assert res["capacity_factor"] == round(est_energy / max_possible_gen, 4)
    assert res["capacity_factor_pct"] == round((est_energy / max_possible_gen) * 100.0, 2)


def test_deployment_plan_changes_with_optimization(opt_service):
    """
    Verify Deployment Plan changes according to optimization parameters.
    """
    plan_solar = opt_service.optimize_deployment(
        solar_resource=9.0, wind_resource=2.0
    )

    plan_wind = opt_service.optimize_deployment(
        solar_resource=2.0, wind_resource=10.0
    )

    assert plan_solar["recommended_technology"] == "Solar"
    assert plan_solar["solar_capacity"] > 0
    assert plan_solar["wind_capacity"] == 0

    assert plan_wind["recommended_technology"] == "Wind"
    assert plan_wind["wind_capacity"] > 0
    assert plan_wind["solar_capacity"] == 0
