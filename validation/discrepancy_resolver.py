import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class DiscrepancyResolver:
    @staticmethod
    def calculate_discrepancy(val_a: float, val_b: float) -> float:
        avg = 0.5 * (abs(val_a) + abs(val_b))
        return 0.0 if avg == 0 else abs(val_a - val_b) / avg

    @staticmethod
    def resolve_conflict(val_a: float, tier_a: str, drs_a: float,
                         val_b: float, tier_b: str, drs_b: float) -> dict:
        discrepancy = DiscrepancyResolver.calculate_discrepancy(val_a, val_b)
        
        result = {
            "discrepancy_pct": discrepancy * 100,
            "status": "VALID",
            "preferred_value": None,
            "confidence": "HIGH"
        }

        if discrepancy <= settings.DATA_QUARANTINE_THRESHOLD:
            result["preferred_value"] = val_a if drs_a >= drs_b else val_b
            return result
        if tier_a == "TIER_1":
            result["preferred_value"] = val_a
            result["confidence"] = "TIER_1_OVERRIDE"
        elif tier_b == "TIER_1":
            result["preferred_value"] = val_b
            result["confidence"] = "TIER_1_OVERRIDE"
        else:
           
            result["status"] = "DATA_INVALID"
            result["confidence"] = "QUARANTINED"
            logger.warning(f"SYSTEM STATUS = DATA_INVALID. Discrepancy: {discrepancy*100:.2f}%")

        return result
