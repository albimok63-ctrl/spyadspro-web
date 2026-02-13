"""Trasformazione metriche in insight. Logica di business separata dallo scraping."""


class CreativeAnalyzer:
    """Trasforma metriche di engagement in punteggio e flag di pattern vincente."""

    def analyze(self, metrics: dict) -> dict:
        """
        Regole:
        - winning_pattern_flag = True se engagement_rate > 0.05, altrimenti False.
        - creative_score = min(100, engagement_rate * 1000).
        """
        engagement_rate = metrics.get("engagement_rate", 0.0) or 0.0

        winning_pattern_flag = engagement_rate > 0.05
        creative_score = min(100.0, engagement_rate * 1000)

        return {
            "creative_score": creative_score,
            "winning_pattern_flag": winning_pattern_flag,
        }
