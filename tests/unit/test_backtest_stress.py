import pytest
import numpy as np
import pandas as pd
from backtesting.engine import BacktestEngine
from stress_testing.stress_engine import StressTestEngine

def test_backtest_metrics():
    np.random.seed(42)
    daily_returns = pd.Series(np.random.normal(0.0006, 0.015, 1000))
    daily_returns.iloc[500] = -0.15 
    
    metrics = BacktestEngine.calculate_metrics(daily_returns, risk_free_rate=0.07)
    
    assert metrics["volatility"] > 0.0
    assert metrics["max_drawdown"] >= 0.15
    assert "cagr" in metrics
    assert "sharpe" in metrics
    assert "sortino" in metrics

def test_stress_synthetic_shock():
    weights = np.array([0.40, 0.40, 0.20])
    betas = np.array([1.0, 1.2, 0.0]) 
    
    shock = StressTestEngine.apply_synthetic_shock(weights, betas, -0.20)
    
    expected_shock = (0.40 * 1.0 * -0.20) + (0.40 * 1.2 * -0.20) + (0.20 * 0.0 * -0.20)
    assert np.isclose(shock, expected_shock, atol=1e-4)

def test_stress_comprehensive_report():
    weights = np.array([0.50, 0.50])
    betas = np.array([1.0, 0.5])
    
    report = StressTestEngine.comprehensive_stress_report(weights, betas)
    
    assert report["Nifty_Down_20_Pct"] == -0.15
    assert report["Nifty_Down_50_Pct"] == -0.375
