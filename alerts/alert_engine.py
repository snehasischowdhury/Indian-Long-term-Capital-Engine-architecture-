from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AlertConfig:
    max_portfolio_drawdown_pct: float = 0.10
    critical_vix_level: float = 25.0
    critical_yield_velocity: float = 50.0

class SystemAlertEngine:
    def __init__(self, config: AlertConfig = AlertConfig()):
        self.config = config

    def evaluate_system_state(
        self, 
        current_drawdown: float, 
        current_vix: float, 
        yield_velocity: float, 
        current_regime: str
    ) -> List[Dict[str, Any]]:
        
        active_alerts = []
        
        if current_drawdown >= self.config.max_portfolio_drawdown_pct:
            active_alerts.append({
                "level": "CRITICAL",
                "type": "DRAWDOWN_BREACH",
                "message": f"Portfolio drawdown at {current_drawdown*100:.1f}%. Exceeds {self.config.max_portfolio_drawdown_pct*100}% limit."
            })
            
        if current_vix >= self.config.critical_vix_level:
            active_alerts.append({
                "level": "WARNING",
                "type": "VOLATILITY_SPIKE",
                "message": f"India VIX at {current_vix}. Exceeds critical threshold of {self.config.critical_vix_level}."
            })
            
        if yield_velocity >= self.config.critical_yield_velocity:
            active_alerts.append({
                "level": "WARNING",
                "type": "YIELD_SHOCK",
                "message": f"10Y Yield velocity at {yield_velocity} bps. Bond market stress detected."
            })
            
        if current_regime in ["Crisis", "Recession"]:
            active_alerts.append({
                "level": "CRITICAL",
                "type": "REGIME_DETERIORATION",
                "message": f"Market regime shifted to {current_regime}. Initiate defensive protocols."
            })
            
        return active_alerts
