import pytest
from alerts.alert_engine import SystemAlertEngine, AlertConfig

def test_alert_engine_normal_state():
    engine = SystemAlertEngine()
    alerts = engine.evaluate_system_state(
        current_drawdown=0.05,
        current_vix=15.0,
        yield_velocity=10.0,
        current_regime="Expansion"
    )
    assert len(alerts) == 0

def test_alert_engine_critical_state():
    engine = SystemAlertEngine()
    alerts = engine.evaluate_system_state(
        current_drawdown=0.15,
        current_vix=28.0,
        yield_velocity=60.0,
        current_regime="Crisis"
    )
    assert len(alerts) == 4
    
    types = [a["type"] for a in alerts]
    assert "DRAWDOWN_BREACH" in types
    assert "VOLATILITY_SPIKE" in types
    assert "REGIME_DETERIORATION" in types
