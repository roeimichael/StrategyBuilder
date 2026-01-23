import backtrader as bt
from src.shared.strategy_skeleton import Strategy_skeleton


class Williams_R(Strategy_skeleton):
    params = (
        ("period", 14),
        ("oversold", -80),
        ("overbought", -20)
    )

    def __init__(self, args):
        super(Williams_R, self).__init__(args)
        self.willr = bt.indicators.WilliamsR(self.data, period=self.p.period)
        self.position_type = 0

    def get_technical_indicators(self):
        return {
            'Williams_R': self.willr
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            if len(self) < self.p.period:
                return
            if self.willr[0] < self.p.oversold:
                self.buy()
                self.position_type = 1
                self.log(f'BUY CREATE (LONG - WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
            elif self.willr[0] > self.p.overbought:
                self.sell()
                self.position_type = -1
                self.log(f'SELL CREATE (SHORT - WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.position_type == 1:
                if self.willr[0] > self.p.overbought:
                    self.close()
                    self.position_type = 0
                    self.log(f'SELL CREATE (LONG EXIT - WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
            elif self.position_type == -1:
                if self.willr[0] < self.p.oversold:
                    self.close()
                    self.position_type = 0
                    self.log(f'BUY CREATE (SHORT EXIT - WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
