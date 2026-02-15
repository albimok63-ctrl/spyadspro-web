"""Business logic per il calcolo delle metriche marketing (dati grezzi → intelligence)."""


class MetricsCalculator:
    """Calcola metriche di engagement e winning ad a partire da dati grezzi."""

    def calculate(self, data: dict) -> dict:
        """Legge likes, comments, shares, impressions, days_active e restituisce metriche.

        - engagement_rate = (likes + comments + shares) / impressions (0 se impressions <= 0)
        - interaction_ratio = comments / impressions (0 se impressions <= 0)
        - is_winning_ad = True se days_active >= 14, altrimenti False
        """
        likes = data.get("likes", 0) or 0
        comments = data.get("comments", 0) or 0
        shares = data.get("shares", 0) or 0
        impressions = data.get("impressions", 0) or 0
        days_active = data.get("days_active", 0) or 0

        if impressions > 0:
            engagement_rate = (likes + comments + shares) / impressions
            interaction_ratio = comments / impressions
        else:
            engagement_rate = 0.0
            interaction_ratio = 0.0

        is_winning_ad = days_active >= 14

        return {
            "engagement_rate": engagement_rate,
            "interaction_ratio": interaction_ratio,
            "is_winning_ad": is_winning_ad,
        }
