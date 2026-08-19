from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Data Schemas
# ---------------------------------------------------------------------------

class SiteMetrics(BaseModel):
    site_id: str
    solar_irradiance: float  # kWh/m2/day
    wind_speed: float        # m/s
    slope: float             # degrees
    elevation: float         # meters
    distance_to_grid: float  # km
    distance_to_road: float  # km
    env_sensitivity: float   # 0 to 1 index (1 = highly sensitive/protected)
    land_cost_per_sqm: float # USD or local currency


class CategoryScores(BaseModel):
    resource_score: float
    terrain_score: float
    infrastructure_score: float
    environmental_score: float
    economic_score: float


class SiteEvaluationResult(BaseModel):
    site_id: str
    category_scores: CategoryScores
    overall_score: float


# ---------------------------------------------------------------------------
# Task 1: Score Normalization Utilities (0 - 100 Scale)
# ---------------------------------------------------------------------------

def normalize_linear(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
    """
    Normalizes a value to a 0-100 scale.
    If invert=True, lower original values yield HIGHER scores (e.g., distance to grid).
    """
    if max_val == min_val:
        return 100.0 if not invert else 0.0
    
    clamped = max(min_val, min(value, max_val))
    score = ((clamped - min_val) / (max_val - min_val)) * 100.0
    
    if invert:
        score = 100.0 - score
        
    return round(score, 2)


def normalize_solar(irradiance: float) -> float:
    # Typical range: 2.0 kWh/m2/day (poor) to 7.0 kWh/m2/day (excellent)
    return normalize_linear(irradiance, min_val=2.0, max_val=7.0)


def normalize_wind(speed: float) -> float:
    # Typical range: 3.0 m/s (cutoff) to 12.0 m/s (rated power target)
    return normalize_linear(speed, min_val=3.0, max_val=12.0)


def normalize_slope(slope: float) -> float:
    # Inverted: 0 deg (perfect) to 15 deg (steep / unbuildable)
    return normalize_linear(slope, min_val=0.0, max_val=15.0, invert=True)


def normalize_distance(distance_km: float, max_acceptable_km: float = 50.0) -> float:
    # Inverted: 0 km (next door) to max_acceptable_km (too far)
    return normalize_linear(distance_km, min_val=0.0, max_val=max_acceptable_km, invert=True)


# ---------------------------------------------------------------------------
# Task 2: Category-Wise Scoring Engine
# ---------------------------------------------------------------------------

class SiteScorer:
    def __init__(self, category_weights: Optional[Dict[str, float]] = None):
        """
        Module 10 Scoring Model Weights (must sum to 1.0):
        - Resource Availability: 35%
        - Geographic Suitability: 25%
        - Infrastructure Accessibility: 15%
        - Environmental Impact: 15%
        - Economic Feasibility: 10%
        """
        self.weights = category_weights or {
            "resource": 0.35,
            "terrain": 0.25,
            "infrastructure": 0.15,
            "environmental": 0.15,
            "economic": 0.10
        }

    def compute_category_scores(self, site: SiteMetrics) -> CategoryScores:
        # Resource Score (50% Solar, 50% Wind)
        res_score = (0.5 * normalize_solar(site.solar_irradiance)) + \
                    (0.5 * normalize_wind(site.wind_speed))

        # Terrain Score (70% Slope, 30% Elevation normalization)
        slope_score = normalize_slope(site.slope)
        elev_score = normalize_linear(site.elevation, min_val=0.0, max_val=3000.0, invert=True)
        terr_score = (0.7 * slope_score) + (0.3 * elev_score)

        # Infrastructure Score (60% Grid distance, 40% Road distance)
        grid_score = normalize_distance(site.distance_to_grid, max_acceptable_km=50.0)
        road_score = normalize_distance(site.distance_to_road, max_acceptable_km=30.0)
        infra_score = (0.6 * grid_score) + (0.4 * road_score)

        # Environmental Score (Higher sensitivity index yields lower score)
        env_score = normalize_linear(site.env_sensitivity, min_val=0.0, max_val=1.0, invert=True)

        # Economic Score (Lower land cost per sq.m yields higher score)
        econ_score = normalize_linear(site.land_cost_per_sqm, min_val=10.0, max_val=200.0, invert=True)

        return CategoryScores(
            resource_score=round(res_score, 2),
            terrain_score=round(terr_score, 2),
            infrastructure_score=round(infra_score, 2),
            environmental_score=round(env_score, 2),
            economic_score=round(econ_score, 2)
        )

    # ---------------------------------------------------------------------------
    # Task 3: Calculate Overall Site Score
    # ---------------------------------------------------------------------------
    def evaluate_site(self, site: SiteMetrics) -> SiteEvaluationResult:
        cats = self.compute_category_scores(site)
        
        overall = (
            cats.resource_score * self.weights["resource"] +
            cats.terrain_score * self.weights["terrain"] +
            cats.infrastructure_score * self.weights["infrastructure"] +
            cats.environmental_score * self.weights["environmental"] +
            cats.economic_score * self.weights["economic"]
        )

        return SiteEvaluationResult(
            site_id=site.site_id,
            category_scores=cats,
            overall_score=round(overall, 2)
        )

    # ---------------------------------------------------------------------------
    # Task 4: Rank Multiple Candidate Sites
    # ---------------------------------------------------------------------------
    def rank_sites(self, sites: List[SiteMetrics]) -> List[SiteEvaluationResult]:
        results = [self.evaluate_site(s) for s in sites]
        # Sort descending by overall_score
        return sorted(results, key=lambda x: x.overall_score, reverse=True)


# ---------------------------------------------------------------------------
# Task 5: Validation Suite
# ---------------------------------------------------------------------------

def run_validation_tests():
    print("--- Running Scoring Engine Validation Tests ---")
    scorer = SiteScorer()

    # Base test site
    base_site = SiteMetrics(
        site_id="Base_Site",
        solar_irradiance=5.5,
        wind_speed=7.5,
        slope=3.0,
        elevation=200.0,
        distance_to_grid=5.0,
        distance_to_road=2.0,
        env_sensitivity=0.1,
        land_cost_per_sqm=30.0
    )

    # Test 1: High Resource vs Low Resource
    low_res_site = base_site.model_copy(update={"site_id": "Low_Resource", "solar_irradiance": 2.5, "wind_speed": 3.5})
    high_res_res = scorer.evaluate_site(base_site)
    low_res_res = scorer.evaluate_site(low_res_site)
    
    assert high_res_res.overall_score > low_res_res.overall_score, "Failed: High resource should yield a higher score!"
    print(" ✓ Check 1 Passed: Higher resource availability increases overall score.")

    # Test 2: Poor Infrastructure / High Slope Penalization
    bad_infra_site = base_site.model_copy(update={"site_id": "Bad_Infra", "distance_to_grid": 45.0, "slope": 14.0})
    bad_infra_res = scorer.evaluate_site(bad_infra_site)

    base_site_score = scorer.evaluate_site(base_site).overall_score
    assert base_site_score > bad_infra_res.overall_score, "Failed: Poor infra/terrain should reduce score!"
    print(" ✓ Check 2 Passed: Poor infrastructure/terrain appropriately penalizes score.")

    # Test 3: Ranking Order Check
    ranked = scorer.rank_sites([low_res_site, base_site, bad_infra_site])
    assert ranked[0].site_id == "Base_Site", "Failed: Base site should be ranked #1!"
    assert ranked[-1].site_id in ["Low_Resource", "Bad_Infra"], "Failed: Worst site should be ranked last!"
    print(f" ✓ Check 3 Passed: Dynamic ranking order correct -> Top candidate: {ranked[0].site_id}")

    # Test 4: Determinism / Consistency
    res_a = scorer.evaluate_site(base_site)
    res_b = scorer.evaluate_site(base_site)
    assert res_a.overall_score == res_b.overall_score, "Failed: Engine is non-deterministic!"
    print(" ✓ Check 4 Passed: Scoring logic produces consistent repeated results.")

    print("\nAll validation checks passed successfully!")


if __name__ == "__main__":
    run_validation_tests()