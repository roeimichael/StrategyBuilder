"""TEMA 20/60 crossover strategy with volume confirmation"""

import math

import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton


class Tema20_tema60(Strategy_skeleton):

    def __init__(self, args):
        """Initialize TEMA indicators and crossover signal"""
        super(Tema20_tema60, self).__init__(args)
        self.volume_average = bt.indicators.SMA(self.data.volume, period=14)
        self.tema_20 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=20)
        self.tema_60 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=60)
        self.tcross = bt.indicators.CrossOver(self.tema_20, self.tema_60)
        self.tcross_flag = 0

    def next(self):
        """Execute strategy logic on each bar"""
        self.log('Close, %.2f' % self.data[0])

        if self.tema_60[0] is not None:
            if self.order:
                return

            if not self.position:
                amount_to_invest = (self.args['order_pct'] * self.broker.cash)
                if self.tcross_flag == 0:
                    if self.data.volume[0] > self.volume_average and self.tcross == 1:
                        self.tcross_flag = 1
                        self.size = math.floor(amount_to_invest / self.data.close)
                        self.order = self.buy(size=self.size)
                        self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
            else:
                if self.tcross == -1 and self.tcross_flag == 1:
                    self.tcross_flag = 0
                    self.log('SELL CREATE (LONG), %.2f' % self.data[0])
                    self.close()
