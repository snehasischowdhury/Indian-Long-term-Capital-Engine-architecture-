import numpy as np
import pandas as pd
from typing import Dict, Any

class PortfolioCovarianceEngine:
    @staticmethod
    def calculate_covariance_matrix(returns_df: pd.DataFrame, annualize_factor: int = 252) -> np.ndarray:
        clean_df = returns_df.dropna()
        if clean_df.empty:
            raise ValueError("Returns dataframe is empty.")
        cov = clean_df.cov().values * annualize_factor
        return cov

    @staticmethod
    def decompose_risk_contributions(weights: np.ndarray, cov_matrix: np.ndarray) -> Dict[str, np.ndarray]:
        w = np.array(weights).flatten()
        port_var = float(w.T @ cov_matrix @ w)

        if port_var <= 0.0:
            n = len(w)
            return {
                "portfolio_volatility": 0.0,
                "marginal_risk_contributions": np.zeros(n),
                "percentage_risk_contributions": np.zeros(n)
            }

        port_vol = np.sqrt(port_var)
        marginal_contrib = (cov_matrix @ w) / port_vol
        component_contrib = w * marginal_contrib
        pct_contrib = component_contrib / port_vol

        return {
            "portfolio_volatility": float(port_vol),
            "marginal_risk_contributions": marginal_contrib,
            "percentage_risk_contributions": pct_contrib
        }

    @staticmethod
    def calculate_diversification_ratio(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        w = np.array(weights).flatten()
        individual_vols = np.sqrt(np.diag(cov_matrix))
        weighted_vol = float(np.sum(w * individual_vols))
        port_var = float(w.T @ cov_matrix @ w)
        port_vol = np.sqrt(port_var)

        if port_vol <= 0.0:
            return 1.0
        return round(weighted_vol / port_vol, 4)
