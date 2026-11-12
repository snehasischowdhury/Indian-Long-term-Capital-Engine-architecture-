from dataclasses import dataclass
from typing import Dict
import numpy as np

@dataclass
class MacroStateInputs:
    gdp_growth_trend_pct: float
    cpi_inflation_pct: float
    rbi_repo_trend_bps: float
    pmi_composite: float
    earnings_revision_breadth: float
    india_vix: float
    credit_growth_spread: float

class MarketRegimeDetector:
    @staticmethod
    def estimate_regime_probabilities(inputs: MacroStateInputs) -> Dict[str, float]:
        score_expansion = 0.0
        score_late_cycle = 0.0
        score_recession = 0.0
        score_crisis = 0.0
        score_recovery = 0.0

        if inputs.pmi_composite > 54.0 and inputs.gdp_growth_trend_pct > 0.06:
            if inputs.cpi_inflation_pct < 0.055:
                score_expansion += 4.0
            else:
                score_late_cycle += 3.5

        if inputs.rbi_repo_trend_bps > 50.0 or inputs.cpi_inflation_pct > 0.065:
            score_late_cycle += 3.0

        if inputs.pmi_composite < 48.0 or inputs.gdp_growth_trend_pct < 0.04:
            score_recession += 3.5

        if inputs.earnings_revision_breadth < -0.30:
            score_recession += 2.5

        if inputs.india_vix > 28.0 or inputs.credit_growth_spread < -0.05:
            score_crisis += 4.5

        if inputs.india_vix > 35.0:
            score_crisis += 3.0

        if inputs.pmi_composite > 50.0 and inputs.earnings_revision_breadth > 0.10:
            if inputs.rbi_repo_trend_bps <= 0.0:
                score_recovery += 4.0

        scores = np.array([
            max(0.1, score_expansion),
            max(0.1, score_late_cycle),
            max(0.1, score_recession),
            max(0.05, score_crisis),
            max(0.1, score_recovery)
        ])

        exp_scores = np.exp(scores - np.max(scores))
        probabilities = exp_scores / np.sum(exp_scores)

        return {
            "Expansion": round(float(probabilities[0]), 4),
            "Late Cycle": round(float(probabilities[1]), 4),
            "Recession": round(float(probabilities[2]), 4),
            "Crisis": round(float(probabilities[3]), 4),
            "Recovery": round(float(probabilities[4]), 4)
        }
