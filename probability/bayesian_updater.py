from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class EvidenceSignal:
    name: str
    likelihood_ratio: float
    description: str

class BayesianThesisUpdater:
    @staticmethod
    def probability_to_odds(probability: float) -> float:
        p = max(0.0001, min(0.9999, probability))
        return p / (1.0 - p)

    @staticmethod
    def odds_to_probability(odds: float) -> float:
        return odds / (1.0 + odds)

    @classmethod
    def update_belief(cls, prior_probability: float, evidence_list: List[EvidenceSignal]) -> Tuple[float, float, float]:
        prior_odds = cls.probability_to_odds(prior_probability)
        cumulative_lr = 1.0

        for evidence in evidence_list:
            lr = max(0.01, min(100.0, evidence.likelihood_ratio))
            cumulative_lr *= lr

        posterior_odds = prior_odds * cumulative_lr
        posterior_prob = cls.odds_to_probability(posterior_odds)

        uncertainty_spread = abs(posterior_prob - prior_probability) * (1.0 - min(0.9, len(evidence_list) * 0.15))
        ci_lower = max(0.01, posterior_prob - uncertainty_spread)
        ci_upper = min(0.99, posterior_prob + uncertainty_spread)

        return (
            round(float(posterior_prob), 4),
            round(float(ci_lower), 4),
            round(float(ci_upper), 4)
        )
