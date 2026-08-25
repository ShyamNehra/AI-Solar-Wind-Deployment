class EnergyEstimationService:
    """
    Service for estimating annual renewable energy generation.

    Solar and wind capacity factors are derived from the
    location-specific environmental inputs supplied by the
    analysis pipeline.
    """

    HOURS_PER_YEAR = 8760

    # ---------------------------------------------------
    # Capacity Factor Estimation
    # ---------------------------------------------------

    def get_solar_capacity_factor(self, solar_irradiance):
        """
        Estimate solar capacity factor from average daily
        solar irradiance in kWh/m²/day.
        """

        solar_irradiance = float(solar_irradiance)

        if solar_irradiance >= 6.0:
            return 0.30
        elif solar_irradiance >= 5.0:
            return 0.27
        elif solar_irradiance >= 4.0:
            return 0.25
        elif solar_irradiance >= 3.0:
            return 0.22
        else:
            return 0.18

    def get_wind_capacity_factor(self, wind_speed):
        """
        Estimate wind capacity factor from average wind speed
        in m/s.
        """

        wind_speed = float(wind_speed)

        if wind_speed >= 8.0:
            return 0.45
        elif wind_speed >= 7.0:
            return 0.42
        elif wind_speed >= 6.0:
            return 0.40
        elif wind_speed >= 5.0:
            return 0.36
        elif wind_speed >= 4.0:
            return 0.32
        elif wind_speed >= 3.0:
            return 0.25
        else:
            return 0.18

    # ---------------------------------------------------
    # Solar Energy
    # ---------------------------------------------------

    def estimate_solar_energy(
        self,
        installed_capacity,
        capacity_factor,
        system_efficiency
    ):
        """
        Annual solar generation in MWh.
        """

        annual_energy = (
            installed_capacity
            * self.HOURS_PER_YEAR
            * capacity_factor
            * system_efficiency
        )

        return round(max(annual_energy, 0), 2)

    # ---------------------------------------------------
    # Wind Energy
    # ---------------------------------------------------

    def estimate_wind_energy(
        self,
        installed_capacity,
        capacity_factor,
        system_efficiency
    ):
        """
        Annual wind generation in MWh.
        """

        annual_energy = (
            installed_capacity
            * self.HOURS_PER_YEAR
            * capacity_factor
            * system_efficiency
        )

        return round(max(annual_energy, 0), 2)

    # ---------------------------------------------------
    # Hybrid Energy
    # ---------------------------------------------------

    def estimate_hybrid_energy(
        self,
        installed_capacity,
        solar_capacity_factor,
        wind_capacity_factor,
        solar_efficiency,
        wind_efficiency
    ):
        """
        Estimate annual generation for a 50/50 hybrid deployment.
        """

        solar_capacity = installed_capacity * 0.50
        wind_capacity = installed_capacity * 0.50

        solar_energy = self.estimate_solar_energy(
            solar_capacity,
            solar_capacity_factor,
            solar_efficiency
        )

        wind_energy = self.estimate_wind_energy(
            wind_capacity,
            wind_capacity_factor,
            wind_efficiency
        )

        total_energy = solar_energy + wind_energy

        return {
            "annual_solar_energy_mwh": round(solar_energy, 2),
            "annual_wind_energy_mwh": round(wind_energy, 2),
            "total_annual_energy_mwh": round(total_energy, 2)
        }

    # ---------------------------------------------------
    # Main Estimation Function
    # ---------------------------------------------------

    def estimate_energy(
        self,
        site_result,
        deployment_type,
        installed_capacity,
        solar_irradiance,
        wind_speed
    ):
        """
        Estimate annual renewable energy generation using
        location-specific solar irradiance and wind speed.
        """

        solar_irradiance = float(solar_irradiance)
        wind_speed = float(wind_speed)
        installed_capacity = float(installed_capacity)

        solar_capacity_factor = self.get_solar_capacity_factor(
            solar_irradiance
        )

        wind_capacity_factor = self.get_wind_capacity_factor(
            wind_speed
        )

        solar_system_efficiency = 0.90
        wind_system_efficiency = 0.95

        solar_energy = 0.0
        wind_energy = 0.0

        if deployment_type == "Solar":

            solar_energy = self.estimate_solar_energy(
                installed_capacity,
                solar_capacity_factor,
                solar_system_efficiency
            )

        elif deployment_type == "Wind":

            wind_energy = self.estimate_wind_energy(
                installed_capacity,
                wind_capacity_factor,
                wind_system_efficiency
            )

        elif deployment_type == "Hybrid":

            hybrid = self.estimate_hybrid_energy(
                installed_capacity,
                solar_capacity_factor,
                wind_capacity_factor,
                solar_system_efficiency,
                wind_system_efficiency
            )

            solar_energy = hybrid["annual_solar_energy_mwh"]
            wind_energy = hybrid["annual_wind_energy_mwh"]

        else:
            raise ValueError(
                f"Unsupported deployment type: {deployment_type}"
            )

        total_energy = solar_energy + wind_energy

        return {
            "site_result": site_result,

            "deployment_type": deployment_type,

            "installed_capacity_mw": installed_capacity,

            "solar_irradiance": round(solar_irradiance, 3),

            "wind_speed": round(wind_speed, 3),

            "solar_capacity_factor": solar_capacity_factor,

            "wind_capacity_factor": wind_capacity_factor,

            "solar_system_efficiency": solar_system_efficiency,

            "wind_system_efficiency": wind_system_efficiency,

            "annual_solar_energy_mwh": round(solar_energy, 2),

            "annual_wind_energy_mwh": round(wind_energy, 2),

            "total_annual_energy_mwh": round(total_energy, 2)
        }