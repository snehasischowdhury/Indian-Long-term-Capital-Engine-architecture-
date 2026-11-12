import pytest
import numpy as np
import pandas as pd
from probability.bayesian_updater import BayesianThesisUpdater, EvidenceSignal
from probability.expected_value import ExpectedValueEngine, ScenarioDistribution
from factors.factor_engine import FactorEngine

def test_bayesian_thesis_update():
    prior = 0.50
    evidence = [
        EvidenceSignal("Q3_Beat", 2.2, "Revenue grew 25% YoY"),
        EvidenceSignal("New_Client_Win", 1.5, "Secured 5-year defense order"),
        EvidenceSignal("Margin_Expansion", 1.8, "EBITDA margin expanded 150 bps")
    ]
    post_prob, ci_low, ci_high = BayesianThesisUpdater.update_belief(prior, evidence)
    assert post_prob > prior
    assert post_prob >= 0.80
    assert ci_low < post_prob < ci_high

def test_negative_bayesian_evidence():
    prior = 0.70
    bad_evidence = [
        EvidenceSignal("CFO_Resignation", 0.2, "Sudden departure without succession"),
        EvidenceSignal("Margin_Collapse", 0.4, "Severe margin contraction")
    ]
    post_prob, _, _ = BayesianThesisUpdater.update_belief(prior, bad_evidence)
    assert post_prob < 0.30

def test_expected_value_distribution():
    scenarios = ScenarioDistribution(
        prob_extreme_down=0.05, return_extreme_down=-0.45,
        prob_bear=0.20, return_bear=-0.15,
        prob_base=0.50, return_base=0.18,
        prob_bull=0.20, return_bull=0.40,
        prob_extreme_up=0.05, return_extreme_up=0.85
    )
    res = ExpectedValueEngine.evaluate(scenarios)
    assert res["expected_return"] > 0.10
    assert res["probability_of_loss"] == 0.25
    assert res["probability_severe_loss"] == 0.05
    assert res["upside_downside_ratio"] > 1.0

def test_factor_engine_momentum_and_value():
    dates = pd.date_range(end="2026-10-01", periods=300)
    prices = [100.0 * (1.001 ** i) for i in range(300)]
    price_series = pd.Series(prices, index=dates)

    mom_score = FactorEngine.calculate_momentum_score(price_series)
    assert mom_score > 50.0

    val_score = FactorEngine.calculate_value_score(pe_ratio=14.0, pb_ratio=1.5, fcf_yield=0.065)
    assert val_score >= 70.0
