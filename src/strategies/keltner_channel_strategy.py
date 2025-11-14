"""
Keltner Channel Breakout Strategy
Uses EMA and ATR to create dynamic channels for breakout trading

Entry: Price breaks above upper channel
Exit: Price crosses back below middle line (EMA)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton


class Keltner_Channel(Strategy_skeleton):
    params = (
        ("ema_period", 20),
        ("atr_period", 10),
        ("atr_multiplier", 2.0)
    )

    def __init__(self, args):
        super(Keltner_Channel, self).__init__(args)
        self.size = 0

        # EMA as the middle line
        self.ema = bt.indicators.EMA(
            self.data.close,
            period=self.p.ema_period
        )

        # ATR for channel width
        self.atr = bt.indicators.ATR(
            self.data,
            period=self.p.atr_period
        )

        # Calculate upper and lower bands
        self.upper_band = self.ema + (self.atr * self.p.atr_multiplier)
        self.lower_band = self.ema - (self.atr * self.p.atr_multiplier)

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        # Wait for indicators to be ready
        if len(self) < max(self.p.ema_period, self.p.atr_period):
            return

        if not self.position:  # not in the market
            # Buy signal: Price breaks above upper Keltner Channel
            if self.data.close[0] > self.upper_band[0]:
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (Breakout: {self.data.close[0]:.2f} > {self.upper_band[0]:.2f}), %.2f' % self.data[0])

        else:
            # Sell signal: Price crosses back below middle line
            if self.data.close[0] < self.ema[0]:
                self.close()
                self.log(f'SELL CREATE (Reversion: {self.data.close[0]:.2f} < {self.ema[0]:.2f}), %.2f' % self.data[0])
