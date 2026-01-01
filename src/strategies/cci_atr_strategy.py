

from typing import Dict
import math

import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton

class CCI_ATR_Strategy(Strategy_skeleton):
    params = (
        ("cci_period", 20),
        ("cci_entry", -100),
        ("cci_exit", 100),
        ("atr_period", 14)
    )

    def __init__(self, args: Dict[str, float]):
        
        super(CCI_ATR_Strategy, self).__init__(args)
        self.size = 0
        self.in_position = False
        self.cci = bt.indicators.CCI(self.data, period=self.p.cci_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)

    def next(self) -> None:        if self.order:
            return

        if len(self) < max(self.p.cci_period, self.p.atr_period) + 1:
            return

        if not self.position:
            if (self.cci[0] > self.p.cci_entry and
                self.cci[-1] <= self.p.cci_entry and
                self.atr[0] > self.atr[-1]):
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (CCI: {self.cci[0]:.2f}, ATR: {self.atr[0]:.2f}), %.2f' % self.data[0])
                self.in_position = True
        else:
            if self.cci[0] < self.p.cci_exit and self.cci[-1] >= self.p.cci_exit:
                self.close()
                self.log(f'SELL CREATE (CCI: {self.cci[0]:.2f}), %.2f' % self.data[0])
                self.in_position = False
