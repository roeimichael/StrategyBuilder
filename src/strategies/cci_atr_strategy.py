import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class CCI_ATR_Strategy(Strategy_skeleton):
    params = (
        ("cci_period", 20),
        ("cci_entry", -100),
        ("cci_exit", 100),
        ("atr_period", 14)
    )

    def __init__(self, args):
        super(CCI_ATR_Strategy, self).__init__(args)
        self.position_type = 0
        self.cci = bt.indicators.CCI(self.data, period=self.p.cci_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)

    def get_technical_indicators(self):
        return {
            'CCI': self.cci,
            'ATR': self.atr
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if len(self) < max(self.p.cci_period, self.p.atr_period) + 1:
            return

        if not self.position:
            if (self.cci[0] > self.p.cci_entry and
                self.cci[-1] <= self.p.cci_entry and
                self.atr[0] > self.atr[-1]):
                self.buy()
                self.position_type = 1
                self.log(f'BUY CREATE (LONG - CCI: {self.cci[0]:.2f}, ATR: {self.atr[0]:.2f}), %.2f' % self.data[0])
            elif (self.cci[0] < -self.p.cci_entry and
                self.cci[-1] >= -self.p.cci_entry and
                self.atr[0] > self.atr[-1]):
                self.sell()
                self.position_type = -1
                self.log(f'SELL CREATE (SHORT - CCI: {self.cci[0]:.2f}, ATR: {self.atr[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.position_type == 1:
                if self.cci[0] < self.p.cci_exit and self.cci[-1] >= self.p.cci_exit:
                    self.close()
                    self.position_type = 0
                    self.log(f'SELL CREATE (LONG EXIT - CCI: {self.cci[0]:.2f}), %.2f' % self.data[0])
            elif self.position_type == -1:
                if self.cci[0] > -self.p.cci_exit and self.cci[-1] <= -self.p.cci_exit:
                    self.close()
                    self.position_type = 0
                    self.log(f'BUY CREATE (SHORT EXIT - CCI: {self.cci[0]:.2f}), %.2f' % self.data[0])
