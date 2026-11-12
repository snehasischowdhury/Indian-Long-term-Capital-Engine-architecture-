import pytest
import numpy as np
import pandas as pd
from regime.regime_detector import MarketRegimeDetector, MacroStateInputs
from risk.thermostat import RiskThermostatEngine, ThermostatInputs
from risk.covariance_engine import PortfolioCovarianceEngine

def test_regime_probabilities_sum_to_one():
    inputs = MacroStateInputs(
        gdp_growth_trend_pct=0.072,
        cpi_inflation_pct=0.048,
        rbi_repo_trend_bps=0.0,
        pmi_composite=56.5,
        earnings_revision_breadth=0.22,
        india_vix=13.5,
        credit_growth_spread=0.03
    )
    probs = MarketRegimeDetector.estimate_regime_probabilities(inputs)
    total_prob = sum(probs.values())
    assert abs(total_prob - 1.0) < 1e-3
    assert probs["Expansion"] > probs["Recession"]
    assert probs["Expansion"] > probs["Crisis"]

def test_crisis_regime_detection():
    crisis_inputs = MacroStateInputs(
        gdp_growth_trend_pct=0.02,
        cpi_inflation_pct=0.08,
        rbi_repo_trend_bps=125.0,
        pmi_composite=44.0,
        earnings_revision_breadth=-0.45,
        india_vix=38.0,
        credit_growth_spread=-0.08
    )
    probs = MarketRegimeDetector.estimate_regime_probabilities(crisis_inputs)
    assert probs["Crisis"] > probs["Expansion"]

def test_thermostat_scoring():
    calm_inputs = ThermostatInputs(
        nifty_pe_percentile=0.30,
        india_vix=12.5,
        breadth_pct_above_200d=75.0,
        gsec_10y_yield_velocity_bps=5.0,
        usdinr_30d_realized_vol=0.035,
        crude_oil_6m_momentum_pct=-0.10,
        fii_net_flow_trend_zscore=1.2,
        credit_spread_stress_index=0.15,
        drawdown_from_peak_pct=0.02,
        global_credit_spread_bps=320.0
    )
    res_calm = RiskThermostatEngine.calculate_thermostat_score(calm_inputs)
    assert res_calm["thermostat_score"] < 40.0
    assert res_calm["posture"] in ["GROWTH", "AGGRESSIVE_OPPORTUNITY"]

    stressed_inputs = ThermostatInputs(
        nifty_pe_percentile=0.95,
        india_vix=32.0,
        breadth_pct_above_200d=25.0,
        gsec_10y_yield_velocity_bps=80.0,
        usdinr_30d_realized_vol=0.09,
        crude_oil_6m_momentum_pct=0.35,
        fii_net_flow_trend_zscore=-2.2,
        credit_spread_stress_index=0.90,
        drawdown_from_peak_pct=0.18,
        global_credit_spread_bps=650.0
    )
    res_stress = RiskThermostatEngine.calculate_thermostat_score(stressed_inputs)
    assert res_stress["thermostat_score"] >= 60.0
    assert res_stress["posture"] in ["DEFENSIVE", "EXTREME_DEFENSIVE"]

def test_risk_decomposition():
    np.random.seed(42)
    ret_a = np.random.normal(0.001, 0.01, 100)
    ret_b = np.random.normal(0.0005, 0.02, 100)
    df = pd.DataFrame({"AssetA": ret_a, "AssetB": ret_b})

    cov = PortfolioCovarianceEngine.calculate_covariance_matrix(df)
    weights = np.array([0.5, 0.5])
    decomp = PortfolioCovarianceEngine.decompose_risk_contributions(weights, cov)

    assert decomp["portfolio_volatility"] > 0
    prc = decomp["percentage_risk_contributions"]
    assert abs(np.sum(prc) - 1.0) < 1e-4
    assert prc[1] > prc[0]
