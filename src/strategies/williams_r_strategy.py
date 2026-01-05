import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class Williams_R(Strategy_skeleton):
    params = (
        ("period", 14),
        ("oversold", -80),
        ("overbought", -20)
    )

    def __init__(self, args):
        super(Williams_R, self).__init__(args)
        self.willr = bt.indicators.WilliamsR(self.data, period=self.p.period)

    def get_technical_indicators(self):
        """Return technical indicators to be exposed for charting"""
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
                self.log(f'BUY CREATE (WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.willr[0] > self.p.overbought:
                self.close()
                self.log(f'SELL CREATE (WillR: {self.willr[0]:.2f}), %.2f' % self.data[0])
