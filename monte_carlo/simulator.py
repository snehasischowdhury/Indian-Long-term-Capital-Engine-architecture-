import numpy as np
from typing import Dict, Any

class MonteCarloWealthSimulator:
    def __init__(self, initial_corpus: float, monthly_sip: float, annual_sip_step_up_pct: float, horizon_years: int, simulations: int = 10000):
        self.initial_corpus = initial_corpus
        self.monthly_sip = monthly_sip
        self.step_up = annual_sip_step_up_pct
        self.years = horizon_years
        self.sims = simulations

    def run_simulation(self, expected_annual_return: float, annual_volatility: float, degrees_of_freedom: int = 5) -> Dict[str, Any]:
        months = self.years * 12
        monthly_mu = (1.0 + expected_annual_return) ** (1/12) - 1.0
        monthly_sigma = annual_volatility / np.sqrt(12)
        
        t_samples = np.random.standard_t(df=degrees_of_freedom, size=(self.sims, months))
        variance_scaling = np.sqrt((degrees_of_freedom - 2) / degrees_of_freedom)
        monthly_returns = monthly_mu + (t_samples * variance_scaling * monthly_sigma)
        
        corpus_matrix = np.zeros((self.sims, months + 1))
        corpus_matrix[:, 0] = self.initial_corpus
        current_sip = self.monthly_sip
        
        for m in range(1, months + 1):
            if m > 1 and (m - 1) % 12 == 0:
                current_sip *= (1.0 + self.step_up)
            prev_corpus = corpus_matrix[:, m - 1]
            corpus_matrix[:, m] = prev_corpus * (1.0 + monthly_returns[:, m - 1]) + current_sip
            
        final_values = corpus_matrix[:, -1]
        
        milestones = [1e7, 5e7, 10e7, 25e7, 50e7]
        milestone_probs = {f"{int(m/1e7)}Cr": float(np.mean(final_values >= m)) for m in milestones}
        
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        percentile_values = {f"p{p}": float(np.percentile(final_values, p)) for p in percentiles}
        
        peak_matrix = np.maximum.accumulate(corpus_matrix, axis=1)
        drawdown_matrix = (peak_matrix - corpus_matrix) / peak_matrix
        max_drawdowns = np.max(drawdown_matrix, axis=1)
        
        return {
            "percentiles": percentile_values,
            "milestone_probabilities": milestone_probs,
            "probability_drawdown_gt_30pct": float(np.mean(max_drawdowns >= 0.30)),
            "probability_drawdown_gt_50pct": float(np.mean(max_drawdowns >= 0.50)),
            "median_final_corpus": percentile_values["p50"]
        }
