from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton


class adx_strat(Strategy_skeleton):

    def __init__(self, args):
        super(adx_strat, self).__init__(args)
        self.type = 0
        self.size = 0
        self.adx = bt.indicators.AverageDirectionalMovementIndex()  # period=14
        self.ma20 = bt.indicators.MovingAverageSimple(period=20)
        self.ma50 = bt.indicators.MovingAverageSimple(period=50)
        self.boll = bt.indicators.BollingerBands(period=14)

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        # Wait for enough data for indicators (ADX needs 14 periods + 1 for lookback)
        if len(self) < 51:  # max(ma50 period, adx period + lookback)
            return

        if self.type == 0:  # not in the market
            amount_to_invest = self.broker.cash
            if self.adx[-1] >= 25:
                if self.ma20[-1] > self.ma50[-1]:
                    self.size = math.floor(amount_to_invest / self.data.low)
                    # self.buy(size=self.size)# long
                    self.buy(size=self.size)
                    self.log('BUY CREATE (LONG TRENDY), %.2f ' % self.data[0])
                    self.type = 1
            else:
                if self.data.low[0] < self.boll.lines.bot:
                    self.size = math.floor(amount_to_invest / self.data.low)
                    # self.buy(size=self.size)# long
                    self.buy(size=self.size)
                    self.log('BUY CREATE (LONG STABLE), %.2f ' % self.data[0])
                    self.type = 2
        else:
            if self.type == 1:
                if self.ma20[-1] < self.ma50[-1]:
                    self.close()
                    self.log('SELL CREATE (LONG TRENDY), %.2f ' % self.data[0])
                    self.type = 0
                    self.print_stats()
            elif self.type == 2:
                if self.data.close[0] > self.boll.lines.mid[0]:
                    self.close()
                    self.log('SELL CREATE (LONG STABLE), %.2f ' % self.data[0])
                    self.type = 0
                    self.print_stats()

