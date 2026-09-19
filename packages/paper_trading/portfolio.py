from dataclasses import dataclass
from packages.paper_trading.engine import Fill, Side

@dataclass
class PaperPosition:
    symbol: str
    quantity: int = 0
    average_price: float = 0.0
    realized_pnl: float = 0.0
    fees: float = 0.0

    def apply(self, fill: Fill) -> None:
        signed=fill.quantity if fill.side==Side.BUY else -fill.quantity
        if self.quantity == 0 or self.quantity*signed > 0:
            total=abs(self.quantity)*self.average_price+fill.quantity*fill.fill_price
            self.quantity += signed
            self.average_price=total/abs(self.quantity)
        else:
            closing=min(abs(self.quantity),fill.quantity)
            direction=1 if self.quantity>0 else -1
            self.realized_pnl += (fill.fill_price-self.average_price)*direction*closing
            self.quantity += signed
            if self.quantity == 0:
                self.average_price=0.0
            elif abs(signed)>closing:
                self.average_price=fill.fill_price
        self.fees += fill.fee
