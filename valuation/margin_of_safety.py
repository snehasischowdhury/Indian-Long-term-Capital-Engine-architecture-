from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ValuationAssessment:
    ticker: str
    current_price: float
    intrinsic_value: float
    margin_of_safety_pct: float
    valuation_band: str
    expected_upside_pct: float

class ValuationClassifier:
    @staticmethod
    def calculate_margin_of_safety(current_price: float, intrinsic_value: float) -> float:
        if intrinsic_value <= 0:
            return -1.0
        mos = (intrinsic_value - current_price) / intrinsic_value
        return round(float(mos), 4)

    @classmethod
    def classify(cls, ticker: str, current_price: float, intrinsic_value: float) -> ValuationAssessment:
        mos = cls.calculate_margin_of_safety(current_price, intrinsic_value)
        upside = ((intrinsic_value - current_price) / current_price) * 100.0 if current_price > 0 else 0.0

        if mos >= 0.35:
            band = "DEEPLY_UNDERVALUED"
        elif 0.15 <= mos < 0.35:
            band = "MODERATELY_UNDERVALUED"
        elif -0.10 <= mos < 0.15:
            band = "FAIRLY_VALUED"
        elif -0.30 <= mos < -0.10:
            band = "MODERATELY_OVERVALUED"
        else:
            band = "EXTREMELY_OVERVALUED"

        return ValuationAssessment(
            ticker=ticker,
            current_price=round(float(current_price), 2),
            intrinsic_value=round(float(intrinsic_value), 2),
            margin_of_safety_pct=round(float(mos * 100), 2),
            valuation_band=band,
            expected_upside_pct=round(float(upside), 2)
        )
