import sys
import logging
from database.connection import init_db, SessionLocal
from database.models import InvestmentDecisionJournal
from regime.regime_detector import MarketRegimeDetector, MacroStateInputs
from risk.thermostat import RiskThermostatEngine, ThermostatInputs
from risk.kill_switch import PortfolioKillSwitchController, MarketEnvironmentState
from ingestion.equity_client import EquityMarketClient
from validation.integrity_checker import DataIntegrityChecker
from fundamentals.quality_score import FundamentalEngine, FinancialInputs
from valuation.dcf_model import DynamicDCFEngine, DCFParameters
from valuation.margin_of_safety import ValuationClassifier
from portfolio.paper_portfolio import PaperPortfolio
from portfolio.decision_engine import DecisionEngine, DecisionContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ILCE_MAIN")

def run_daily_pipeline():
    logger.info("INITIATING ILCE DAILY PIPELINE")
    init_db()
    
    macro_inputs = MacroStateInputs(0.065, 0.045, 0.0, 52.0, 0.10, 14.0, 0.02)
    regime_probs = MarketRegimeDetector.estimate_regime_probabilities(macro_inputs)
    dominant_regime = max(regime_probs.items(), key=lambda x: x[1])[0]
    logger.info(f"DOMINANT REGIME: {dominant_regime}")
    
    thermo_inputs = ThermostatInputs(0.75, 14.0, 65.0, 10.0, 0.04, 0.10, 0.5, 0.2, 0.02, 350.0)
    thermostat_data = RiskThermostatEngine.calculate_thermostat_score(thermo_inputs)
    rts = thermostat_data["thermostat_score"]
    logger.info(f"RISK THERMOSTAT: {rts} ({thermostat_data['posture']})")
    
    env_state = MarketEnvironmentState(0.02, 14.0, 10.0, False)
    kill_stage = PortfolioKillSwitchController.evaluate_stage(env_state)
    logger.info(f"KILL SWITCH STAGE: {kill_stage.value}")
    
    portfolio = PaperPortfolio(cash=1000000.0)
    
    ticker = "RELIANCE.NS"
    equity_client = EquityMarketClient()
    df = equity_client.fetch_historical_ohlcv(ticker, days_back=10)
    
    if df.empty:
        logger.error(f"DATA INVALID: Could not fetch {ticker}")
        return
        
    is_valid, report = DataIntegrityChecker.validate_price_series(df)
    if not is_valid:
        logger.error(f"DATA INTEGRITY FAILURE: {report}")
        return
        
    current_price = float(df.iloc[-1]['close'])
    logger.info(f"{ticker} CURRENT PRICE: {current_price}")
    
    fqs_inputs = FinancialInputs(0.20, 0.18, 500.0, 1500.0, 10.0, 1.5, 1200.0, 1000.0, 900.0, 0.0, False, 0.10)
    fundamental_engine = FundamentalEngine()
    fqs = fundamental_engine.compute_fqs(fqs_inputs)
    
    dcf_params = DCFParameters(100.0, 0.12, 0.08, 0.05, 0.10, 50.0, 10.0)
    intrinsic_value = DynamicDCFEngine.calculate_fair_value_per_share(dcf_params)
    mos_assessment = ValuationClassifier.classify(ticker, current_price, intrinsic_value)
    
    kelly_fraction = PortfolioKillSwitchController.calculate_constrained_fractional_kelly(
        expected_excess_return=0.08,
        return_variance=0.04,
        base_fraction=0.25,
        max_allowed_weight=0.08,
        stage=kill_stage
    )
    
    ctx = DecisionContext(
        ticker=ticker,
        current_price=current_price,
        expected_return=0.12,
        kelly_fraction=kelly_fraction,
        max_weight=0.08,
        fqs_score=fqs
    )
    
    action, qty = DecisionEngine.generate_trade_instruction(ctx, portfolio)
    logger.info(f"DECISION ENGINE: {action.value} {qty} shares of {ticker}")
    
    db = SessionLocal()
    try:
        journal_entry = InvestmentDecisionJournal(
            security_id=ticker,
            signal=action.value,
            target_weight=kelly_fraction,
            risk_thermostat_score=rts,
            rationale={
                "price": current_price,
                "fqs": fqs,
                "intrinsic_value": intrinsic_value,
                "mos_band": mos_assessment.valuation_band,
                "regime": dominant_regime,
                "kill_stage": kill_stage.value
            }
        )
        db.add(journal_entry)
        db.commit()
        logger.info("DECISION LOGGED TO IMMUTABLE WORM JOURNAL")
    except Exception as e:
        db.rollback()
        logger.error(f"JOURNAL WRITE FAILED: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_daily_pipeline()
