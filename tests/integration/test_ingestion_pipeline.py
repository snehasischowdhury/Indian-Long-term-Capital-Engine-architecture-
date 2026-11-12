import pytest
from ingestion.amfi_client import AMFIClient
from ingestion.equity_client import EquityMarketClient
from validation.integrity_checker import DataIntegrityChecker
from validation.discrepancy_resolver import DiscrepancyResolver

def test_amfi_ingestion():
    client = AMFIClient()
    nav_data = client.fetch_daily_navs()
    assert len(nav_data) > 1000, "Should fetch thousands of mutual fund NAVs"
    assert "scheme_code" in nav_data[0]
    assert nav_data[0]["data_tier"] == "TIER_1"

def test_equity_ingestion_and_integrity():
    client = EquityMarketClient()
    df = client.fetch_historical_ohlcv("RELIANCE.NS", days_back=10)
    assert not df.empty
    
    is_valid, report = DataIntegrityChecker.validate_price_series(df)
    assert is_valid is True, f"Integrity failed: {report}"

def test_discrepancy_logic():
   
    res1 = DiscrepancyResolver.resolve_conflict(100.0, "TIER_1", 1.0, 102.0, "TIER_3", 0.65)
    assert res1["preferred_value"] == 100.0
    assert res1["confidence"] == "TIER_1_OVERRIDE"

  
    res2 = DiscrepancyResolver.resolve_conflict(100.0, "TIER_2", 0.85, 102.0, "TIER_3", 0.65)
    assert res2["status"] == "DATA_INVALID"
