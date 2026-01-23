import backtrader as bt
from src.shared.strategy_skeleton import Strategy_skeleton
from src.shared.indicators.obv_indicator import OBV


class Momentum_Multi(Strategy_skeleton):
    params = (
        ("roc_period", 12),
        ("roc_threshold", 2.0),
        ("rsi_period", 14),
        ("rsi_min", 40),
        ("rsi_max", 60),
        ("rsi_exit", 70)
    )

    def __init__(self, args):
        super(Momentum_Multi, self).__init__(args)
        self.roc = bt.indicators.ROC(self.data.close, period=self.p.roc_period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.obv = OBV(self.data)
        self.position_type = 0

    def get_technical_indicators(self):
        return {
            'ROC': self.roc,
            'RSI': self.rsi,
            'OBV': self.obv
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if len(self) < max(self.p.roc_period, self.p.rsi_period) + 1:
            return

        if not self.position:
            if (self.roc[0] > self.p.roc_threshold and
                self.p.rsi_min < self.rsi[0] < self.p.rsi_max and
                self.obv[0] > self.obv[-1]):
                self.buy()
                self.position_type = 1
                self.log(f'BUY CREATE (LONG - ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}, OBV↑), %.2f' % self.data[0])
            elif (self.roc[0] < -self.p.roc_threshold and
                self.p.rsi_min < self.rsi[0] < self.p.rsi_max and
                self.obv[0] < self.obv[-1]):
                self.sell()
                self.position_type = -1
                self.log(f'SELL CREATE (SHORT - ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}, OBV↓), %.2f' % self.data[0])
        else:
            if self.position_type == 1:
                if self.roc[0] < 0 or self.rsi[0] > self.p.rsi_exit:
                    self.close()
                    self.position_type = 0
                    self.log(f'SELL CREATE (LONG EXIT - ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}), %.2f' % self.data[0])
            elif self.position_type == -1:
                if self.roc[0] > 0 or self.rsi[0] < (100 - self.p.rsi_exit):
                    self.close()
                    self.position_type = 0
                    self.log(f'BUY CREATE (SHORT EXIT - ROC: {self.roc[0]:.2f}, RSI: {self.rsi[0]:.2f}), %.2f' % self.data[0])
