class FinancialAnalysisService:
    """
    Service for financial analysis of renewable energy projects.
    """

    def estimate_annual_revenue(
        self,
        annual_energy_mwh,
        electricity_tariff
    ):
        """
        Estimate annual revenue.

        annual_energy_mwh : MWh/year
        electricity_tariff : ₹/kWh
        """

        annual_energy_kwh = annual_energy_mwh * 1000

        annual_revenue = (
            annual_energy_kwh
            * electricity_tariff
        )

        return round(annual_revenue, 2)

    def estimate_project_cost(
        self,
        installed_capacity,
        cost_per_mw,
        additional_installation_percent=0
    ):
        """
        Estimate total project cost.
        """

        base_cost = (
            installed_capacity
            * cost_per_mw
        )

        additional_cost = (
            base_cost
            * additional_installation_percent
            / 100
        )

        total_cost = (
            base_cost
            + additional_cost
        )

        return round(total_cost, 2)

    def calculate_payback_period(
        self,
        total_project_cost,
        annual_revenue
    ):
        """
        Estimate payback period.
        """

        if annual_revenue <= 0:
            return None

        payback = (
            total_project_cost
            / annual_revenue
        )

        return round(payback, 2)

    def calculate_roi(
        self,
        annual_revenue,
        total_project_cost
    ):
        """
        Calculate ROI.
        """

        if total_project_cost <= 0:
            return None

        roi = (
            annual_revenue
            / total_project_cost
        ) * 100

        return round(roi, 2)

    def analyze_finances(
        self,
        installed_capacity,
        annual_energy_mwh,
        electricity_tariff=6,
        cost_per_mw=60000000,
        installation_percent=10
    ):
        """
        Complete financial analysis.
        """

        annual_revenue = self.estimate_annual_revenue(
            annual_energy_mwh,
            electricity_tariff
        )

        project_cost = self.estimate_project_cost(
            installed_capacity,
            cost_per_mw,
            installation_percent
        )

        payback = self.calculate_payback_period(
            project_cost,
            annual_revenue
        )

        roi = self.calculate_roi(
            annual_revenue,
            project_cost
        )

        return {

            "electricity_tariff_rs_per_kwh": electricity_tariff,

            "cost_per_mw_rs": cost_per_mw,

            "annual_revenue_rs": annual_revenue,

            "estimated_project_cost_rs": project_cost,

            "payback_period_years": payback,

            "roi_percent": roi

        }