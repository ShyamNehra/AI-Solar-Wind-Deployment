from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


# Enums and Schemas

class DeploymentType(str, Enum):
    SOLAR = "Solar"
    WIND = "Wind"
    HYBRID = "Hybrid"


class EnergyEstimationRequest(BaseModel):
    site_id: str
    deployment_type: DeploymentType
    solar_capacity_mw: float = Field(default=0.0, ge=0.0, description="Installed Solar capacity in Megawatts")
    wind_capacity_mw: float = Field(default=0.0, ge=0.0, description="Installed Wind capacity in Megawatts")
    solar_capacity_factor: float = Field(default=0.20, ge=0.0, le=1.0, description="Solar CF (typically 0.15 - 0.28)")
    wind_capacity_factor: float = Field(default=0.35, ge=0.0, le=1.0, description="Wind CF (typically 0.25 - 0.50)")


class EnergyEstimationResult(BaseModel):
    site_id: str
    deployment_type: DeploymentType
    annual_solar_mwh: float
    annual_wind_mwh: float
    total_annual_mwh: float
    capacity_weighted_cf: float  # Combined effective capacity factor


# Task 1 & Task 2: Core Estimation Functions

ANNUAL_OPERATING_HOURS = 8760  # 24 hours * 365 days


def calculate_annual_solar_energy(capacity_mw: float, capacity_factor: float) -> float:
    """
    Task 1: Estimates annual solar energy generation in MWh.
    Formula: Installed Capacity (MW) * Capacity Factor * 8760 hours
    """
    if capacity_mw <= 0 or capacity_factor <= 0:
        return 0.0
    return round(capacity_mw * capacity_factor * ANNUAL_OPERATING_HOURS, 2)


def calculate_annual_wind_energy(capacity_mw: float, capacity_factor: float) -> float:
    """
    Task 2: Estimates annual wind energy generation in MWh.
    Formula: Installed Capacity (MW) * Capacity Factor * 8760 hours
    """
    if capacity_mw <= 0 or capacity_factor <= 0:
        return 0.0
    return round(capacity_mw * capacity_factor * ANNUAL_OPERATING_HOURS, 2)


# Task 3 & Task 4: Energy Estimation Service (Includes Hybrid Engine)

class EnergyEstimationService:
    @staticmethod
    def estimate_energy(request: EnergyEstimationRequest) -> EnergyEstimationResult:
        solar_mwh = 0.0
        wind_mwh = 0.0

        if request.deployment_type in (DeploymentType.SOLAR, DeploymentType.HYBRID):
            solar_mwh = calculate_annual_solar_energy(
                capacity_mw=request.solar_capacity_mw,
                capacity_factor=request.solar_capacity_factor
            )

        if request.deployment_type in (DeploymentType.WIND, DeploymentType.HYBRID):
            wind_mwh = calculate_annual_wind_energy(
                capacity_mw=request.wind_capacity_mw,
                capacity_factor=request.wind_capacity_factor
            )

        # Task 4: Combine outputs for Hybrid or Single deployment types
        total_mwh = round(solar_mwh + wind_mwh, 2)

        # Compute weighted average Capacity Factor across total installed capacity
        total_capacity_mw = 0.0
        if request.deployment_type in (DeploymentType.SOLAR, DeploymentType.HYBRID):
            total_capacity_mw += request.solar_capacity_mw
        if request.deployment_type in (DeploymentType.WIND, DeploymentType.HYBRID):
            total_capacity_mw += request.wind_capacity_mw

        weighted_cf = 0.0
        if total_capacity_mw > 0:
            weighted_cf = round(total_mwh / (total_capacity_mw * ANNUAL_OPERATING_HOURS), 4)

        return EnergyEstimationResult(
            site_id=request.site_id,
            deployment_type=request.deployment_type,
            annual_solar_mwh=solar_mwh,
            annual_wind_mwh=wind_mwh,
            total_annual_mwh=total_mwh,
            capacity_weighted_cf=weighted_cf
        )


# Task 5: Validation Suite

def run_validation_tests():
    print("--- Running Energy Estimation Engine Validation Tests ---")
    service = EnergyEstimationService()

    # Site A: Pure Solar
    site_a = EnergyEstimationRequest(
        site_id="Site_A_Solar",
        deployment_type=DeploymentType.SOLAR,
        solar_capacity_mw=50.0,
        solar_capacity_factor=0.22
    )

    # Site B: Pure Wind
    site_b = EnergyEstimationRequest(
        site_id="Site_B_Wind",
        deployment_type=DeploymentType.WIND,
        wind_capacity_mw=100.0,
        wind_capacity_factor=0.38
    )

    # Site C: Hybrid Site (50 MW Solar + 50 MW Wind)
    site_c = EnergyEstimationRequest(
        site_id="Site_C_Hybrid",
        deployment_type=DeploymentType.HYBRID,
        solar_capacity_mw=50.0,
        wind_capacity_mw=50.0,
        solar_capacity_factor=0.22,
        wind_capacity_factor=0.38
    )

    res_a = service.estimate_energy(site_a)
    res_b = service.estimate_energy(site_b)
    res_c = service.estimate_energy(site_c)

    # Check 1: Higher capacity factor produces higher energy output given equal capacity
    site_a_higher_cf = site_a.model_copy(update={"solar_capacity_factor": 0.25})
    res_a_higher = service.estimate_energy(site_a_higher_cf)
    
    assert res_a_higher.annual_solar_mwh > res_a.annual_solar_mwh, \
        "Failed: Higher capacity factor must produce higher annual yield!"
    print(" ✓ Check 1 Passed: Higher capacity factor accurately produces higher annual yield.")

    # Check 2: Hybrid site correctly combines individual solar and wind outputs
    assert res_c.annual_solar_mwh == res_a.annual_solar_mwh, \
        "Failed: Solar component in hybrid mismatch!"
    assert res_c.total_annual_mwh == (res_c.annual_solar_mwh + res_c.annual_wind_mwh), \
        "Failed: Hybrid total output does not equal sum of solar and wind components!"
    print(f" ✓ Check 2 Passed: Hybrid combined output correct ({res_c.total_annual_mwh:,} MWh).")

    # Check 3: Linear scalability across different capacities
    site_a_double = site_a.model_copy(update={"solar_capacity_mw": 100.0})
    res_a_double = service.estimate_energy(site_a_double)
    assert round(res_a_double.annual_solar_mwh, 1) == round(2 * res_a.annual_solar_mwh, 1), \
        "Failed: Scaling capacity did not scale output linearly!"
    print(" ✓ Check 3 Passed: Estimation logic remains consistent when doubling capacity.")

    print("\nSummary of Evaluated Sites:")
    for res in [res_a, res_b, res_c]:
        print(f" - [{res.site_id}] Type: {res.deployment_type.value:<6} | Total Yield: {res.total_annual_mwh:>10,.2f} MWh | Weighted CF: {res.capacity_weighted_cf*100:.1f}%")

    print("\nAll validation checks passed successfully!")


if __name__ == "__main__":
    run_validation_tests()