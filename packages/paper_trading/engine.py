from dataclasses import dataclass
from enum import Enum

class Side(str,Enum):
    BUY="BUY"
    SELL="SELL"

@dataclass(frozen=True)
class PaperOrder:
    symbol: str
    side: Side
    quantity: int
    requested_price: float
    stop: float
    target: float

@dataclass(frozen=True)
class Fill:
    symbol: str
    side: Side
    quantity: int
    requested_price: float
    fill_price: float
    slippage: float
    fee: float

def simulate_market_fill(order: PaperOrder, *, slippage_per_unit: float=0.0, fee_per_contract: float=0.0) -> Fill:
    if order.quantity <= 0:
        raise ValueError("quantity must be positive")
    direction=1 if order.side==Side.BUY else -1
    slip=abs(slippage_per_unit)
    fill=order.requested_price+direction*slip
    return Fill(order.symbol,order.side,order.quantity,order.requested_price,fill,slip*order.quantity,fee_per_contract*order.quantity)
