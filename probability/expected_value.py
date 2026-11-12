from dataclasses import dataclass
from typing import Dict, Any
import numpy as np

@dataclass
class ScenarioDistribution:
    prob_extreme_down: float
    return_extreme_down: float
    prob_bear: float
    return_bear: float
    prob_base: float
    return_base: float
    prob_bull: float
    return_bull: float
    prob_extreme_up: float
    return_extreme_up: float

class ExpectedValueEngine:
    @staticmethod
    def evaluate(scenarios: ScenarioDistribution) -> Dict[str, Any]:
        probs = np.array([
            scenarios.prob_extreme_down,
            scenarios.prob_bear,
            scenarios.prob_base,
            scenarios.prob_bull,
            scenarios.prob_extreme_up
        ])
        returns = np.array([
            scenarios.return_extreme_down,
            scenarios.return_bear,
            scenarios.return_base,
            scenarios.return_bull,
            scenarios.return_extreme_up
        ])

        norm_probs = probs / np.sum(probs)
        expected_return = float(np.sum(norm_probs * returns))

        downside_mask = returns < 0
        upside_mask = returns > 0

        downside_risk = float(np.sum(norm_probs[downside_mask] * np.abs(returns[downside_mask])))
        upside_potential = float(np.sum(norm_probs[upside_mask] * returns[upside_mask]))

        skew_ratio = (upside_potential / downside_risk) if downside_risk > 0 else 99.0
        prob_loss = float(np.sum(norm_probs[downside_mask]))
        prob_severe_loss = float(norm_probs[0])

        return {
            "expected_return": round(expected_return, 4),
            "probability_of_loss": round(prob_loss, 4),
            "probability_severe_loss": round(prob_severe_loss, 4),
            "downside_risk_weighted": round(downside_risk, 4),
            "upside_potential_weighted": round(upside_potential, 4),
            "upside_downside_ratio": round(skew_ratio, 2)
        }
