import backtrader as bt
from src.shared.strategy_skeleton import Strategy_skeleton


class Tema20_tema60(Strategy_skeleton):
    params = (
        ("tema_short_period", 20),
        ("tema_long_period", 60),
        ("volume_period", 14)
    )

    def __init__(self, args):
        super(Tema20_tema60, self).__init__(args)
        self.volume_average = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.tema_20 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=self.p.tema_short_period)
        self.tema_60 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=self.p.tema_long_period)
        self.tcross = bt.indicators.CrossOver(self.tema_20, self.tema_60)
        self.position_type = 0

    def get_technical_indicators(self):
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
            if self.data.volume[0] > self.volume_average and self.tcross == 1:
                self.buy()
                self.position_type = 1
                self.log('BUY CREATE (LONG - TEMA Cross Up), %.2f ' % self.data[0])
            elif self.data.volume[0] > self.volume_average and self.tcross == -1:
                self.sell()
                self.position_type = -1
                self.log('SELL CREATE (SHORT - TEMA Cross Down), %.2f ' % self.data[0])
        else:
            if self.position_type == 1 and self.tcross == -1:
                self.close()
                self.position_type = 0
                self.log('SELL CREATE (LONG EXIT - TEMA Cross Down), %.2f' % self.data[0])
            elif self.position_type == -1 and self.tcross == 1:
                self.close()
                self.position_type = 0
                self.log('BUY CREATE (SHORT EXIT - TEMA Cross Up), %.2f' % self.data[0])
