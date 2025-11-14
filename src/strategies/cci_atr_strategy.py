"""
CCI + ATR Volatility Breakout Strategy
Combines Commodity Channel Index with ATR for volatility-based entries

Entry: CCI crosses above -100 (trend reversal) AND ATR is rising (volatility)
Exit: CCI crosses below +100 (trend weakening)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
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

    def __init__(self, args):
        super(CCI_ATR_Strategy, self).__init__(args)
        self.size = 0
        self.in_position = False

        # CCI indicator
        self.cci = bt.indicators.CCI(
            self.data,
            period=self.p.cci_period
        )

        # ATR for volatility
        self.atr = bt.indicators.ATR(
            self.data,
            period=self.p.atr_period
        )

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        # Wait for indicators to be ready
        if len(self) < max(self.p.cci_period, self.p.atr_period) + 1:
            return

        if not self.position:  # not in the market
            # Buy signal: CCI crosses above entry level AND ATR is rising (increasing volatility)
            if (self.cci[0] > self.p.cci_entry and
                self.cci[-1] <= self.p.cci_entry and
                self.atr[0] > self.atr[-1]):

                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (CCI: {self.cci[0]:.2f}, ATR: {self.atr[0]:.2f}), %.2f' % self.data[0])
                self.in_position = True

        else:
            # Sell signal: CCI crosses below exit level
            if self.cci[0] < self.p.cci_exit and self.cci[-1] >= self.p.cci_exit:
                self.close()
                self.log(f'SELL CREATE (CCI: {self.cci[0]:.2f}), %.2f' % self.data[0])
                self.in_position = False
