

from typing import Dict
import math

import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton
from indicators.mfi_indicator import MFI

class MFI_Strategy(Strategy_skeleton):
    params = (
        ("period", 14),
        ("oversold", 20),
        ("overbought", 80)
    )

    def __init__(self, args: Dict[str, float]):
        
        super(MFI_Strategy, self).__init__(args)
        self.size = 0
        self.mfi = MFI(self.data, period=self.p.period)

    def next(self) -> None:        if self.order:
            return

        if not self.position:
            if len(self) < self.p.period:
                return

            if self.mfi[0] < self.p.oversold:
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.mfi[0] > self.p.overbought:
                self.close()
                self.log(f'SELL CREATE (MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
