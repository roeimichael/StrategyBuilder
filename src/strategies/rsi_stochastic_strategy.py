"""RSI + Stochastic Oscillator Strategy combining oversold/overbought signals"""

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
        """Initialize RSI and Stochastic indicators"""
        super(RSI_Stochastic, self).__init__(args)
        self.size = 0
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.stoch = bt.indicators.Stochastic(self.data, period=self.p.stoch_period)

    def next(self):
        """Execute strategy logic on each bar"""
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            if len(self) < max(self.p.rsi_period, self.p.stoch_period):
                return

            if (self.rsi[0] < self.p.rsi_oversold and
                self.stoch.percK[0] < self.p.stoch_oversold):
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])
        else:
            if (self.rsi[0] > self.p.rsi_overbought or
                self.stoch.percK[0] > self.p.stoch_overbought):
                self.close()
                self.log(f'SELL CREATE (RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])
