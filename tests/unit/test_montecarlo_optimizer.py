import pytest
import numpy as np
from monte_carlo.simulator import MonteCarloWealthSimulator
from optimization.optimizer import PortfolioOptimizer

def test_monte_carlo_simulator():
    np.random.seed(42)
    sim = MonteCarloWealthSimulator(
        initial_corpus=1000000.0,
        monthly_sip=50000.0,
        annual_sip_step_up_pct=0.10,
        horizon_years=15,
        simulations=1000
    )
    res = sim.run_simulation(expected_annual_return=0.12, annual_volatility=0.16)
    
    assert res["median_final_corpus"] > 1000000.0
    assert 0.0 <= res["probability_drawdown_gt_30pct"] <= 1.0
    assert "1Cr" in res["milestone_probabilities"]
    assert res["percentiles"]["p95"] > res["percentiles"]["p50"]

def test_portfolio_optimizer_sharpe():
    exp_returns = np.array([0.14, 0.10, 0.08])
    cov_matrix = np.array([
        [0.040, 0.010, 0.005],
        [0.010, 0.030, 0.004],
        [0.005, 0.004, 0.020]
    ])
    bounds = [(0.0, 0.50), (0.0, 0.50), (0.0, 0.50)]
    
    w_sharpe = PortfolioOptimizer.maximize_sharpe(exp_returns, cov_matrix, risk_free_rate=0.07, bounds=bounds)
    
    assert np.isclose(np.sum(w_sharpe), 1.0, atol=1e-3)
    assert all(w <= 0.501 for w in w_sharpe)
    assert all(w >= -0.001 for w in w_sharpe)

def test_portfolio_optimizer_minvar():
    cov_matrix = np.array([
        [0.050, 0.000, 0.000],
        [0.000, 0.020, 0.000],
        [0.000, 0.000, 0.010]
    ])
    bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
    
    w_minvar = PortfolioOptimizer.minimum_variance(cov_matrix, bounds)
    
    assert np.isclose(np.sum(w_minvar), 1.0, atol=1e-3)
    assert w_minvar[2] > w_minvar[1] > w_minvar[0]
