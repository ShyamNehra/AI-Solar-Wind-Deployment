/**
 * Centralized API client for the Solar & Wind Platform.
 * Communicates with the FastAPI backend endpoint `/analysis`.
 */

const API_BASE_URL = window.location.origin;

/**
 * Sends a POST /analysis request to run the complete site analysis pipeline.
 *
 * @param {number} latitude - Latitude coordinate (-90.0 to 90.0).
 * @param {number} longitude - Longitude coordinate (-180.0 to 180.0).
 * @param {Object} configuration - Optional parameters override (efficiency, cost, tariffs, terrain etc.)
 * @returns {Promise<Object>} The parsed AnalysisResponse object from the server.
 */
async function analyzeSite(latitude, longitude, configuration = {}) {
    // 1. Build request payload matching AnalysisRequest schema fields
    const payload = {
        project_name: configuration.project_name || "Ad-hoc Site Analysis",
        location: configuration.location || `Coords: ${latitude}, ${longitude}`,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        
        // Site suitability parameters with defaults
        elevation: (configuration.elevation !== undefined && configuration.elevation !== null && !isNaN(parseFloat(configuration.elevation))) ? parseFloat(configuration.elevation) : 10.0,
        slope: (configuration.slope !== undefined && configuration.slope !== null && !isNaN(parseFloat(configuration.slope))) ? parseFloat(configuration.slope) : 2.0,
        distance_to_road: (configuration.distance_to_road !== undefined && configuration.distance_to_road !== null && !isNaN(parseFloat(configuration.distance_to_road))) ? parseFloat(configuration.distance_to_road) : 1.5,
        distance_to_grid: (configuration.distance_to_grid !== undefined && configuration.distance_to_grid !== null && !isNaN(parseFloat(configuration.distance_to_grid))) ? parseFloat(configuration.distance_to_grid) : 3.5,
        protected_area_distance: (configuration.protected_area_distance !== undefined && configuration.protected_area_distance !== null && !isNaN(parseFloat(configuration.protected_area_distance))) ? parseFloat(configuration.protected_area_distance) : 10.0,
        environmental_impact_level: (configuration.environmental_impact_level !== undefined && configuration.environmental_impact_level !== null && !isNaN(parseFloat(configuration.environmental_impact_level))) ? parseFloat(configuration.environmental_impact_level) : 1.0,
        land_cost_per_acre: (configuration.land_cost_per_acre !== undefined && configuration.land_cost_per_acre !== null && !isNaN(parseFloat(configuration.land_cost_per_acre))) ? parseFloat(configuration.land_cost_per_acre) : 10000.0,
        grid_connection_cost: (configuration.grid_connection_cost !== undefined && configuration.grid_connection_cost !== null && !isNaN(parseFloat(configuration.grid_connection_cost))) ? parseFloat(configuration.grid_connection_cost) : 50000.0,

        // Energy yield parameters
        installed_capacity_kw: (configuration.installed_capacity_kw !== undefined && configuration.installed_capacity_kw !== null && !isNaN(parseFloat(configuration.installed_capacity_kw))) ? parseFloat(configuration.installed_capacity_kw) : 1000.0,
        solar_system_efficiency: (configuration.solar_system_efficiency !== undefined && configuration.solar_system_efficiency !== null && !isNaN(parseFloat(configuration.solar_system_efficiency))) ? parseFloat(configuration.solar_system_efficiency) : 0.80,
        wind_operational_losses: (configuration.wind_operational_losses !== undefined && configuration.wind_operational_losses !== null && !isNaN(parseFloat(configuration.wind_operational_losses))) ? parseFloat(configuration.wind_operational_losses) : 0.15,
        solar_capacity_factor: (configuration.solar_capacity_factor !== undefined && configuration.solar_capacity_factor !== null && !isNaN(parseFloat(configuration.solar_capacity_factor))) ? parseFloat(configuration.solar_capacity_factor) : null,
        wind_capacity_factor: (configuration.wind_capacity_factor !== undefined && configuration.wind_capacity_factor !== null && !isNaN(parseFloat(configuration.wind_capacity_factor))) ? parseFloat(configuration.wind_capacity_factor) : null,

        // Financial analysis parameters
        electricity_tariff_inr_per_kwh: (configuration.electricity_tariff_inr_per_kwh !== undefined && configuration.electricity_tariff_inr_per_kwh !== null && !isNaN(parseFloat(configuration.electricity_tariff_inr_per_kwh))) ? parseFloat(configuration.electricity_tariff_inr_per_kwh) : 7.0,
        cost_per_kw: (configuration.cost_per_kw !== undefined && configuration.cost_per_kw !== null && !isNaN(parseFloat(configuration.cost_per_kw))) ? parseFloat(configuration.cost_per_kw) : 25000.0,
        additional_installation_percentage: (configuration.additional_installation_percentage !== undefined && configuration.additional_installation_percentage !== null && !isNaN(parseFloat(configuration.additional_installation_percentage))) ? parseFloat(configuration.additional_installation_percentage) : 10.0
    };

    // 2. Perform request
    let response;
    try {
        response = await fetch(`${API_BASE_URL}/analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
    } catch (networkError) {
        throw new Error("Unable to connect to the analysis server. Please make sure the backend is running.");
    }

    // 3. Handle response errors
    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            throw new Error(`HTTP Error ${response.status}: Server returned an unparseable response.`);
        }

        // Pydantic / FastAPI ValidationError formatting mapping
        if (errorData && errorData.detail) {
            if (Array.isArray(errorData.detail)) {
                // Extract clean readable sentences from Pydantic detail list
                const validationMsg = errorData.detail.map(err => {
                    const field = err.loc[err.loc.length - 1];
                    return `${field}: ${err.msg}`;
                }).join('. ');
                throw new Error(`Validation Error: ${validationMsg}`);
            }
            throw new Error(errorData.detail);
        }
        throw new Error(`HTTP Error ${response.status}: Site analysis failed.`);
    }

    // 4. Return successful parsed JSON data
    return await response.json();
}
