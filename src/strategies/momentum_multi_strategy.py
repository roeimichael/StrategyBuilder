"""Multi-Indicator Momentum Strategy combining ROC, RSI, and OBV"""

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
        """Initialize ROC, RSI, and OBV indicators"""
        super(Momentum_Multi, self).__init__(args)
        self.size = 0
        self.roc = bt.indicators.ROC(self.data.close, period=self.p.roc_period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.obv = OBV(self.data)

    def next(self):
        """Execute strategy logic on each bar"""
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if len(self) < max(self.p.roc_period, self.p.rsi_period) + 1:
            return

        if not self.position:
            if (self.roc[0] > self.p.roc_threshold and
                self.p.rsi_min < self.rsi[0] < self.p.rsi_max and
                self.obv[0] > self.obv[-1]):
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}, OBV↑), %.2f' % self.data[0])
        else:
            if self.roc[0] < 0 or self.rsi[0] > self.p.rsi_exit:
                self.close()
                self.log(f'SELL CREATE (ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}), %.2f' % self.data[0])
