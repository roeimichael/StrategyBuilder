import backtrader as bt
from src.shared.indicators.cmf_indicator import CMF
from src.shared.strategy_skeleton import Strategy_skeleton


class MACD_CMF_ATR_Strategy(Strategy_skeleton):
    params = (
        ("macd1", 12),
        ("macd2", 26),
        ("macdsig", 9),
        ("atrperiod", 14),
        ("atrdist", 2.0)
    )

    def __init__(self, args):
        super(MACD_CMF_ATR_Strategy, self).__init__(args)
        self.stop_loss_long = 0
        self.take_profit_long = 0
        self.stop_loss_short = 0
        self.take_profit_short = 0
        self.is_long, self.is_short = 0, 0
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.mcross_short = bt.indicators.CrossOver(self.macd.signal, self.macd.macd)
        self.macd_histogram = self.macd.macd - self.macd.signal
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)
        self.cmf = CMF(self.data)

    def get_technical_indicators(self):
        return {
            'MACD': self.macd.macd,
            'MACD_Signal': self.macd.signal,
            'MACD_Histogram': self.macd_histogram,
            'ATR': self.atr,
            'CMF': self.cmf
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            if self.macd.macd[0] > 0 and self.macd.signal[0] > 0:
                if self.mcross[0] == 1.0 and self.cmf[0] > 0:
                    self.buy()
                    self.is_long = 1
                    self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                    pdist = self.atr[0] * self.p.atrdist
                    self.stop_loss_long = self.data.close[0] - pdist
                    self.take_profit_long = self.data.close[0] + (2 * pdist)

            elif self.macd.macd[0] < 0 and self.macd.signal[0] < 0:
                if self.mcross_short == 1.0 and self.cmf[0] < 0:
                    self.sell()
                    self.is_short = 1
                    self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
                    pdist = self.atr[0] * self.p.atrdist
                    self.stop_loss_short = self.data.close[0] + pdist
                    self.take_profit_short = self.data.close[0] - (2 * pdist)
        else:
            pclose = self.data.close[0]

            if self.is_long == 1 and pclose >= self.take_profit_long:
                self.is_long = 0
                self.close()
                self.log('SELL CREATE (LONG), %.2f' % self.data[0])

            if self.is_long == 1 and pclose <= self.stop_loss_long:
                self.is_long = 0
                self.close()
                self.log('STOP CREATE (LONG), %.2f ' % self.data[0])

            if self.is_short == 1 and pclose <= self.take_profit_short:
                self.is_short = 0
                self.close()
                self.log('BUY CREATE (SHORT), %.2f' % self.data[0])

            if self.is_short == 1 and pclose >= self.stop_loss_short:
                self.is_short = 0
                self.close()
                self.log('STOP CREATE (SHORT), %.2f ' % self.data[0])
