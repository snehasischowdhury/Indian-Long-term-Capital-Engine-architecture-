import numpy as np
from scipy.optimize import minimize
from typing import List

class PortfolioOptimizer:
    @staticmethod
    def maximize_sharpe(expected_returns: np.ndarray, cov_matrix: np.ndarray, risk_free_rate: float = 0.07, bounds: List[tuple] = None) -> np.ndarray:
        n_assets = len(expected_returns)
        if bounds is None:
            bounds = [(0.0, 1.0) for _ in range(n_assets)]
            
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        init_guess = np.array([1.0 / n_assets] * n_assets)
        
        def negative_sharpe(w):
            port_return = np.sum(w * expected_returns)
            port_vol = np.sqrt(w.T @ cov_matrix @ w)
            if port_vol == 0:
                return 0.0
            return -(port_return - risk_free_rate) / port_vol
            
        result = minimize(negative_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        return np.round(result.x, 4)

    @staticmethod
    def minimum_variance(cov_matrix: np.ndarray, bounds: List[tuple] = None) -> np.ndarray:
        n_assets = len(cov_matrix)
        if bounds is None:
            bounds = [(0.0, 1.0) for _ in range(n_assets)]
            
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        init_guess = np.array([1.0 / n_assets] * n_assets)
        
        def port_variance(w):
            return w.T @ cov_matrix @ w
            
        result = minimize(port_variance, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        return np.round(result.x, 4)
