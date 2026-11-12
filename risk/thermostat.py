from dataclasses import dataclass
from typing import Dict, Any
import numpy as np

@dataclass
class ThermostatInputs:
    nifty_pe_percentile: float
    india_vix: float
    breadth_pct_above_200d: float
    gsec_10y_yield_velocity_bps: float
    usdinr_30d_realized_vol: float
    crude_oil_6m_momentum_pct: float
    fii_net_flow_trend_zscore: float
    credit_spread_stress_index: float
    drawdown_from_peak_pct: float
    global_credit_spread_bps: float

class RiskThermostatEngine:
    @staticmethod
    def calculate_thermostat_score(data: ThermostatInputs) -> Dict[str, Any]:
        val_hazard = data.nifty_pe_percentile * 15.0

        vix_hazard = min(15.0, max(0.0, ((data.india_vix - 11.0) / 24.0) * 15.0))

        breadth_hazard = (1.0 - (data.breadth_pct_above_200d / 100.0)) * 10.0

        yield_hazard = min(10.0, max(0.0, (data.gsec_10y_yield_velocity_bps / 100.0) * 10.0))

        fx_hazard = min(10.0, max(0.0, ((data.usdinr_30d_realized_vol - 0.03) / 0.07) * 10.0))

        crude_hazard = min(10.0, max(0.0, (data.crude_oil_6m_momentum_pct / 0.40) * 10.0))

        fii_hazard = min(10.0, max(0.0, (-data.fii_net_flow_trend_zscore / 2.5) * 10.0))

        credit_hazard = min(10.0, max(0.0, data.credit_spread_stress_index * 10.0))

        dd_hazard = min(5.0, max(0.0, (data.drawdown_from_peak_pct / 0.25) * 5.0))

        cds_hazard = min(5.0, max(0.0, ((data.global_credit_spread_bps - 300.0) / 400.0) * 5.0))

        aggregate_risk_score = (
            val_hazard + vix_hazard + breadth_hazard + yield_hazard +
            fx_hazard + crude_hazard + fii_hazard + credit_hazard +
            dd_hazard + cds_hazard
        )
        aggregate_risk_score = float(np.clip(aggregate_risk_score, 0.0, 100.0))

        if aggregate_risk_score >= 80.0:
            regime_label = "EXTREME_DEFENSIVE"
        elif aggregate_risk_score >= 60.0:
            regime_label = "DEFENSIVE"
        elif aggregate_risk_score >= 40.0:
            regime_label = "NEUTRAL"
        elif aggregate_risk_score >= 20.0:
            regime_label = "GROWTH"
        else:
            regime_label = "AGGRESSIVE_OPPORTUNITY"

        return {
            "thermostat_score": round(aggregate_risk_score, 2),
            "posture": regime_label,
            "components": {
                "valuation_hazard": round(val_hazard, 2),
                "volatility_hazard": round(vix_hazard, 2),
                "breadth_hazard": round(breadth_hazard, 2),
                "credit_hazard": round(credit_hazard, 2),
                "macro_fii_hazard": round(fii_hazard + fx_hazard + crude_hazard, 2)
            }
        }
