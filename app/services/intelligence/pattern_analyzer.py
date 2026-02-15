"""Identificazione di pattern comuni tra annunci."""


class PatternAnalyzer:
    """Analizza una lista di annunci e restituisce metriche aggregate sui pattern."""

    def analyze(self, ads: list[dict]) -> dict:
        """Conta gli annunci con high_engagement_pattern True; calcola winning_ratio = winning_ads / total_ads."""
        total_ads = len(ads)
        winning_ads = sum(1 for ad in ads if ad.get("high_engagement_pattern") is True)
        winning_ratio = winning_ads / total_ads if total_ads > 0 else 0.0
        return {"winning_ratio": winning_ratio}
