"""
Energy Yield Service

Unified service orchestrating Solar, Wind, and Hybrid energy yield estimations.
Independent of Machine Learning prediction.
"""

import logging
from typing import Dict, Any, Optional

from app.services.energy.solar_energy import estimate_solar_energy
from app.services.energy.wind_energy import estimate_wind_energy
from app.services.energy.hybrid_energy import estimate_hybrid_energy
from app.services.energy.models import EnergyYieldResponse

logger = logging.getLogger("services.energy")


class EnergyYieldService:
    """
    Independent service for estimating energy yield across deployment types.
    """

    def calculate_energy_yield(
        self,
        solar_irradiance: float = 5.2,
        wind_speed: float = 6.5,
        installed_capacity: float = 1000.0,
        solar_capacity_factor: Optional[float] = 0.20,
        wind_capacity_factor: Optional[float] = 0.35,
        solar_efficiency: float = 0.85,
        wind_efficiency: float = 0.90,
        solar_loss: float = 0.10,
        wind_loss: float = 0.12,
        deployment_type: str = "Hybrid"
    ) -> Dict[str, Any]:
        """
        Estimates Solar, Wind, and Hybrid Annual Energy Yields.

        :return: Dict containing yields and metadata
        """
        logger.info("Energy Estimation Started (Deployment: %s, Capacity: %s kW)", deployment_type, installed_capacity)

        # 1. Calculate Solar Energy Yield
        solar_yield = estimate_solar_energy(
            solar_irradiance=solar_irradiance,
            installed_capacity=installed_capacity,
            capacity_factor=solar_capacity_factor,
            system_efficiency=solar_efficiency,
            operational_loss=solar_loss
        )
        logger.info("Solar Yield: %s kWh/year", solar_yield)

        # 2. Calculate Wind Energy Yield
        wind_yield = estimate_wind_energy(
            wind_speed=wind_speed,
            installed_capacity=installed_capacity,
            capacity_factor=wind_capacity_factor,
            system_efficiency=wind_efficiency,
            operational_loss=wind_loss
        )
        logger.info("Wind Yield: %s kWh/year", wind_yield)

        # 3. Calculate Hybrid Energy Yield
        hybrid_yield = estimate_hybrid_energy(solar_yield, wind_yield)
        logger.info("Hybrid Yield: %s kWh/year", hybrid_yield)

        dep_type = (deployment_type or "Hybrid").strip().capitalize()
        if dep_type == "Solar":
            annual_energy_yield = solar_yield
        elif dep_type == "Wind":
            annual_energy_yield = wind_yield
        else:
            annual_energy_yield = hybrid_yield

        response = {
            "solar_energy_yield": solar_yield,
            "wind_energy_yield": wind_yield,
            "hybrid_energy_yield": hybrid_yield,
            "annual_energy_yield": annual_energy_yield,
            "deployment_type": dep_type,
            "installed_capacity": installed_capacity
        }

        logger.info("Energy Estimation Completed successfully: Total Yield = %s kWh/year", annual_energy_yield)
        return response
