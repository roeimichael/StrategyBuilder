import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class TEMA_MACD(Strategy_skeleton):
    params = (
        ("macd1", 12),
        ("macd2", 26),
        ("macdsig", 9),
        ("tema_period", 12)
    )

    def __init__(self, args):
        super(TEMA_MACD, self).__init__(args)
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.macd_histogram = self.macd.macd - self.macd.signal
        self.tema_open = bt.indicators.TripleExponentialMovingAverage(self.data.open, period=self.p.tema_period)
        self.tema_close = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=self.p.tema_period)
        self.tcross = bt.indicators.CrossOver(self.tema_close, self.tema_open)
        self.flag_macd = 0
        self.flag_tema = 0

    def get_technical_indicators(self):
        return {
            'MACD': self.macd.macd,
            'MACD_Signal': self.macd.signal,
            'MACD_Histogram': self.macd_histogram,
            'TEMA_Open': self.tema_open,
            'TEMA_Close': self.tema_close
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])
        if self.tema_open[0] is None:
            return

        if self.flag_tema == 1 and self.tcross == -1:
            self.flag_tema = 0
        if self.flag_macd == 1 and self.mcross == -1:
            self.flag_macd = 0

        if self.order:
            return

        if not self.position:
            if self.flag_tema == 0 and self.tcross == 1:
                self.flag_tema = 1
            if self.flag_macd == 0 and self.mcross == 1 and self.flag_tema == 1:
                self.flag_macd = 1
            if self.flag_macd == 1 and self.flag_tema == 1:
                self.buy()
                self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
        elif self.position:
            if self.flag_tema != 1 or self.flag_macd != 1:
                self.close()
                self.log('SELL CREATE (LONG), %.2f' % self.data[0])
