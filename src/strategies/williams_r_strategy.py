"""
Williams %R Mean Reversion Strategy
Uses Williams %R for oversold/overbought signals

Entry: Williams %R < -80 (oversold)
Exit: Williams %R > -20 (overbought)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton


class Williams_R(Strategy_skeleton):
    params = (
        ("period", 14),
        ("oversold", -80),
        ("overbought", -20)
    )

    def __init__(self, args):
        super(Williams_R, self).__init__(args)
        self.size = 0

        # Williams %R indicator
        self.willr = bt.indicators.WilliamsR(
            self.data,
            period=self.p.period
        )

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            # Wait for indicator to be ready
            if len(self) < self.p.period:
                return

            # Buy signal: Williams %R is oversold
            if self.willr[0] < self.p.oversold:
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])

        else:
            # Sell signal: Williams %R reaches overbought
            if self.willr[0] > self.p.overbought:
                self.close()
                self.log(f'SELL CREATE (WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
