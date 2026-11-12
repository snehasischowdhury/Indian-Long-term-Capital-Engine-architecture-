import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Integer, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SecurityMaster(Base):
    __tablename__ = "security_master"
    security_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String(32), nullable=False, index=True)
    exchange = Column(String(16), nullable=False, default="NSE")
    asset_class = Column(String(32), nullable=False) # EQUITY, ETF, GOLD
    is_active = Column(Boolean, default=True)

class MarketDataDaily(Base):
    __tablename__ = "market_data_daily"
    record_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    security_id = Column(String(36), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    close = Column(Numeric(14, 4), nullable=False)
    data_tier = Column(String(16), default="TIER_1")
    reliability_score = Column(Numeric(5, 2), default=1.0)

class FundamentalPointInTime(Base):
    __tablename__ = "fundamentals_point_in_time"
    record_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    security_id = Column(String(36), nullable=False, index=True)
    filing_date = Column(DateTime, nullable=False)
    revenue = Column(Numeric(18, 2), nullable=True)
    pat = Column(Numeric(18, 2), nullable=True)
    promoter_pledge_pct = Column(Numeric(5, 2), default=0.0)
    auditor_qualification = Column(Boolean, default=False)

class InvestmentDecisionJournal(Base):
    __tablename__ = "investment_decision_journal"
    decision_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    security_id = Column(String(36), nullable=False)
    signal = Column(String(16), nullable=False) # BUY, HOLD, SELL, DO_NOTHING
    target_weight = Column(Numeric(6, 4), nullable=False)
    risk_thermostat_score = Column(Numeric(5, 2), nullable=False)
    rationale = Column(JSON, nullable=False)
