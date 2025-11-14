"""
Multi-Indicator Momentum Strategy
Combines ROC (Rate of Change), RSI, and OBV for strong momentum signals

Entry: ROC > threshold AND RSI between 40-60 AND OBV rising
Exit: ROC < 0 OR RSI > 70
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton
from indicators.obv_indicator import OBV


class Momentum_Multi(Strategy_skeleton):
    params = (
        ("roc_period", 12),
        ("roc_threshold", 2.0),
        ("rsi_period", 14),
        ("rsi_min", 40),
        ("rsi_max", 60),
        ("rsi_exit", 70)
    )

    def __init__(self, args):
        super(Momentum_Multi, self).__init__(args)
        self.size = 0

        # Rate of Change - momentum indicator
        self.roc = bt.indicators.ROC(
            self.data.close,
            period=self.p.roc_period
        )

        # RSI - trend strength
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.p.rsi_period
        )

        # On Balance Volume - volume trend
        self.obv = OBV(
            self.data
        )

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        # Wait for indicators to be ready
        if len(self) < max(self.p.roc_period, self.p.rsi_period) + 1:
            return

        if not self.position:  # not in the market
            # Buy signal: Strong positive momentum with neutral RSI and rising volume
            if (self.roc[0] > self.p.roc_threshold and
                self.p.rsi_min < self.rsi[0] < self.p.rsi_max and
                self.obv[0] > self.obv[-1]):

                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}, OBV↑), %.2f' % self.data[0])

        else:
            # Sell signal: Momentum turns negative OR RSI overbought
            if self.roc[0] < 0 or self.rsi[0] > self.p.rsi_exit:
                self.close()
                self.log(f'SELL CREATE (ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}), %.2f' % self.data[0])
