from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt

from strategy_skeleton import Strategy_skeleton


class Bollinger_three(Strategy_skeleton):

    def __init__(self, args):
        super(Bollinger_three, self).__init__(args)
        self.in_trade = 0
        self.size = 0
        self.boll = bt.indicators.BollingerBands(period=80, devfactor=2.0)

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        if self.in_trade == 0:  # not in the market
            amount_to_invest = self.broker.cash
            if self.data.close[0] < self.boll.lines.bot[0]:
                self.size = math.floor(amount_to_invest / self.data.close)
                self.sell(size=self.size)
                self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
                self.in_trade = 1

            if self.data.close[0] > self.boll.lines.top[0]:
                self.size = math.floor(amount_to_invest / self.data.close)
                self.buy(size=self.size)
                self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                self.in_trade = 2
        else:  # if already in a position (closing condition)
            if self.in_trade == 2:  # long position
                if self.data.close[0] < self.boll.lines.top[0]:
                    self.close()
                    self.log('Close Long Position , %.2f ' % self.data[0])
                    self.in_trade = 0
                    self.print_stats()
            else:
                if self.data.close[0] > self.boll.lines.bot[0]:
                    self.close()
                    self.log('Close Short Position , %.2f ' % self.data[0])
                    self.in_trade = 0
                    self.print_stats()

