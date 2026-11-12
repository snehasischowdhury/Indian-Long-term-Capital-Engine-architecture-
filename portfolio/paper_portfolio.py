from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Position:
    ticker: str
    quantity: float
    average_cost: float
    current_price: float

    def market_value(self) -> float:
        return self.quantity * self.current_price

@dataclass
class PaperPortfolio:
    cash: float
    positions: Dict[str, Position] = field(default_factory=dict)

    def total_value(self) -> float:
        pos_value = sum(p.market_value() for p in self.positions.values())
        return self.cash + pos_value

    def update_price(self, ticker: str, new_price: float):
        if ticker in self.positions:
            self.positions[ticker].current_price = new_price

    def execute_trade(self, ticker: str, quantity: float, price: float, transaction_cost: float = 0.0):
        cost = (quantity * price) + transaction_cost
        
        if quantity > 0 and self.cash < cost:
            raise ValueError("Insufficient cash for trade execution")
            
        self.cash -= cost
        
        if ticker not in self.positions:
            self.positions[ticker] = Position(ticker, 0.0, 0.0, price)
            
        pos = self.positions[ticker]
        
        if quantity > 0:
            total_cost = (pos.quantity * pos.average_cost) + (quantity * price)
            pos.quantity += quantity
            pos.average_cost = total_cost / pos.quantity
        else:
            pos.quantity += quantity
            if pos.quantity <= 0.0001:
                del self.positions[ticker]
                
        if ticker in self.positions:
            self.positions[ticker].current_price = price
