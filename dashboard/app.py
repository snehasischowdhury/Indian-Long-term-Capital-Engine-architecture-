import streamlit as st
from regime.regime_detector import MarketRegimeDetector, MacroStateInputs
from risk.thermostat import RiskThermostatEngine, ThermostatInputs
from monte_carlo.simulator import MonteCarloWealthSimulator
from alerts.alert_engine import SystemAlertEngine, AlertConfig

st.set_page_config(page_title="ILCE Command Center", layout="wide")

st.title("🇮🇳 ILCE: Daily Portfolio Command Center")

st.sidebar.header("Market Telemetry")
vix_val = st.sidebar.slider("India VIX", 10.0, 45.0, 14.0)
nifty_dd = st.sidebar.slider("Nifty 50 Drawdown (%)", 0.0, 50.0, 2.0)
gdp_trend = st.sidebar.slider("GDP Trend (%)", 0.0, 10.0, 6.5)
cpi_trend = st.sidebar.slider("CPI Inflation (%)", 2.0, 10.0, 4.5)
port_dd = st.sidebar.slider("Portfolio Drawdown (%)", 0.0, 30.0, 1.5)

macro_inputs = MacroStateInputs(
    gdp_growth_trend_pct=gdp_trend / 100.0,
    cpi_inflation_pct=cpi_trend / 100.0,
    rbi_repo_trend_bps=0.0,
    pmi_composite=52.0,
    earnings_revision_breadth=0.10,
    india_vix=vix_val,
    credit_growth_spread=0.02
)
regime_probs = MarketRegimeDetector.estimate_regime_probabilities(macro_inputs)
dominant_regime = max(regime_probs.items(), key=lambda x: x[1])[0]

thermostat_inputs = ThermostatInputs(
    nifty_pe_percentile=0.75,
    india_vix=vix_val,
    breadth_pct_above_200d=65.0,
    gsec_10y_yield_velocity_bps=10.0,
    usdinr_30d_realized_vol=0.04,
    crude_oil_6m_momentum_pct=0.10,
    fii_net_flow_trend_zscore=0.5,
    credit_spread_stress_index=0.2,
    drawdown_from_peak_pct=nifty_dd / 100.0,
    global_credit_spread_bps=350.0
)
thermostat_data = RiskThermostatEngine.calculate_thermostat_score(thermostat_inputs)

alert_engine = SystemAlertEngine(AlertConfig(max_portfolio_drawdown_pct=0.10))
active_alerts = alert_engine.evaluate_system_state(
    current_drawdown=port_dd / 100.0,
    current_vix=vix_val,
    yield_velocity=10.0,
    current_regime=dominant_regime
)

if active_alerts:
    for alert in active_alerts:
        if alert["level"] == "CRITICAL":
            st.error(f"🚨 {alert['type']}: {alert['message']}")
        else:
            st.warning(f"⚠️ {alert['type']}: {alert['message']}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Dominant Regime", dominant_regime, f"{regime_probs[dominant_regime]*100:.1f}% Prob")
col2.metric("Risk Thermostat", f"{thermostat_data['thermostat_score']}/100", thermostat_data['posture'])
col3.metric("India VIX", f"{vix_val:.1f}")
col4.metric("System Status", "NORMAL" if not active_alerts else "ELEVATED RISK")

st.subheader("Monte Carlo Wealth Projection")
col_a, col_b = st.columns(2)
with col_a:
    sip_amount = st.number_input("Monthly SIP (₹)", value=100000)
    horizon = st.slider("Investment Horizon (Years)", 5, 30, 15)
with col_b:
    if st.button("Run Simulation"):
        sim = MonteCarloWealthSimulator(initial_corpus=1000000, monthly_sip=sip_amount, annual_sip_step_up_pct=0.10, horizon_years=horizon, simulations=5000)
        res = sim.run_simulation(expected_annual_return=0.12, annual_volatility=0.16)
        st.success(f"Median Corpus at Year {horizon}: ₹{res['median_final_corpus']/1e7:.2f} Cr")
        st.info(f"Probability of exceeding ₹10 Cr: {res['milestone_probabilities'].get('10Cr', 0)*100:.1f}%")
