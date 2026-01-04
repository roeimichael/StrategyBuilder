import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class Alligator_strategy(Strategy_skeleton):

    def __init__(self, args):
        super(Alligator_strategy, self).__init__(args)
        self.lips = bt.indicators.SmoothedMovingAverage(self.data.close, period=5)
        self.teeth = bt.indicators.SmoothedMovingAverage(self.data.close, period=8)
        self.jaws = bt.indicators.SmoothedMovingAverage(self.data.close, period=13)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=200)
        self.cross_lips = bt.indicators.CrossOver(self.data.close, self.lips)
        self.long_position = 0
        self.short_position = 0

    def next(self):
        self.log('Close, %.2f' % self.data[0])
        if self.ema[0] is None:
            return
        if self.order:
            return

        if not self.position:
            if self.data.close[0] > self.ema[0] and (self.jaws[0] < self.teeth[0] < self.lips[0]):
                if self.lips[0] > self.data.close[0] > self.teeth[0]:
                    self.long_position = 1
                    self.buy()
                    self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
            if self.data.close[0] < self.ema[0] and (self.jaws[0] > self.teeth[0] > self.lips[0]):
                if self.lips[0] < self.data.close[0] < self.teeth[0]:
                    self.short_position = 1
                    self.sell()
                    self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
        else:
            if self.long_position == 1:
                if self.cross_lips > 0:
                    self.long_position = 0
                    self.close()
                    self.log('SELL CREATE (LONG), %.2f' % self.data[0])
            elif self.short_position == 1:
                if self.cross_lips < 0:
                    self.short_position = 0
                    self.close()
                    self.log('BUY CREATE (SHORT), %.2f' % self.data[0])
