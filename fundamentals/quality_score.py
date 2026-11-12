from dataclasses import dataclass
from typing import Tuple

@dataclass
class FinancialInputs:
    roce: float
    roe: float
    net_debt: float
    ebitda: float
    interest_coverage: float
    current_ratio: float
    cfo: float
    pat: float
    fcf: float
    promoter_pledge_pct: float
    auditor_qualified: bool
    margin_stability_cv: float

class FundamentalEngine:
    def __init__(self, risk_free_rate: float = 0.07):
        self.rf = risk_free_rate

    def detect_permanent_impairment(self, data: FinancialInputs) -> Tuple[bool, str]:
        if data.promoter_pledge_pct > 50.0:
            return True, f"Excessive promoter pledge: {data.promoter_pledge_pct:.1f}% exceeds 50% threshold"
        if data.auditor_qualified:
            return True, "Auditor adverse qualification or disclaimer of opinion"
        if data.interest_coverage < 1.0 and data.net_debt > 0:
            return True, f"Insolvency threat: Interest coverage {data.interest_coverage:.2f} < 1.0"
        if data.cfo < 0 and data.pat > 0 and (data.cfo / data.pat) < -0.5:
            return True, "Severe cash flow divergence: Negative operating cash flow against positive PAT"
        return False, "No structural impairment detected"

    def compute_fqs(self, data: FinancialInputs) -> float:
        roce_spread = max(0.0, min(1.0, (data.roce - self.rf) / 0.15))
        roe_spread = max(0.0, min(1.0, (data.roe - self.rf) / 0.12))
        prof_score = 12.5 * roce_spread + 12.5 * roe_spread

        net_debt_ebitda = data.net_debt / data.ebitda if data.ebitda > 0 else 5.0
        solv_debt = 8.0 * max(0.0, min(1.0, 1.0 - (net_debt_ebitda / 3.0)))
        solv_int = 6.0 * min(1.0, max(0.0, data.interest_coverage / 6.0))
        solv_cr = 6.0 * min(1.0, max(0.0, data.current_ratio / 1.5))
        solv_score = solv_debt + solv_int + solv_cr

        cfo_pat_ratio = data.cfo / data.pat if data.pat > 0 else 0.0
        fcf_cfo_ratio = data.fcf / data.cfo if data.cfo > 0 else 0.0
        cash_score = 10.0 * min(1.0, max(0.0, cfo_pat_ratio)) + 10.0 * min(1.0, max(0.0, fcf_cfo_ratio))

        gov_base = 20.0
        gov_base -= min(20.0, (data.promoter_pledge_pct / 50.0) * 15.0)
        if data.auditor_qualified:
            gov_base -= 10.0
        gov_score = max(0.0, gov_base)

        moat_score = 15.0 * max(0.0, min(1.0, 1.0 - data.margin_stability_cv))

        total_fqs = prof_score + solv_score + cash_score + gov_score + moat_score
        return round(float(total_fqs), 2)
