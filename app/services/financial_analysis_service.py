class FinancialAnalysisService:
    """
    Service responsible for conducting financial estimations for solar, wind, and hybrid projects.
    
    NOTE: These calculations represent baseline planning estimates for planning purposes,
    and must not be treated as bankable solar or wind resource assessments.
    """

    def estimate_annual_revenue(
        self,
        annual_energy_yield_kwh: float,
        electricity_tariff_inr_per_kwh: float
    ) -> float:
        """
        Estimate the annual revenue in INR.
        Formula: annual_revenue = annual_energy_yield_kwh * electricity_tariff_inr_per_kwh
        """
        if annual_energy_yield_kwh < 0.0:
            raise ValueError("Annual energy yield must be non-negative.")
        if electricity_tariff_inr_per_kwh < 0.0:
            raise ValueError("Electricity tariff must be non-negative.")

        annual_revenue = annual_energy_yield_kwh * electricity_tariff_inr_per_kwh
        return round(annual_revenue, 2)

    def estimate_project_cost(
        self,
        installed_capacity_kw: float,
        cost_per_kw: float,
        additional_installation_percentage: float = 0.0
    ) -> float:
        """
        Estimate the total project cost in INR.
        Formula:
        base_cost = installed_capacity_kw * cost_per_kw
        total_project_cost = base_cost + (base_cost * additional_installation_percentage / 100)
        """
        if installed_capacity_kw < 0.0:
            raise ValueError("Installed capacity must be non-negative.")
        if cost_per_kw < 0.0:
            raise ValueError("Cost per kW must be non-negative.")
        if additional_installation_percentage < 0.0:
            raise ValueError("Additional installation percentage must be non-negative.")

        base_cost = installed_capacity_kw * cost_per_kw
        additional_cost = base_cost * (additional_installation_percentage / 100.0)
        total_project_cost = base_cost + additional_cost
        return round(total_project_cost, 2)

    def calculate_payback_period(
        self,
        total_project_cost: float,
        annual_revenue: float
    ) -> float:
        """
        Calculate the payback period in years.
        Formula: payback_period_years = total_project_cost / annual_revenue
        
        Edge cases:
        - If annual revenue <= 0, payback period is undefined/infinite (returns -1.0).
        - If total project cost is 0, payback period is immediate (returns 0.0).
        """
        if total_project_cost < 0.0:
            raise ValueError("Total project cost must be non-negative.")
        
        # Payback period is undefined/infinite if revenue is zero or negative
        if annual_revenue <= 0.0:
            return -1.0
            
        # If cost is zero, payback period is immediate (0.0)
        if total_project_cost == 0.0:
            return 0.0

        payback_period_years = total_project_cost / annual_revenue
        return round(payback_period_years, 2)

    def calculate_roi(
        self,
        annual_revenue: float,
        total_project_cost: float
    ) -> float:
        """
        Calculate the Return on Investment (ROI) as a percentage.
        Formula: ROI (%) = (annual_revenue / total_project_cost) * 100
        
        Edge cases:
        - If total project cost is <= 0, ROI is undefined (returns -1.0).
        """
        if total_project_cost < 0.0:
            raise ValueError("Total project cost must be non-negative.")

        # ROI is undefined if project cost is zero
        if total_project_cost == 0.0:
            return -1.0

        roi_percentage = (annual_revenue / total_project_cost) * 100.0
        return round(roi_percentage, 2)
