from enum import Enum
from dataclasses import dataclass
from typing import Tuple
from portfolio.paper_portfolio import PaperPortfolio

class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    DO_NOTHING = "DO_NOTHING"

@dataclass
class DecisionContext:
    ticker: str
    current_price: float
    expected_return: float
    kelly_fraction: float
    max_weight: float
    fqs_score: float

class DecisionEngine:
    @staticmethod
    def generate_trade_instruction(ctx: DecisionContext, portfolio: PaperPortfolio) -> Tuple[Action, float]:
        if ctx.fqs_score < 40.0:
            if ctx.ticker in portfolio.positions:
                return Action.SELL, portfolio.positions[ctx.ticker].quantity
            return Action.DO_NOTHING, 0.0
            
        if ctx.expected_return <= 0:
            if ctx.ticker in portfolio.positions:
                return Action.SELL, portfolio.positions[ctx.ticker].quantity
            return Action.DO_NOTHING, 0.0
            
        target_weight = min(ctx.kelly_fraction, ctx.max_weight)
        target_value = portfolio.total_value() * target_weight
        
        current_value = 0.0
        if ctx.ticker in portfolio.positions:
            current_value = portfolio.positions[ctx.ticker].market_value()
            
        value_delta = target_value - current_value
        
        if value_delta > (ctx.current_price * 1.0):
            qty = value_delta / ctx.current_price
            return Action.BUY, round(qty, 4)
        elif value_delta < -(ctx.current_price * 1.0):
            qty = abs(value_delta) / ctx.current_price
            return Action.SELL, round(qty, 4)
            
        return Action.DO_NOTHING, 0.0
