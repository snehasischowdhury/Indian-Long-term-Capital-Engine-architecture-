import numpy as np
import pandas as pd
from typing import Dict, Any

class BacktestEngine:
    @staticmethod
    def calculate_metrics(daily_returns: pd.Series, risk_free_rate: float = 0.07) -> Dict[str, Any]:
        clean_returns = daily_returns.dropna()
        if clean_returns.empty:
            raise ValueError("Returns series is empty.")
            
        days = len(clean_returns)
        cumulative_return = (1.0 + clean_returns).prod() - 1.0
        cagr = ((1.0 + cumulative_return) ** (252.0 / days)) - 1.0 if days > 0 else 0.0
        
        ann_vol = clean_returns.std() * np.sqrt(252.0)
        
        daily_rf = risk_free_rate / 252.0
        excess_returns = clean_returns - daily_rf
        
        sharpe = (excess_returns.mean() / clean_returns.std()) * np.sqrt(252.0) if clean_returns.std() > 0 else 0.0
        
        downside_returns = excess_returns[excess_returns < 0]
        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252.0) if (len(downside_returns) > 1 and downside_returns.std() > 0) else 0.0
        
        cum_idx = (1.0 + clean_returns).cumprod()
        peak_idx = cum_idx.cummax()
        drawdowns = (peak_idx - cum_idx) / peak_idx
        max_drawdown = float(drawdowns.max())
        
        return {
            "cumulative_return": round(float(cumulative_return), 4),
            "cagr": round(float(cagr), 4),
            "volatility": round(float(ann_vol), 4),
            "sharpe": round(float(sharpe), 4),
            "sortino": round(float(sortino), 4),
            "max_drawdown": round(max_drawdown, 4)
        }
