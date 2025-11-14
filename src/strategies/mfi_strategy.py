"""
MFI (Money Flow Index) Strategy
Volume-weighted RSI for identifying overbought/oversold with volume confirmation

Entry: MFI < 20 (strong selling pressure)
Exit: MFI > 80 (strong buying pressure)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
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

    def __init__(self, args):
        super(MFI_Strategy, self).__init__(args)
        self.size = 0

        # Money Flow Index indicator (like RSI but volume-weighted)
        self.mfi = MFI(
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

            # Buy signal: MFI shows strong selling pressure (oversold)
            if self.mfi[0] < self.p.oversold:
                amount_to_invest = self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.low[0])
                self.buy(size=self.size)
                self.log(f'BUY CREATE (MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])

        else:
            # Sell signal: MFI shows strong buying pressure (overbought)
            if self.mfi[0] > self.p.overbought:
                self.close()
                self.log(f'SELL CREATE (MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
