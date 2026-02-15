"""Logica di marketing intelligence separata dal calcolo delle metriche."""


class IntelligenceRules:
    """Valuta dati già arricchiti con metriche e applica regole business."""

    def evaluate(self, data: dict) -> dict:
        """Legge engagement_rate, interaction_ratio, activity_duration; aggiunge creative_score e winning_pattern_flag.

        Restituisce il dizionario in input con i nuovi campi aggiunti.
        """
        engagement_rate = data.get("engagement_rate", 0.0) or 0.0
        interaction_ratio = data.get("interaction_ratio", 0.0) or 0.0
        activity_duration = data.get("activity_duration", 0) or 0

        creative_score = (
            engagement_rate * 0.6
            + interaction_ratio * 0.3
            + min(activity_duration / 30, 1) * 0.1
        )
        winning_pattern_flag = engagement_rate > 0.05 and activity_duration > 7

        result = dict(data)
        result["creative_score"] = creative_score
        result["winning_pattern_flag"] = winning_pattern_flag
        return result
