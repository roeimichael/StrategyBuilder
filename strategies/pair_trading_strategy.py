from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt


class BOLLStrat(bt.Strategy):

    params = (
        ("period", 20),
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
        self.boll_low, self.boll_high = 0, 0
        self.size = 0

    def short_pair(self):
        pass

    def long_pair(self):
        pass

    def close_pair(self):
        pass

    def next(self):

        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        if not self.position:
            amount_to_invest =  self.broker.cash

            if self.data.high[0] > self.boll.lines.top:

                self.boll_high = 1
                self.size = math.floor(amount_to_invest / self.data.high)
                # self.sell(size=self.size)# short
                self.short_pair()

                self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])


            if self.data.low[0] < self.boll.lines.bot:

                self.boll_low = 1
                self.size = math.floor(amount_to_invest / self.data.low)
                # self.buy(size=self.size)# long
                self.long_pair()

                self.log('BUY CREATE (LONG), %.2f ' % self.data[0])


        else:
            if self.position.size > 0:
                if self.data.close[0] > self.boll.lines.mid[0] and self.boll_low == 1:
                    self.boll_low = 0
                    self.close_pair()


                    self.log('SELL CREATE (LONG), %.2f ' % self.data[0])

                elif self.data.close[0] < self.boll.lines.mid[0] and self.boll_high == 1:
                    self.boll_low = 0
                    self.close_pair()


                    self.log('BUY CREATE (SHORT), %.2f ' % self.data[0])
