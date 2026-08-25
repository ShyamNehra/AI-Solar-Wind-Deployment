const API_BASE_URL = "http://localhost:8000";

export interface AnalysisParams {
  latitude: number;
  longitude: number;
  land_area: number;
  available_land_percent: number;
  installed_capacity: number;
}

export interface AnalysisResponse {
  location: {
    latitude: number;
    longitude: number;
  };

  environmental_data: {
    solar_features: any;
    wind_assessment: any;
  };

  site_suitability: {
    overall_score: number;
    recommendation: string;
  };

  recommended_deployment: {
    technology: string;
    capacity_mw: number;
    expansion_status: string;
  };

  technical_feasibility: {
    status: string;
    passed: boolean;
    failed_constraints: string[];
    soft_constraint_score: number;
  };

  energy_yield: {
    annual_solar_energy_mwh: number;
    annual_wind_energy_mwh: number;
    total_annual_energy_mwh: number;
  };

  financial_metrics: {
    electricity_tariff_rs_per_kwh: number;
    annual_revenue_rs: number;
    estimated_project_cost_rs: number;
    payback_period_years: number;
    roi_percent: number;
  };

  recommendation_reason: string[];

  final_recommendation: string;
}

export async function analyzeSite(
  params: AnalysisParams
): Promise<AnalysisResponse> {

  const query = new URLSearchParams({
    latitude: String(params.latitude),
    longitude: String(params.longitude),
    land_area: String(params.land_area),
    available_land_percent: String(params.available_land_percent),
    installed_capacity: String(params.installed_capacity),
  });

  const url = `${API_BASE_URL}/analysis?${query.toString()}`;

  console.log("Calling backend:", url);

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `Backend returned ${response.status}: ${text}`
    );
  }

  return await response.json();
}