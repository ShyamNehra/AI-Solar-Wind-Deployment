from app.services.scoring_engine import evaluate_site_suitability, SiteSuitabilityResult


def rank_candidate_sites(
    candidate_sites: list[dict],
    custom_weights: dict[str, float] | None = None
) -> list[dict]:
    """
    Evaluates and ranks multiple candidate sites by overall_score descending (highest score first).

    Args:
        candidate_sites (list[dict]): List of candidate site dictionaries.
            Each dictionary can either contain raw features (e.g. solar_irradiance, wind_speed, etc.)
            or an already computed 'evaluation' result.
        custom_weights (dict, optional): Custom weight overrides for category scoring.

    Returns:
        list[dict]: Sorted candidate sites ranked from highest to lowest suitability score.
            Each element contains 'rank', 'site_name'/'site_id' (if provided), input details, and evaluation scores.
    """
    ranked_results: list[dict] = []

    for index, site in enumerate(candidate_sites):
        # Determine if site already has evaluation or needs evaluation
        if "overall_score" in site:
            eval_result = site
            site_info = site.get("site_info", site)
        elif "evaluation" in site and "overall_score" in site["evaluation"]:
            eval_result = site["evaluation"]
            site_info = site
        else:
            eval_result = evaluate_site_suitability(site, custom_weights)
            site_info = site

        ranked_results.append({
            "site_info": site_info,
            "evaluation": eval_result,
            "overall_score": eval_result["overall_score"]
        })

    # Sort descending by overall_score
    ranked_results.sort(key=lambda x: x["overall_score"], reverse=True)

    # Assign 1-indexed rank
    for rank_idx, item in enumerate(ranked_results, start=1):
        item["rank"] = rank_idx

    return ranked_results
