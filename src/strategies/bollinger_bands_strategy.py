import math
from typing import Dict
import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton

class Bollinger_three(Strategy_skeleton):
    params = (
        ("period", 20),
        ("devfactor", 2)
    )

    def __init__(self, args: Dict[str, float]):
        super(Bollinger_three, self).__init__(args)
        self.boll_low = 0
        self.boll_high = 0
        self.size = 0
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)

    def next(self) -> None:
        if self.order:
            return
        if not self.position:
            amount_to_invest = self.broker.cash
            if self.data.low[0] < self.boll.lines.bot:
                self.boll_low = 1
                self.size = math.floor(amount_to_invest / self.data.low)
                self.buy(size=self.size)
        else:
            if self.position.size > 0:
                if self.data.close[0] > self.boll.lines.mid[0] and self.boll_low == 1:
                    self.boll_low = 0
                    self.close()
