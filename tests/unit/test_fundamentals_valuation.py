import pytest
from fundamentals.quality_score import FundamentalEngine, FinancialInputs
from valuation.dcf_model import DynamicDCFEngine, DCFParameters
from valuation.margin_of_safety import ValuationClassifier

def test_high_quality_fqs():
    engine = FundamentalEngine(risk_free_rate=0.07)
    healthy_inputs = FinancialInputs(
        roce=0.24,
        roe=0.20,
        net_debt=-1000.0,
        ebitda=2500.0,
        interest_coverage=35.0,
        current_ratio=2.2,
        cfo=2100.0,
        pat=1800.0,
        fcf=1700.0,
        promoter_pledge_pct=0.0,
        auditor_qualified=False,
        margin_stability_cv=0.06
    )
    score = engine.compute_fqs(healthy_inputs)
    assert 85.0 <= score <= 100.0
    impaired, _ = engine.detect_permanent_impairment(healthy_inputs)
    assert impaired is False

def test_permanent_impairment_pledge():
    engine = FundamentalEngine(risk_free_rate=0.07)
    compromised_inputs = FinancialInputs(
        roce=0.10, roe=0.08, net_debt=1500.0, ebitda=300.0,
        interest_coverage=1.8, current_ratio=1.1, cfo=100.0,
        pat=80.0, fcf=-50.0, promoter_pledge_pct=62.5,
        auditor_qualified=False, margin_stability_cv=0.25
    )
    impaired, reason = engine.detect_permanent_impairment(compromised_inputs)
    assert impaired is True
    assert "pledge" in reason.lower()

def test_dcf_scenario_triangulation():
    params = DCFParameters(
        base_fcf=100.0,
        growth_stage1=0.15,
        growth_stage2=0.08,
        terminal_growth=0.05,
        wacc=0.11,
        net_debt=50.0,
        shares_outstanding=10.0
    )
    results = DynamicDCFEngine.run_scenario_triangulation(params)
    assert results["bear_fair_value"] < results["base_fair_value"]
    assert results["base_fair_value"] < results["bull_fair_value"]

def test_valuation_classification():
    assessment = ValuationClassifier.classify("TEST_TICKER", current_price=700.0, intrinsic_value=1000.0)
    assert assessment.valuation_band == "MODERATELY_UNDERVALUED"
    assert assessment.margin_of_safety_pct == 30.0

    deep_value = ValuationClassifier.classify("TEST_TICKER", current_price=500.0, intrinsic_value=1000.0)
    assert deep_value.valuation_band == "DEEPLY_UNDERVALUED"
    assert deep_value.margin_of_safety_pct == 50.0
