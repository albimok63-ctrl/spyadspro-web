"""Business Rules Engine: trasforma le metriche in Marketing Intelligence."""


class BusinessRulesEngine:
    """Applica regole di business alle metriche e restituisce solo i campi di intelligence."""

    def apply(self, data: dict) -> dict:
        """Legge engagement_rate, days_active, interaction_ratio; applica regole; restituisce solo is_winning_ad, creative_score, winning_pattern_flag."""
        engagement_rate = data.get("engagement_rate", 0.0) or 0.0
        days_active = data.get("days_active", 0) or 0
        interaction_ratio = data.get("interaction_ratio", 0.0) or 0.0

        is_winning_ad = days_active >= 14

        raw_score = (engagement_rate * 0.6) + (interaction_ratio * 0.4)
        creative_score = max(0.0, min(1.0, raw_score))

        winning_pattern_flag = engagement_rate > 0.05

        return {
            "is_winning_ad": is_winning_ad,
            "creative_score": creative_score,
            "winning_pattern_flag": winning_pattern_flag,
        }
