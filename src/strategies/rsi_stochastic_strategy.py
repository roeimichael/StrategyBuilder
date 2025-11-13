"""
RSI + Stochastic Oscillator Strategy
Classic oversold/overbought strategy combining RSI and Stochastic

Entry: RSI < 30 AND Stochastic %K < 20 (oversold)
Exit: RSI > 70 OR Stochastic %K > 80 (overbought)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton


class RSI_Stochastic(Strategy_skeleton):
    params = (
        ("rsi_period", 14),
        ("rsi_oversold", 30),
        ("rsi_overbought", 70),
        ("stoch_period", 14),
        ("stoch_oversold", 20),
        ("stoch_overbought", 80)
    )

    def __init__(self, args):
        super(RSI_Stochastic, self).__init__(args)
        self.size = 0

        # RSI indicator
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.p.rsi_period
        )

        # Stochastic indicator
        self.stoch = bt.indicators.Stochastic(
            self.data,
            period=self.p.stoch_period
        )

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            # Wait for indicators to be ready
            if len(self) < max(self.p.rsi_period, self.p.stoch_period):
                return

            # Buy signal: Both RSI and Stochastic are oversold
            if (self.rsi[0] < self.p.rsi_oversold and
                self.stoch.percK[0] < self.p.stoch_oversold):

                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])

        else:
            # Sell signal: Either RSI or Stochastic reaches overbought
            if (self.rsi[0] > self.p.rsi_overbought or
                self.stoch.percK[0] > self.p.stoch_overbought):

                self.close()
                self.log(f'SELL CREATE (RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])
                self.print_stats()
