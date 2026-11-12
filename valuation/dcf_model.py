from dataclasses import dataclass
from typing import Dict

@dataclass
class DCFParameters:
    base_fcf: float
    growth_stage1: float
    growth_stage2: float
    terminal_growth: float
    wacc: float
    net_debt: float
    shares_outstanding: float
    stage1_years: int = 5
    stage2_years: int = 5

class DynamicDCFEngine:
    @staticmethod
    def calculate_enterprise_value(params: DCFParameters) -> float:
        pv_fcf = 0.0
        current_fcf = params.base_fcf

        for t in range(1, params.stage1_years + 1):
            current_fcf *= (1.0 + params.growth_stage1)
            pv_fcf += current_fcf / ((1.0 + params.wacc) ** t)

        for t in range(params.stage1_years + 1, params.stage1_years + params.stage2_years + 1):
            decay_step = t - params.stage1_years
            interpolated_growth = params.growth_stage1 - (
                (params.growth_stage1 - params.terminal_growth) * (decay_step / params.stage2_years)
            )
            current_fcf *= (1.0 + interpolated_growth)
            pv_fcf += current_fcf / ((1.0 + params.wacc) ** t)

        total_explicit_years = params.stage1_years + params.stage2_years
        terminal_fcf = current_fcf * (1.0 + params.terminal_growth)
        terminal_value = terminal_fcf / (params.wacc - params.terminal_growth)
        pv_terminal_value = terminal_value / ((1.0 + params.wacc) ** total_explicit_years)

        enterprise_value = pv_fcf + pv_terminal_value
        return float(enterprise_value)

    @classmethod
    def calculate_fair_value_per_share(cls, params: DCFParameters) -> float:
        ev = cls.calculate_enterprise_value(params)
        equity_value = ev - params.net_debt
        fair_value = equity_value / params.shares_outstanding
        return round(float(max(0.0, fair_value)), 2)

    @classmethod
    def run_scenario_triangulation(cls, base_params: DCFParameters) -> Dict[str, float]:
        bear_params = DCFParameters(
            base_fcf=base_params.base_fcf * 0.90,
            growth_stage1=base_params.growth_stage1 * 0.70,
            growth_stage2=base_params.growth_stage2 * 0.60,
            terminal_growth=min(0.045, base_params.terminal_growth - 0.01),
            wacc=base_params.wacc + 0.015,
            net_debt=base_params.net_debt,
            shares_outstanding=base_params.shares_outstanding,
            stage1_years=base_params.stage1_years,
            stage2_years=base_params.stage2_years
        )
        bull_params = DCFParameters(
            base_fcf=base_params.base_fcf * 1.10,
            growth_stage1=base_params.growth_stage1 * 1.25,
            growth_stage2=base_params.growth_stage2 * 1.15,
            terminal_growth=min(0.060, base_params.terminal_growth + 0.005),
            wacc=max(0.09, base_params.wacc - 0.01),
            net_debt=base_params.net_debt,
            shares_outstanding=base_params.shares_outstanding,
            stage1_years=base_params.stage1_years,
            stage2_years=base_params.stage2_years
        )

        return {
            "bear_fair_value": cls.calculate_fair_value_per_share(bear_params),
            "base_fair_value": cls.calculate_fair_value_per_share(base_params),
            "bull_fair_value": cls.calculate_fair_value_per_share(bull_params)
        }
