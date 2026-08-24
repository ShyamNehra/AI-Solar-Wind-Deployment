"""
Deployment Optimization Service

Implements Modules 1-5 of the Deployment Intelligence Platform:
- Module 1: Deployment Optimization Engine (Solar, Wind, Hybrid technology & strategy determination)
- Module 2: Optimization Constraints (Land, Budget, Environment, Grid, Infrastructure, Transmission, Road limits)
- Module 3: Capacity Planning (Rule-based capacity estimation, Capacity Factor calculation via EnergyEstimationService)
- Module 4: Expansion Feasibility (Remaining land, remaining grid, infrastructure & env analysis)
- Module 5: Deployment Plan Generation (Unified deployment plan output)
"""

from typing import Dict, List, Optional, Any, Union
from app.services.energy_estimation_service import EnergyEstimationService


class DeploymentOptimizationService:
    """
    Service layer for optimizing renewable energy deployment parameters based on site assessment,
    ranking, resource availability, operational constraints, capacity planning, and expansion analysis.
    """

    # Estimated land requirements in sq km per MW
    SOLAR_LAND_SQ_KM_PER_MW = 0.020  # ~2 hectares / MW
    WIND_LAND_SQ_KM_PER_MW = 0.060   # ~6 hectares / MW
    HYBRID_LAND_SQ_KM_PER_MW = 0.035 # ~3.5 hectares / MW

    # Estimated CAPEX cost per kW in baseline monetary units ($ / kW)
    SOLAR_CAPEX_PER_KW = 900.0
    WIND_CAPEX_PER_KW = 1350.0
    HYBRID_CAPEX_PER_KW = 1100.0

    def __init__(self):
        self.energy_service = EnergyEstimationService()

    def optimize_deployment(
        self,
        site_ranking_result: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        overall_suitability_score: float = 75.0,
        solar_resource: float = 5.5,
        wind_resource: float = 6.2,
        terrain_score: float = 70.0,
        infrastructure_score: float = 65.0,
        environmental_score: float = 80.0,
        installed_capacity: float = 1000.0,  # kW
        land_area: Optional[float] = None,
        grid_availability: Optional[float] = None,
        deployment_type: str = "Hybrid",
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs deployment optimization, constraint evaluation, capacity planning,
        and expansion feasibility to generate a unified Deployment Plan.
        """
        constraints_cfg = constraints or {}
        if hasattr(constraints_cfg, "dict"):
            constraints_cfg = constraints_cfg.dict(exclude_unset=True)

        target_capacity = max(10.0, float(installed_capacity or 1000.0))

        # Normalize resource indicators onto a 0-100 scale for technology selection
        solar_score_norm = min(100.0, solar_resource * 14.0) if solar_resource <= 10.0 else min(100.0, solar_resource)
        wind_score_norm = min(100.0, wind_resource * 12.5) if wind_resource <= 12.0 else min(100.0, wind_resource)

        # ── Module 1: Deployment Optimization Engine (Technology & Strategy Selection) ──
        dep_type_input = (deployment_type or "Hybrid").capitalize()
        if dep_type_input not in ["Solar", "Wind", "Hybrid"]:
            dep_type_input = "Hybrid"

        if solar_score_norm > 65.0 and wind_score_norm > 65.0:
            rec_technology = "Hybrid"
        elif solar_score_norm >= wind_score_norm + 15.0:
            rec_technology = "Solar"
        elif wind_score_norm >= solar_score_norm + 15.0:
            rec_technology = "Wind"
        else:
            rec_technology = dep_type_input

        # Renewable mix split ratios
        if rec_technology == "Solar":
            solar_ratio = 1.0
            wind_ratio = 0.0
            strategy_text = "Solar Photovoltaic deployment optimized for maximum solar irradiance capture."
        elif rec_technology == "Wind":
            solar_ratio = 0.0
            wind_ratio = 1.0
            strategy_text = "Wind Turbine deployment optimized for high wind speed velocity and kinetic yield."
        else: # Hybrid
            total_res = (solar_score_norm + wind_score_norm) or 1.0
            solar_ratio = round(solar_score_norm / total_res, 2)
            wind_ratio = round(1.0 - solar_ratio, 2)
            if solar_ratio < 0.2:
                solar_ratio, wind_ratio = 0.2, 0.8
            elif solar_ratio > 0.8:
                solar_ratio, wind_ratio = 0.8, 0.2
            strategy_text = f"Hybrid Solar-Wind deployment co-locating PV ({int(solar_ratio*100)}%) and Wind ({int(wind_ratio*100)}%) to maximize capacity utilization."

        # ── Module 2: Optimization Constraints Evaluation ──
        optimal_capacity = target_capacity
        violations: List[str] = []
        satisfaction_score = 100.0

        # Constraint 1: Grid Capacity / Availability
        grid_cap = constraints_cfg.get("grid_capacity") if constraints_cfg.get("grid_capacity") is not None else grid_availability
        if grid_cap is not None and float(grid_cap) > 0:
            grid_cap_kw = float(grid_cap) * 1000.0 if float(grid_cap) <= 500.0 else float(grid_cap)
            if optimal_capacity > grid_cap_kw:
                violations.append(f"Grid capacity limit breached: target {optimal_capacity:.0f} kW exceeds grid limit {grid_cap_kw:.0f} kW.")
                optimal_capacity = grid_cap_kw
                satisfaction_score -= 20.0

        # Constraint 2: Maximum Land Area
        max_land = constraints_cfg.get("max_land_area_sq_km") or constraints_cfg.get("land_area") or land_area
        if max_land is not None and float(max_land) > 0:
            land_avail = float(max_land)
            land_per_mw = (
                self.SOLAR_LAND_SQ_KM_PER_MW if rec_technology == "Solar" else
                self.WIND_LAND_SQ_KM_PER_MW if rec_technology == "Wind" else
                self.HYBRID_LAND_SQ_KM_PER_MW
            )
            max_cap_land_kw = (land_avail / land_per_mw) * 1000.0
            if optimal_capacity > max_cap_land_kw:
                violations.append(f"Land area constraint breached: available land ({land_avail:.2f} sq km) caps capacity at {max_cap_land_kw:.0f} kW.")
                optimal_capacity = min(optimal_capacity, max_cap_land_kw)
                satisfaction_score -= 25.0
        else:
            land_avail = 10.0  # default baseline land area for expansion calculations if unconstrained

        # Constraint 3: Budget Limit
        budget_limit = constraints_cfg.get("budget_limit") or constraints_cfg.get("budget")
        if budget_limit is not None and float(budget_limit) > 0:
            b_limit = float(budget_limit)
            unit_capex = (
                self.SOLAR_CAPEX_PER_KW if rec_technology == "Solar" else
                self.WIND_CAPEX_PER_KW if rec_technology == "Wind" else
                self.HYBRID_CAPEX_PER_KW
            )
            max_cap_budget_kw = b_limit / unit_capex
            if optimal_capacity > max_cap_budget_kw:
                violations.append(f"Budget limit breached: allocated budget restricts capacity to {max_cap_budget_kw:.0f} kW.")
                optimal_capacity = min(optimal_capacity, max_cap_budget_kw)
                satisfaction_score -= 20.0

        # Constraint 4: Environmental Restrictions
        min_env = constraints_cfg.get("environmental_restrictions")
        if min_env is not None and float(min_env) > 0:
            req_env = float(min_env)
            if environmental_score < req_env:
                violations.append(f"Environmental restriction breached: site score ({environmental_score:.1f}) is below requirement ({req_env:.1f}).")
                satisfaction_score -= 25.0

        # Constraint 5: Infrastructure & Distance bounds
        max_substation_dist = constraints_cfg.get("infrastructure_availability")
        if max_substation_dist is not None and float(max_substation_dist) > 0:
            if infrastructure_score < 40.0:
                violations.append("Infrastructure restriction: access distance exceeds allowable bounds.")
                satisfaction_score -= 15.0

        max_trans_dist = constraints_cfg.get("transmission_distance")
        if max_trans_dist is not None and float(max_trans_dist) > 0:
            if float(max_trans_dist) < 5.0:
                violations.append("Transmission distance restriction: grid point is beyond preferred radius.")
                satisfaction_score -= 10.0

        max_road_dist = constraints_cfg.get("road_accessibility")
        if max_road_dist is not None and float(max_road_dist) > 0:
            if float(max_road_dist) < 2.0:
                violations.append("Road accessibility restriction: site road distance exceeds limits.")
                satisfaction_score -= 10.0

        satisfaction_score = max(0.0, round(satisfaction_score, 1))
        optimal_capacity = max(10.0, round(optimal_capacity, 1))

        # Split component capacities
        solar_capacity = round(optimal_capacity * solar_ratio, 1)
        wind_capacity = round(optimal_capacity * wind_ratio, 1)
        solar_pct = round(solar_ratio * 100.0, 1)
        wind_pct = round(wind_ratio * 100.0, 1)

        is_feasible = (satisfaction_score >= 50.0) and (optimal_capacity >= 10.0)

        # ── Module 3: Capacity Planning ──
        land_per_mw = (
            self.SOLAR_LAND_SQ_KM_PER_MW if rec_technology == "Solar" else
            self.WIND_LAND_SQ_KM_PER_MW if rec_technology == "Wind" else
            self.HYBRID_LAND_SQ_KM_PER_MW
        )
        max_possible_gen = round(optimal_capacity * 8760.0, 2)  # kWh

        # Derive capacity factors from resource indicators
        sol_cf = max(10.0, min(35.0, solar_score_norm * 0.35))
        wnd_cf = max(15.0, min(55.0, wind_score_norm * 0.45))

        energy_res = self.energy_service.estimate_energy(
            deployment_type=rec_technology,
            installed_capacity=optimal_capacity,
            operating_hours=8760.0,
            solar_capacity_factor=sol_cf,
            wind_capacity_factor=wnd_cf
        )

        estimated_annual_energy = energy_res["total_energy"]
        capacity_factor_val = round(estimated_annual_energy / max_possible_gen, 4) if max_possible_gen > 0 else 0.0
        capacity_factor_pct = round(capacity_factor_val * 100.0, 2)

        # ── Module 4: Expansion Feasibility ──
        used_land = (optimal_capacity / 1000.0) * land_per_mw
        remaining_land = max(0.0, land_avail - used_land)

        if grid_cap is not None and float(grid_cap) > 0:
            grid_cap_kw = float(grid_cap) * 1000.0 if float(grid_cap) <= 500.0 else float(grid_cap)
            remaining_grid_kw = max(0.0, grid_cap_kw - optimal_capacity)
        else:
            remaining_grid_kw = 5000.0  # Baseline default headroom

        if remaining_land >= 0.5 * land_avail and remaining_grid_kw >= 500.0 and environmental_score >= 60.0:
            expansion_status = "Expandable"
            expansion_remarks = f"Significant remaining land ({remaining_land:.2f} sq km) and grid capacity ({remaining_grid_kw:.0f} kW) allow future expansion."
        elif remaining_land >= 0.1 * land_avail and remaining_grid_kw > 0 and environmental_score >= 50.0:
            expansion_status = "Limited Expansion"
            expansion_remarks = f"Moderate remaining land ({remaining_land:.2f} sq km) supports phase-2 expansion with minor grid upgrades."
        else:
            expansion_status = "Not Expandable"
            expansion_remarks = "Site capacity fully utilized or constrained by land, grid, or environmental thresholds."

        # ── Module 5: Deployment Plan & Optimization Score ──
        if not is_feasible:
            status = "Infeasible"
            optimization_remarks = "Deployment exceeds severe site/constraint limits. Mitigation or layout changes required."
        elif len(violations) == 0:
            status = "Optimal"
            optimization_remarks = "Fully compliant deployment strategy satisfying all operational and land constraints."
        elif optimal_capacity >= target_capacity * 0.8:
            status = "Feasible"
            optimization_remarks = "Feasible deployment meeting performance objectives with minor constraint trade-offs."
        else:
            status = "Sub-optimal"
            optimization_remarks = "Target capacity scaled down to satisfy site land or grid boundary limits."

        suit_weight = 0.4
        satisfaction_weight = 0.4
        resource_weight = 0.2
        avg_res_score = (solar_score_norm + wind_score_norm) / 2.0

        overall_opt_score = round(
            (overall_suitability_score * suit_weight) +
            (satisfaction_score * satisfaction_weight) +
            (avg_res_score * resource_weight),
            1
        )
        overall_opt_score = max(0.0, min(100.0, overall_opt_score))

        return {
            # Module 1
            "recommended_technology": rec_technology,
            "recommended_deployment_type": rec_technology,
            "deployment_strategy": strategy_text,
            "optimization_score": overall_opt_score,
            "overall_optimization_score": overall_opt_score,

            # Module 2
            "constraint_satisfaction_score": satisfaction_score,
            "constraint_violations": violations if violations else ["No constraint violations"],
            "feasible": is_feasible,
            "feasibility_status": "Feasible" if is_feasible else "Not Feasible",

            # Module 3 (Capacity Planning)
            "recommended_installed_capacity": optimal_capacity,
            "recommended_capacity": optimal_capacity,
            "optimal_installed_capacity": optimal_capacity,
            "best_capacity": optimal_capacity,
            "maximum_possible_generation": max_possible_gen,
            "estimated_annual_energy": estimated_annual_energy,
            "capacity_factor": capacity_factor_val,
            "capacity_factor_pct": capacity_factor_pct,

            # Module 4 (Expansion Feasibility)
            "expansion_status": expansion_status,
            "expansion_remarks": expansion_remarks,
            "remaining_land_sq_km": round(remaining_land, 2),
            "remaining_grid_capacity_kw": round(remaining_grid_kw, 2),

            # Module 5 (Deployment Plan)
            "solar_capacity": solar_capacity,
            "wind_capacity": wind_capacity,
            "hybrid_ratio": {
                "solar": solar_ratio,
                "wind": wind_ratio
            },
            "renewable_mix": {
                "solar_pct": solar_pct,
                "wind_pct": wind_pct
            },
            "optimization_remarks": optimization_remarks,
            "optimization_status": status
        }
