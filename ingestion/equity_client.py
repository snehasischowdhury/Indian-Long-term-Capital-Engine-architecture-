import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class EquityMarketClient:
    """
    Tier 3 Data Source: Yahoo Finance Aggregator.
    Data Reliability Score (DRS) = 0.65.
    """
    def __init__(self):
        self.data_tier = "TIER_3"
        self.drs = 0.65

    def fetch_historical_ohlcv(self, ticker: str, days_back: int = 30) -> pd.DataFrame:
        if not ticker.endswith(".NS") and not ticker.endswith(".BO"):
            ticker = f"{ticker}.NS"
            
        start_date = datetime.now() - timedelta(days=days_back)
        
        try:
            data = yf.download(ticker, start=start_date, progress=False)
            if data.empty:
                return pd.DataFrame()
                
            data.reset_index(inplace=True)
            
           
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [c[0].lower() for c in data.columns]
            else:
                data.columns = [col.lower() for col in data.columns]
            
            df = pd.DataFrame({
                "timestamp": data.get("date", data.get("index")),
                "open": data["open"],
                "high": data["high"],
                "low": data["low"],
                "close": data["close"],
                "volume": data["volume"],
                "data_tier": self.data_tier,
                "reliability_score": self.drs
            })
            return df.dropna()
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()
