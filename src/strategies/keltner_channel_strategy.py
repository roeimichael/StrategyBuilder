import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class Keltner_Channel(Strategy_skeleton):
    params = (
        ("ema_period", 20),
        ("atr_period", 10),
        ("atr_multiplier", 2.0)
    )

    def __init__(self, args):
        super(Keltner_Channel, self).__init__(args)
        self.ema = bt.indicators.EMA(self.data.close, period=self.p.ema_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.upper_band = self.ema + (self.atr * self.p.atr_multiplier)
        self.lower_band = self.ema - (self.atr * self.p.atr_multiplier)
        self.cross_upper = bt.ind.CrossOver(self.data.close, self.upper_band)
        self.cross_ema = bt.ind.CrossOver(self.data.close, self.ema)

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if len(self) < max(self.p.ema_period, self.p.atr_period):
            return

        if not self.position:
            if self.cross_upper > 0:
                self.buy()
                self.log(f'BUY CREATE (Breakout: {self.data.close[0]:.2f} > {self.upper_band[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.cross_ema < 0:
                self.close()
                self.log(f'SELL CREATE (Reversion: {self.data.close[0]:.2f} < {self.ema[0]:.2f}), %.2f' % self.data[0])
