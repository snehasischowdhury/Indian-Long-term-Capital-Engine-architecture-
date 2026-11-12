import numpy as np
import pandas as pd
from typing import Dict, Any

class FactorEngine:
    @staticmethod
    def calculate_momentum_score(price_series: pd.Series) -> float:
        if len(price_series) < 252:
            return 50.0

        p_current = price_series.iloc[-1]
        p_1m = price_series.iloc[-21]
        p_12m = price_series.iloc[-252]

        mom_12m = (p_current / p_12m) - 1.0
        mom_1m = (p_current / p_1m) - 1.0
        reversal_adj_momentum = mom_12m - mom_1m

        returns = price_series.pct_change().dropna()
        vol_ann = float(returns.tail(252).std() * np.sqrt(252))

        vol_adj_momentum = reversal_adj_momentum / vol_ann if vol_ann > 0 else 0.0
        standardized = 50.0 + (vol_adj_momentum * 25.0)
        return float(np.clip(standardized, 0.0, 100.0))

    @staticmethod
    def calculate_value_score(pe_ratio: float, pb_ratio: float, fcf_yield: float) -> float:
        pe_points = 35.0 * max(0.0, min(1.0, (40.0 - pe_ratio) / 30.0)) if pe_ratio > 0 else 0.0
        pb_points = 25.0 * max(0.0, min(1.0, (6.0 - pb_ratio) / 5.0)) if pb_ratio > 0 else 0.0
        fcf_points = 40.0 * max(0.0, min(1.0, fcf_yield / 0.07))
        return float(np.clip(pe_points + pb_points + fcf_points, 0.0, 100.0))

    @staticmethod
    def calculate_low_vol_score(realized_volatility_annualized: float) -> float:
        score = 100.0 - ((realized_volatility_annualized - 0.10) / 0.35) * 100.0
        return float(np.clip(score, 0.0, 100.0))

    @classmethod
    def composite_factor_profile(
        cls,
        fqs_score: float,
        pe_ratio: float,
        pb_ratio: float,
        fcf_yield: float,
        price_series: pd.Series
    ) -> Dict[str, float]:
        returns = price_series.pct_change().dropna()
        vol = float(returns.tail(252).std() * np.sqrt(252)) if len(returns) >= 20 else 0.20

        val_score = cls.calculate_value_score(pe_ratio, pb_ratio, fcf_yield)
        mom_score = cls.calculate_momentum_score(price_series)
        vol_score = cls.calculate_low_vol_score(vol)

        composite = (0.35 * fqs_score) + (0.25 * val_score) + (0.25 * mom_score) + (0.15 * vol_score)

        return {
            "quality_factor": round(fqs_score, 2),
            "value_factor": round(val_score, 2),
            "momentum_factor": round(mom_score, 2),
            "low_volatility_factor": round(vol_score, 2),
            "composite_score": round(float(composite), 2)
        }
