"""
Data Models for Energy Yield Estimation Module
"""

from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, Any


class SolarEnergyInput(BaseModel):
    solar_irradiance: float = Field(..., description="Solar irradiance in kWh/m2/day or W/m2")
    installed_capacity: float = Field(..., description="Installed capacity in kW")
    capacity_factor: float = Field(..., description="Capacity factor (0-100% or 0-1.0)")
    system_efficiency: float = Field(0.85, description="System efficiency fraction (default 0.85)")
    operational_loss: float = Field(0.10, description="Estimated operational losses fraction (default 0.10)")


class WindEnergyInput(BaseModel):
    wind_speed: float = Field(..., description="Wind speed in m/s")
    installed_capacity: float = Field(..., description="Installed capacity in kW")
    capacity_factor: float = Field(..., description="Capacity factor (0-100% or 0-1.0)")
    system_efficiency: float = Field(0.90, description="System efficiency fraction (default 0.90)")
    operational_loss: float = Field(0.12, description="Estimated operational losses fraction (default 0.12)")


class HybridEnergyInput(BaseModel):
    solar_yield: float = Field(..., description="Annual Solar energy yield in kWh/year")
    wind_yield: float = Field(..., description="Annual Wind energy yield in kWh/year")


class EnergyYieldResponse(BaseModel):
    solar_energy_yield: float = Field(..., description="Annual Solar Energy Yield (kWh/year)")
    wind_energy_yield: float = Field(..., description="Annual Wind Energy Yield (kWh/year)")
    hybrid_energy_yield: float = Field(..., description="Annual Hybrid Energy Yield (kWh/year)")
    deployment_type: str = Field("Hybrid", description="Deployment type (Solar, Wind, Hybrid)")
    installed_capacity: float = Field(..., description="Installed capacity in kW")
    details: Optional[Dict[str, Any]] = None
