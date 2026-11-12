import pandas as pd
from typing import Tuple, Dict, Any

class DataIntegrityChecker:
    @staticmethod
    def validate_price_series(df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        issues = []
        if df.empty:
            return False, {"error": "Empty dataframe"}
        
        # Non-negative prices
        for col in ['open', 'high', 'low', 'close']:
            if (df[col] <= 0).any():
                issues.append(f"Non-positive prices detected in {col}.")
            
        # Logical OHLC relationships
        if (df['high'] < df['low']).any():
            issues.append("High price lower than low price detected.")
            
        if (df['high'] < df['open']).any() or (df['high'] < df['close']).any():
            issues.append("High price breached by Open or Close.")
            
        is_valid = len(issues) == 0
        return is_valid, {"status": "PASSED" if is_valid else "FAILED", "issues": issues}
