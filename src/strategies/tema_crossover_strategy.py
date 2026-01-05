import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class Tema20_tema60(Strategy_skeleton):

    def __init__(self, args):
        super(Tema20_tema60, self).__init__(args)
        self.volume_average = bt.indicators.SMA(self.data.volume, period=14)
        self.tema_20 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=20)
        self.tema_60 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=60)
        self.tcross = bt.indicators.CrossOver(self.tema_20, self.tema_60)
        self.tcross_flag = 0

    def get_technical_indicators(self):
        """Return technical indicators to be exposed for charting"""
        return {
            'Volume_SMA': self.volume_average,
            'TEMA_20': self.tema_20,
            'TEMA_60': self.tema_60
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.tema_60[0] is None:
            return
        if self.order:
            return

        if not self.position:
            if self.tcross_flag == 0:
                if self.data.volume[0] > self.volume_average and self.tcross == 1:
                    self.tcross_flag = 1
                    self.buy()
                    self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
        else:
            if self.tcross == -1 and self.tcross_flag == 1:
                self.tcross_flag = 0
                self.close()
                self.log('SELL CREATE (LONG), %.2f' % self.data[0])
