import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class Alligator_strategy(Strategy_skeleton):
    params = (
        ("lips_period", 5),
        ("teeth_period", 8),
        ("jaws_period", 13),
        ("ema_period", 200)
    )

    def __init__(self, args):
        super(Alligator_strategy, self).__init__(args)
        self.lips = bt.indicators.SmoothedMovingAverage(self.data.close, period=self.p.lips_period)
        self.teeth = bt.indicators.SmoothedMovingAverage(self.data.close, period=self.p.teeth_period)
        self.jaws = bt.indicators.SmoothedMovingAverage(self.data.close, period=self.p.jaws_period)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.p.ema_period)
        self.cross_lips = bt.indicators.CrossOver(self.data.close, self.lips)
        self.long_position = 0
        self.short_position = 0

    def get_technical_indicators(self):
        return {
            'Alligator_Lips_SMA5': self.lips,
            'Alligator_Teeth_SMA8': self.teeth,
            'Alligator_Jaws_SMA13': self.jaws,
            'EMA_200': self.ema
        }

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
