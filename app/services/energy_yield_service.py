class EnergyYieldService:
    """
    Service responsible for estimating annual energy yield for solar, wind, and hybrid configurations.
    
    NOTE: These calculations represent baseline engineering estimates for planning purposes,
    and must not be treated as bankable solar or wind resource assessments.
    """

    def validate_inputs(
        self,
        installed_capacity_kw: float,
        solar_system_efficiency: float,
        wind_operational_losses: float,
        solar_capacity_factor: float | None = None,
        wind_capacity_factor: float | None = None
    ):
        """
        Validate that capacity, efficiency, capacity factor, and losses are within sensible bounds.
        """
        if installed_capacity_kw <= 0.0:
            raise ValueError("Installed capacity must be greater than 0 kW.")
        if not (0.0 <= solar_system_efficiency <= 1.0):
            raise ValueError("Solar system efficiency must be between 0.0 and 1.0 (0% and 100%).")
        if not (0.0 <= wind_operational_losses <= 1.0):
            raise ValueError("Wind operational losses must be between 0.0 and 1.0 (0% and 100%).")
        
        if solar_capacity_factor is not None and not (0.0 <= solar_capacity_factor <= 1.0):
            raise ValueError("Solar capacity factor must be between 0.0 and 1.0.")
        if wind_capacity_factor is not None and not (0.0 <= wind_capacity_factor <= 1.0):
            raise ValueError("Wind capacity factor must be between 0.0 and 1.0.")

    def estimate_solar_energy_yield(
        self,
        solar_irradiance: float,
        installed_capacity_kw: float,
        system_efficiency: float,
        solar_capacity_factor: float | None = None
    ) -> float:
        """
        Estimate the annual solar energy yield in kWh.
        Consistently calculates yield via capacity factor:
        E_annual = Installed Capacity (kW) * 8760 (hours/year) * Capacity Factor * System Efficiency
        """
        self.validate_inputs(
            installed_capacity_kw=installed_capacity_kw,
            solar_system_efficiency=system_efficiency,
            wind_operational_losses=0.0,
            solar_capacity_factor=solar_capacity_factor
        )

        # Derive or use capacity factor
        if solar_capacity_factor is None:
            # Baseline rule: daily capacity factor = daily peak sun hours (irradiance in kWh/m2/day) / 24 hours
            cf = max(0.0, min(1.0, solar_irradiance / 24.0))
        else:
            cf = solar_capacity_factor

        annual_yield = installed_capacity_kw * 8760.0 * cf * system_efficiency
        return round(annual_yield, 2)

    def estimate_wind_energy_yield(
        self,
        wind_speed: float,
        installed_capacity_kw: float,
        wind_capacity_factor: float | None = None,
        losses: float = 0.15
    ) -> float:
        """
        Estimate the annual wind energy yield in kWh.
        E_annual = Installed Capacity (kW) * 8760 (hours/year) * Capacity Factor * (1 - Losses)
        """
        self.validate_inputs(
            installed_capacity_kw=installed_capacity_kw,
            solar_system_efficiency=1.0,
            wind_operational_losses=losses,
            wind_capacity_factor=wind_capacity_factor
        )

        # Derive or use capacity factor
        if wind_capacity_factor is None:
            # Baseline rule: estimated capacity factor based on average wind speed (clamped between 5% and 50%)
            cf = max(0.05, min(0.50, 0.08 * (wind_speed - 2.0)))
        else:
            cf = wind_capacity_factor

        annual_yield = installed_capacity_kw * 8760.0 * cf * (1.0 - losses)
        return round(annual_yield, 2)

    def estimate_hybrid_energy_yield(
        self,
        solar_yield: float,
        wind_yield: float,
        hybrid_efficiency: float = 0.95
    ) -> float:
        """
        Estimate the annual hybrid energy yield in kWh.
        Applies a grid integration/inverter overlap efficiency adjustment to the sum of yields.
        NOTE: Crucially uses pre-calculated solar and wind yields (which already incorporate their respective
        system efficiency and losses) to ensure loss adjustments are not applied twice.
        
        Assumes the total hybrid system capacity is split 50/50 between solar and wind components,
        giving: E_hybrid = (E_solar_full + E_wind_full) * 0.5 * hybrid_efficiency
        """
        if solar_yield < 0.0 or wind_yield < 0.0:
            raise ValueError("Energy yields must be non-negative.")
        if not (0.0 <= hybrid_efficiency <= 1.0):
            raise ValueError("Hybrid integration efficiency must be between 0.0 and 1.0.")

        combined_yield = (solar_yield + wind_yield) * 0.5 * hybrid_efficiency
        return round(combined_yield, 2)
