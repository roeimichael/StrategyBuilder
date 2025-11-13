from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt

from strategy_skeleton import Strategy_skeleton


class ethereum_vol(Strategy_skeleton):
    params = (
        ("period", 20),
        ("devfactor", 2)
    )

    def __init__(self, args):
        super(ethereum_vol, self).__init__(args)
        self.boll_low, self.boll_high = 0, 0
        self.size = 0
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market

            amount_to_invest =  self.broker.cash

            if self.data.low[0] < self.boll.lines.bot:
                self.boll_low = 1
                self.size = math.floor(amount_to_invest / self.data.low)
                # self.buy(size=self.size)# long
                self.buy(size=self.size)

                self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
        else:
            if self.position.size > 0:
                if self.data.close[0] > self.boll.lines.mid[0] and self.boll_low == 1:
                    self.boll_low = 0
                    self.close()
                    self.log('SELL CREATE (LONG), %.2f ' % self.data[0])


