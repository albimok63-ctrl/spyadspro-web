"""Calcolo parametri analytics da dati grezzi. Logica pura, nessun DB né FastAPI."""


class EngagementMetricsCalculator:
    """Calcola metriche di engagement a partire da likes, comments, shares, impressions."""

    def calculate(self, data: dict) -> dict:
        """
        Input: dict con likes, comments, shares, impressions (int).
        Output: engagement_rate, interaction_ratio (float).
        """
        likes = data.get("likes", 0) or 0
        comments = data.get("comments", 0) or 0
        shares = data.get("shares", 0) or 0
        impressions = data.get("impressions", 0) or 0

        if impressions == 0:
            engagement_rate = 0.0
        else:
            engagement_rate = (likes + comments + shares) / impressions

        interaction_ratio = comments / max(likes, 1)

        return {
            "engagement_rate": engagement_rate,
            "interaction_ratio": interaction_ratio,
        }
