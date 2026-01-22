import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton
from src.shared.indicators.mfi_indicator import MFI


class MFI_Strategy(Strategy_skeleton):
    params = (
        ("period", 14),
        ("oversold", 20),
        ("overbought", 80)
    )

    def __init__(self, args):
        super(MFI_Strategy, self).__init__(args)
        self.mfi = MFI(self.data, period=self.p.period)
        self.position_type = 0

    def get_technical_indicators(self):
        return {
            'MFI': self.mfi
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            if len(self) < self.p.period:
                return
            if self.mfi[0] < self.p.oversold:
                self.buy()
                self.position_type = 1
                self.log(f'BUY CREATE (LONG - MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
            elif self.mfi[0] > self.p.overbought:
                self.sell()
                self.position_type = -1
                self.log(f'SELL CREATE (SHORT - MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.position_type == 1:
                if self.mfi[0] > self.p.overbought:
                    self.close()
                    self.position_type = 0
                    self.log(f'SELL CREATE (LONG EXIT - MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
            elif self.position_type == -1:
                if self.mfi[0] < self.p.oversold:
                    self.close()
                    self.position_type = 0
                    self.log(f'BUY CREATE (SHORT EXIT - MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
