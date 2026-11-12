import pytest
from portfolio.paper_portfolio import PaperPortfolio, Position
from portfolio.decision_engine import DecisionEngine, DecisionContext, Action

def test_paper_portfolio_execution():
    port = PaperPortfolio(cash=100000.0)
    
    port.execute_trade("RELIANCE.NS", quantity=10.0, price=2500.0, transaction_cost=50.0)
    assert port.cash == 74950.0
    assert "RELIANCE.NS" in port.positions
    assert port.total_value() == 99950.0
    
    port.update_price("RELIANCE.NS", 3000.0)
    assert port.total_value() == 104950.0
    
    port.execute_trade("RELIANCE.NS", quantity=-10.0, price=3000.0, transaction_cost=60.0)
    assert port.cash == 104890.0
    assert "RELIANCE.NS" not in port.positions

def test_decision_engine_buy_logic():
    port = PaperPortfolio(cash=100000.0)
    ctx = DecisionContext(
        ticker="TCS.NS",
        current_price=4000.0,
        expected_return=0.12,
        kelly_fraction=0.10,
        max_weight=0.08,
        fqs_score=85.0
    )
    
    action, qty = DecisionEngine.generate_trade_instruction(ctx, port)
    
    assert action == Action.BUY
    assert qty == 2.0

def test_decision_engine_sell_impaired_asset():
    port = PaperPortfolio(cash=50000.0)
    port.execute_trade("BADSTOCK.NS", quantity=100.0, price=500.0)
    
    ctx = DecisionContext(
        ticker="BADSTOCK.NS",
        current_price=400.0,
        expected_return=-0.05,
        kelly_fraction=0.0,
        max_weight=0.05,
        fqs_score=25.0
    )
    
    action, qty = DecisionEngine.generate_trade_instruction(ctx, port)
    
    assert action == Action.SELL
    assert qty == 100.0
