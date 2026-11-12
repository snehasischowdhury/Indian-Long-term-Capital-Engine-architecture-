from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal
import os

class SystemSettings(BaseSettings):
    ENVIRONMENT: Literal["development", "research", "paper", "production"] = "development"
    LOG_LEVEL: str = "INFO"
    APP_SECRET_KEY: str = Field(..., min_length=32)
    DATABASE_URL: str = Field(default="sqlite:///./data/ilce_local.db")
    
    DATA_QUARANTINE_THRESHOLD: float = Field(default=0.01, description="1% discrepancy triggers quarantine")
    QUARTER_KELLY_FRACTION: float = Field(default=0.25, le=0.5, ge=0.05)
    MAX_SINGLE_STOCK_WEIGHT: float = Field(default=0.08, le=0.15)
    
  
    DEFAULT_RISK_FREE_RATE: float = Field(default=0.070, description="Indian 10Y G-Sec")
    ERP_INDIA: float = Field(default=0.050, description="India Equity Risk Premium")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = SystemSettings()
