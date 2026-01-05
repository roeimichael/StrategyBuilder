import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton
from src.indicators.mfi_indicator import MFI


class MFI_Strategy(Strategy_skeleton):
    params = (
        ("period", 14),
        ("oversold", 20),
        ("overbought", 80)
    )

    def __init__(self, args):
        super(MFI_Strategy, self).__init__(args)
        self.mfi = MFI(self.data, period=self.p.period)

    def get_technical_indicators(self):
        """Return technical indicators to be exposed for charting"""
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
                self.log(f'BUY CREATE (MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.mfi[0] > self.p.overbought:
                self.close()
                self.log(f'SELL CREATE (MFI: {self.mfi[0]:.2f}), %.2f' % self.data[0])
