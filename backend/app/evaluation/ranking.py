class SiteRanking:
    """
    Rank multiple candidate sites based on
    Overall Site Suitability Score.
    """

    def rank_sites(self, sites):

        ranked_sites = sorted(
            sites,
            key=lambda site: site["overall_site_score"],
            reverse=True
        )

        return ranked_sites

    def best_site(self, sites):

        ranked = self.rank_sites(sites)

        if ranked:
            return ranked[0]

        return None