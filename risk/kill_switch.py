from enum import Enum
from dataclasses import dataclass

class KillSwitchStage(str, Enum):
    STAGE_0 = "STAGE_0_NORMAL"
    STAGE_1 = "STAGE_1_RISK_REVIEW"
    STAGE_2 = "STAGE_2_FREEZE_SPECULATION"
    STAGE_3 = "STAGE_3_DERISK_BETA"
    STAGE_4 = "STAGE_4_STRUCTURAL_DEFENSE"
    STAGE_5 = "STAGE_5_EMERGENCY_PRESERVATION"

@dataclass
class MarketEnvironmentState:
    nifty_drawdown_pct: float
    india_vix: float
    credit_spread_widening_bps: float
    macro_shock_flag: bool

class PortfolioKillSwitchController:
    @staticmethod
    def evaluate_stage(env: MarketEnvironmentState) -> KillSwitchStage:
        if env.nifty_drawdown_pct >= 0.35 or (env.macro_shock_flag and env.india_vix > 35):
            return KillSwitchStage.STAGE_5
        if env.nifty_drawdown_pct >= 0.22 or env.india_vix >= 30:
            return KillSwitchStage.STAGE_4
        if env.nifty_drawdown_pct >= 0.15 or env.credit_spread_widening_bps > 150:
            return KillSwitchStage.STAGE_3
        if env.nifty_drawdown_pct >= 0.08 or env.india_vix > 20:
            return KillSwitchStage.STAGE_1
        return KillSwitchStage.STAGE_0

    @staticmethod
    def calculate_constrained_fractional_kelly(
        expected_excess_return: float,
        return_variance: float,
        base_fraction: float = 0.25,
        max_allowed_weight: float = 0.08,
        stage: KillSwitchStage = KillSwitchStage.STAGE_0
    ) -> float:
        if return_variance <= 0 or expected_excess_return <= 0:
            return 0.0

        full_kelly = expected_excess_return / return_variance
        allocated = full_kelly * base_fraction

        stage_multipliers = {
            KillSwitchStage.STAGE_0: 1.0,
            KillSwitchStage.STAGE_1: 0.8,
            KillSwitchStage.STAGE_2: 0.5,
            KillSwitchStage.STAGE_3: 0.2,
            KillSwitchStage.STAGE_4: 0.0,
            KillSwitchStage.STAGE_5: 0.0,
        }
        
        final_weight = allocated * stage_multipliers[stage]
        return round(float(min(final_weight, max_allowed_weight)), 4)
