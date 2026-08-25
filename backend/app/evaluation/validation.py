from app.evaluation.scorer import SiteScorer
from app.evaluation.ranking import SiteRanking


class ScoreValidation:
    """
    Validate the scoring engine
    using sample site data.
    """

    def __init__(self):
        self.scorer = SiteScorer()
        self.ranking = SiteRanking()

    def validate(self):

        sites = []

        site1 = self.scorer.calculate_overall_score(
            solar_irradiance=6.5,
            wind_speed=7.5,
            slope=2,
            elevation=40,
            grid_distance=1,
            road_distance=0.5,
        )

        site1["site_id"] = 1

        site2 = self.scorer.calculate_overall_score(
            solar_irradiance=4.2,
            wind_speed=3.5,
            slope=8,
            elevation=120,
            grid_distance=6,
            road_distance=4,
        )

        site2["site_id"] = 2

        site3 = self.scorer.calculate_overall_score(
            solar_irradiance=5.8,
            wind_speed=6.2,
            slope=3,
            elevation=60,
            grid_distance=2,
            road_distance=1,
        )

        site3["site_id"] = 3

        sites.append(site1)
        sites.append(site2)
        sites.append(site3)

        ranked_sites = self.ranking.rank_sites(sites)

        return {
            "sites": sites,
            "ranking": ranked_sites,
            "best_site": self.ranking.best_site(sites)
        }