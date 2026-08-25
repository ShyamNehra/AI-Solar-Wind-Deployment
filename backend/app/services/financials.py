def estimate_energy_yield(strategy, capacity_mw, solar_irr, wind_speed):
    """
    Estimates the annual energy yield in kWh based on tech, capacity, and resource metrics.
    """
    # 8760 hours in a year
    hours_per_year = 8760.0
    
    # Standard engineering constants
    solar_cf = min(max(solar_irr / 10.0, 0.1), 0.35)  # proxy capacity factor based on GHI
    wind_cf = min(max(wind_speed / 25.0, 0.15), 0.5)  # proxy capacity factor based on wind speed
    
    solar_efficiency = 0.82
    wind_efficiency = 0.90
    
    if strategy == "Solar":
        yield_kwh = capacity_mw * 1000.0 * hours_per_year * solar_cf * solar_efficiency
    elif strategy == "Wind":
        yield_kwh = capacity_mw * 1000.0 * hours_per_year * wind_cf * wind_efficiency
    elif strategy == "Hybrid":
        # Assume 50/50 capacity split for generation estimates
        cap_solar = capacity_mw * 0.5
        cap_wind = capacity_mw * 0.5
        yield_solar = cap_solar * 1000.0 * hours_per_year * solar_cf * solar_efficiency
        yield_wind = cap_wind * 1000.0 * hours_per_year * wind_cf * wind_efficiency
        yield_kwh = yield_solar + yield_wind
    else:
        yield_kwh = 0.0
        
    return round(yield_kwh, 2)

def calculate_financials(yield_kwh, strategy, capacity_mw, tariff_inr_kwh=5.5):
    """
    Computes total project cost, annual revenue, payback period, and ROI.
    """
    # Base costs per MW in INR (Rupees): Solar = 4.5 Crore, Wind = 6.5 Crore, Hybrid = 5.5 Crore
    cost_per_mw = {
        "Solar": 45000000.0,
        "Wind": 65000000.0,
        "Hybrid": 55000000.0,
        "None": 0.0
    }
    
    project_cost = capacity_mw * cost_per_mw.get(strategy, 45000000.0)
    # Plus 10% for installation grid integration
    project_cost = project_cost * 1.10
    
    # Revenue
    annual_revenue = yield_kwh * tariff_inr_kwh
    
    # Payback & ROI
    if annual_revenue > 0:
        payback_period = project_cost / annual_revenue
        roi = (annual_revenue / project_cost) * 100.0
    else:
        payback_period = 999.0
        roi = 0.0
        
    return {
        "estimated_project_cost_inr": round(project_cost, 2),
        "annual_revenue_inr": round(annual_revenue, 2),
        "payback_period_years": round(payback_period, 2),
        "roi_percentage": round(roi, 2)
    }
