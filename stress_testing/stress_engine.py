import numpy as np
from typing import Dict

class StressTestEngine:
    @staticmethod
    def apply_synthetic_shock(portfolio_weights: np.ndarray, asset_betas: np.ndarray, market_shock_pct: float) -> float:
        w = np.array(portfolio_weights).flatten()
        betas = np.array(asset_betas).flatten()
        
        asset_shocks = betas * market_shock_pct
        portfolio_shock = np.sum(w * asset_shocks)
        return round(float(portfolio_shock), 4)

    @staticmethod
    def evaluate_historical_scenario(portfolio_weights: np.ndarray, asset_historical_drawdowns: np.ndarray) -> float:
        w = np.array(portfolio_weights).flatten()
        drawdowns = np.array(asset_historical_drawdowns).flatten()
        
        portfolio_impact = np.sum(w * drawdowns)
        return round(float(portfolio_impact), 4)

    @staticmethod
    def comprehensive_stress_report(portfolio_weights: np.ndarray, asset_betas: np.ndarray) -> Dict[str, float]:
        return {
            "Nifty_Down_20_Pct": StressTestEngine.apply_synthetic_shock(portfolio_weights, asset_betas, -0.20),
            "Nifty_Down_35_Pct": StressTestEngine.apply_synthetic_shock(portfolio_weights, asset_betas, -0.35),
            "Nifty_Down_50_Pct": StressTestEngine.apply_synthetic_shock(portfolio_weights, asset_betas, -0.50)
        }
