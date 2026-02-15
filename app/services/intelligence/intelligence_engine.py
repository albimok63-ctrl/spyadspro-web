"""IntelligenceEngine: trasforma metriche e business rules in marketing intelligence completa."""

# Benchmark base (hardcoded per ora)
BENCHMARK_ENGAGEMENT_RATE = 0.04

direct_response_keywords = [
    "buy", "shop", "order", "discount",
    "limited", "offer", "sale", "today",
    "now", "free shipping",
]
branding_keywords = [
    "story", "mission", "community",
    "brand", "values", "experience",
    "vision", "lifestyle",
]


class IntelligenceEngine:
    """Valuta i dati già arricchiti con metriche e regole e produce intelligence completa."""

    def __init__(self) -> None:
        self.default_benchmark = 0.04

    def evaluate(self, data: dict) -> dict:
        """Legge engagement_rate, creative_score, days_active; applica benchmark e pattern; restituisce intelligence."""
        engagement_rate = data.get("engagement_rate", 0.0) or 0.0
        creative_score = data.get("creative_score", 0.0) or 0.0
        days_active = data.get("days_active", 0) or 0
        ad_copy_raw = data.get("ad_copy") or ""

        creative_type = "unknown"
        if ad_copy_raw:
            ad_copy = ad_copy_raw.lower()
            direct_response_count = sum(ad_copy.count(w) for w in direct_response_keywords)
            branding_count = sum(ad_copy.count(w) for w in branding_keywords)
            if direct_response_count > branding_count:
                creative_type = "direct_response"
            elif branding_count > direct_response_count:
                creative_type = "branding"
            else:
                creative_type = "mixed"

        benchmark = data.get("platform_average_engagement")
        if benchmark is None:
            benchmark = self.default_benchmark
        if engagement_rate >= benchmark:
            benchmark_score = 1.0
        elif engagement_rate >= benchmark * 0.5:
            benchmark_score = 0.5
        else:
            benchmark_score = 0.1

        intelligence_score = (creative_score + benchmark_score) / 2

        high_engagement_pattern = engagement_rate >= benchmark
        long_running_pattern = days_active >= 14

        return {
            "benchmark_score": benchmark_score,
            "intelligence_score": intelligence_score,
            "high_engagement_pattern": high_engagement_pattern,
            "long_running_pattern": long_running_pattern,
            "creative_type": creative_type,
        }
