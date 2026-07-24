from typing import TypedDict
from app.services.scoring_constants import (
    DEFAULT_CATEGORY_WEIGHTS,
    SOLAR_IRRADIANCE_BOUNDS,
    WIND_SPEED_BOUNDS,
    SLOPE_BOUNDS,
    GRID_DISTANCE_BOUNDS,
    ROAD_DISTANCE_BOUNDS,
)


class SiteSuitabilityResult(TypedDict):
    """
    Strongly-typed dictionary output structure for site suitability evaluation.
    """
    resource_score: float
    terrain_score: float
    infrastructure_score: float
    environmental_score: float
    economic_score: float
    overall_score: float


# =====================================================================
# Task 1: Score Normalization Functions (0 to 100)
# =====================================================================

def _min_max_scale(val: float, min_val: float, max_val: float, invert: bool = False) -> float:
    """
    Helper function to scale a continuous numerical parameter onto a 0-100 score.
    """
    if max_val <= min_val:
        return 50.0

    clamped = max(min_val, min(val, max_val))
    ratio = (clamped - min_val) / (max_val - min_val)

    if invert:
        ratio = 1.0 - ratio

    return round(ratio * 100.0, 2)


def normalize_solar(solar_irradiance: float) -> float:
    """Normalize solar irradiance (kWh/m²/day) to a score between 0 and 100."""
    return _min_max_scale(solar_irradiance, SOLAR_IRRADIANCE_BOUNDS[0], SOLAR_IRRADIANCE_BOUNDS[1])


def normalize_wind(wind_speed: float) -> float:
    """Normalize wind speed (m/s) to a score between 0 and 100."""
    return _min_max_scale(wind_speed, WIND_SPEED_BOUNDS[0], WIND_SPEED_BOUNDS[1])


def normalize_slope(slope: float) -> float:
    """Normalize slope (degrees) to a score between 0 and 100 (lower slope is better)."""
    return _min_max_scale(slope, SLOPE_BOUNDS[0], SLOPE_BOUNDS[1], invert=True)


def normalize_distance_grid(distance_to_grid: float) -> float:
    """Normalize grid distance (km) to a score between 0 and 100 (closer is better)."""
    return _min_max_scale(distance_to_grid, GRID_DISTANCE_BOUNDS[0], GRID_DISTANCE_BOUNDS[1], invert=True)


def normalize_distance_road(distance_to_road: float) -> float:
    """Normalize road distance (km) to a score between 0 and 100 (closer is better)."""
    return _min_max_scale(distance_to_road, ROAD_DISTANCE_BOUNDS[0], ROAD_DISTANCE_BOUNDS[1], invert=True)


# =====================================================================
# Task 2: Category-wise Scoring Functions
# =====================================================================

def calculate_resource_score(solar_irradiance: float, wind_speed: float) -> float:
    """
    Calculate independent Renewable Resource Score (0 to 100).
    Combines normalized solar and wind parameters equally or by dominant resource.
    """
    solar_score = normalize_solar(solar_irradiance)
    wind_score = normalize_wind(wind_speed)
    # Average resource potential
    return round((solar_score + wind_score) / 2.0, 2)


def calculate_terrain_score(slope: float, elevation: float = 0.0) -> float:
    """
    Calculate independent Terrain Score (0 to 100).
    Evaluates slope flatness; optionally incorporates elevation factor.
    """
    slope_score = normalize_slope(slope)
    # Elevation factor: penalty for extreme elevations (> 2500m)
    elevation_penalty = 0.0
    if elevation > 2500.0:
        elevation_penalty = min(20.0, (elevation - 2500.0) / 100.0)

    return round(max(0.0, slope_score - elevation_penalty), 2)


def calculate_infrastructure_score(distance_to_road: float, distance_to_grid: float) -> float:
    """
    Calculate independent Infrastructure Score (0 to 100).
    Combines proximity to grid (60% weight) and proximity to road (40% weight).
    """
    grid_score = normalize_distance_grid(distance_to_grid)
    road_score = normalize_distance_road(distance_to_road)
    return round((grid_score * 0.60) + (road_score * 0.40), 2)


def calculate_environmental_score(
    protected_area_distance: float = 10.0,
    environmental_impact_level: float = 0.0
) -> float:
    """
    Calculate independent Environmental Score (0 to 100).
    Higher score indicates lower environmental risk/impact.
    """
    # Distance to protected area: 0km = 0 score, >=20km = 100 score
    dist_score = _min_max_scale(protected_area_distance, 0.0, 20.0)
    impact_penalty = min(30.0, environmental_impact_level * 10.0)
    return round(max(0.0, dist_score - impact_penalty), 2)


def calculate_economic_score(
    land_cost_per_acre: float = 10000.0,
    grid_connection_cost: float = 50000.0
) -> float:
    """
    Calculate independent Economic Score (0 to 100).
    Lower costs yield a higher economic score.
    """
    # Scale land cost: $0 = 100, $50,000+ = 0
    land_score = _min_max_scale(land_cost_per_acre, 0.0, 50000.0, invert=True)
    # Scale connection cost: $0 = 100, $200,000+ = 0
    connection_score = _min_max_scale(grid_connection_cost, 0.0, 200000.0, invert=True)
    return round((land_score * 0.50) + (connection_score * 0.50), 2)


# =====================================================================
# Task 3: Overall Site Suitability Score
# =====================================================================

def evaluate_site_suitability(
    site_data: dict,
    custom_weights: dict[str, float] | None = None
) -> SiteSuitabilityResult:
    """
    Combines category scores using configurable weights to compute the overall site score.

    Args:
        site_data (dict): Contains feature values (solar_irradiance, wind_speed, slope, etc.)
        custom_weights (dict, optional): Custom weight dictionary overriding default category weights.

    Returns:
        SiteSuitabilityResult: Typed dictionary containing category scores and overall score.
    """
    weights = DEFAULT_CATEGORY_WEIGHTS if custom_weights is None else custom_weights

    # Extract inputs with defaults
    solar = float(site_data.get("solar_irradiance", 0.0))
    wind = float(site_data.get("wind_speed", 0.0))
    slope = float(site_data.get("slope", 0.0))
    elevation = float(site_data.get("elevation", 0.0))
    road_dist = float(site_data.get("distance_to_road", 0.0))
    grid_dist = float(site_data.get("distance_to_grid", 0.0))
    prot_dist = float(site_data.get("protected_area_distance", 10.0))
    env_impact = float(site_data.get("environmental_impact_level", 0.0))
    land_cost = float(site_data.get("land_cost_per_acre", 10000.0))
    conn_cost = float(site_data.get("grid_connection_cost", 50000.0))

    # Calculate category scores
    res_score = calculate_resource_score(solar, wind)
    ter_score = calculate_terrain_score(slope, elevation)
    inf_score = calculate_infrastructure_score(road_dist, grid_dist)
    env_score = calculate_environmental_score(prot_dist, env_impact)
    eco_score = calculate_economic_score(land_cost, conn_cost)

    # Weighted overall aggregation
    w_res = weights.get("resource", 0.35)
    w_ter = weights.get("terrain", 0.25)
    w_inf = weights.get("infrastructure", 0.15)
    w_env = weights.get("environmental", 0.15)
    w_eco = weights.get("economic", 0.10)

    overall = (
        (res_score * w_res) +
        (ter_score * w_ter) +
        (inf_score * w_inf) +
        (env_score * w_env) +
        (eco_score * w_eco)
    )

    return SiteSuitabilityResult(
        resource_score=res_score,
        terrain_score=ter_score,
        infrastructure_score=inf_score,
        environmental_score=env_score,
        economic_score=eco_score,
        overall_score=round(overall, 2)
    )
