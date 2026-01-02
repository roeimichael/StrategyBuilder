"""Williams %R Mean Reversion Strategy"""

import math

import backtrader as bt

from ..core.strategy_skeleton import Strategy_skeleton


class Williams_R(Strategy_skeleton):
    params = (
        ("period", 14),
        ("oversold", -80),
        ("overbought", -20)
    )

    def __init__(self, args):
        """Initialize Williams %R indicator"""
        super(Williams_R, self).__init__(args)
        self.size = 0
        self.willr = bt.indicators.WilliamsR(self.data, period=self.p.period)

    def next(self):
        """Execute strategy logic on each bar"""
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            if len(self) < self.p.period:
                return

            if self.willr[0] < self.p.oversold:
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.willr[0] > self.p.overbought:
                self.close()
                self.log(f'SELL CREATE (WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
