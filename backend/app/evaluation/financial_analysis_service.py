from typing import Dict, Any


class FinancialAnalysisService:
    """
    Dedicated financial evaluation service for estimating total project costs,
    annual revenue, simple payback period, and ROI for renewable installations.
    """

    # Industry benchmarks based on domain parameters (INR Defaults)
    DEFAULT_TARIFF_INR_PER_KWH = 4.50         # ₹4.50 per kWh tariff benchmark
    DEFAULT_SOLAR_COST_PER_MW = 42500000.0     # ₹4.25 Crore per MW for Solar PV (range ₹3.5–5.0 Cr/MW)
    DEFAULT_WIND_COST_PER_MW = 80000000.0      # ₹8.0 Crore per MW for Onshore Wind (range ₹6.0–10.0 Cr/MW)
    DEFAULT_INSTALLATION_ADDON_PCT = 0.10       # 10% additional balance-of-plant/EPC cost

    def estimate_project_cost(
        self, 
        installed_capacity_mw: float, 
        deployment_type: str, 
        env_features: Dict[str, Any]
    ) -> float:
        """
        Calculates total project CAPEX installation cost in INR (₹).
        Benchmark:
          - Solar: ₹3.5 - ₹5.0 Crore / MW (Default: ₹4.25 Cr)
          - Wind:  ₹6.0 - ₹10.0 Crore / MW (Default: ₹8.00 Cr)
        Allows overriding cost per MW or adding custom installation percentage.
        """
        dtype = deployment_type.lower()
        
        # Base cost selection based on technology
        if "custom_cost_per_mw" in env_features:
            base_cost = installed_capacity_mw * float(env_features["custom_cost_per_mw"])
        elif "hybrid" in dtype:
            solar_mw = float(env_features.get("solar_capacity_mw", installed_capacity_mw * 0.6))
            wind_mw = float(env_features.get("wind_capacity_mw", installed_capacity_mw * 0.4))
            base_cost = (solar_mw * self.DEFAULT_SOLAR_COST_PER_MW) + (wind_mw * self.DEFAULT_WIND_COST_PER_MW)
        elif "wind" in dtype:
            base_cost = installed_capacity_mw * self.DEFAULT_WIND_COST_PER_MW
        else:
            base_cost = installed_capacity_mw * self.DEFAULT_SOLAR_COST_PER_MW

        # Additional installation / balance of plant percentage
        addon_pct = float(env_features.get("installation_addon_pct", self.DEFAULT_INSTALLATION_ADDON_PCT))
        total_project_cost = base_cost * (1.0 + addon_pct)

        return round(total_project_cost, 2)

    def estimate_annual_revenue(
        self, 
        annual_energy_yield_mwh: float, 
        env_features: Dict[str, Any]
    ) -> float:
        """
        Estimates annual gross revenue in INR (₹) from MWh energy yield.
        Formula: Yield (kWh) * Tariff (₹/kWh)
        """
        tariff_per_kwh = float(env_features.get("electricity_tariff", self.DEFAULT_TARIFF_INR_PER_KWH))
        yield_kwh = annual_energy_yield_mwh * 1000.0  # Convert MWh to kWh
        
        annual_revenue = yield_kwh * tariff_per_kwh
        return round(annual_revenue, 2)

    def calculate_payback_period(
        self, 
        total_project_cost: float, 
        annual_revenue: float
    ) -> float:
        """
        Estimates project payback period in years.
        Handles zero or negative revenue edge cases to avoid division-by-zero errors.
        """
        if annual_revenue <= 0.0 or total_project_cost <= 0.0:
            return 999.99  # Safe fallback representing indefinite payback

        payback_years = total_project_cost / annual_revenue
        return round(payback_years, 2)

    def calculate_roi(
        self, 
        total_project_cost: float, 
        annual_revenue: float, 
        project_lifespan_years: int = 25
    ) -> float:
        """
        Calculates Return on Investment (ROI) percentage over total project lifespan.
        Formula: [((Annual Revenue * Lifespan) - Total Cost) / Total Cost] * 100
        """
        if total_project_cost <= 0.0:
            return 0.0

        total_lifetime_revenue = annual_revenue * project_lifespan_years
        net_profit = total_lifetime_revenue - total_project_cost
        
        roi_percentage = (net_profit / total_project_cost) * 100.0
        return round(roi_percentage, 2)

    def run_financial_analysis(
        self, 
        deployment_type: str, 
        annual_energy_yield_mwh: float, 
        env_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main routing entry point for full financial valuation pass."""
        capacity_mw = float(env_features.get("installed_capacity_mw", 10.0))
        tariff_per_kwh = float(env_features.get("electricity_tariff", self.DEFAULT_TARIFF_INR_PER_KWH))
        lifespan_years = int(env_features.get("project_lifespan_years", 25))

        # Perform calculations
        total_cost = self.estimate_project_cost(capacity_mw, deployment_type, env_features)
        annual_revenue = self.estimate_annual_revenue(annual_energy_yield_mwh, env_features)
        payback_period = self.calculate_payback_period(total_cost, annual_revenue)
        roi_pct = self.calculate_roi(total_cost, annual_revenue, lifespan_years)

        return {
            "electricity_tariff_inr_kwh": tariff_per_kwh,
            "estimated_project_cost_inr": total_cost,
            "annual_revenue_inr": annual_revenue,
            "payback_period_years": payback_period,
            "roi_percentage": roi_pct,
            "project_lifespan_years": lifespan_years
        }