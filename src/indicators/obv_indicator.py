"""On-Balance Volume (OBV) Indicator"""

import backtrader as bt


class OBV(bt.Indicator):
    """On-Balance Volume indicator"""
    lines = ('obv',)

    def __init__(self):
        """Initialize OBV indicator calculation"""
        self.change = self.data.close - self.data.close(-1)

    def next(self):
        """Calculate OBV value for each bar"""
        if len(self) == 1:
            self.lines.obv[0] = self.data.volume[0]
        else:
            prev_obv = self.lines.obv[-1]
            if self.change[0] > 0:
                self.lines.obv[0] = prev_obv + self.data.volume[0]
            elif self.change[0] < 0:
                self.lines.obv[0] = prev_obv - self.data.volume[0]
            else:
                self.lines.obv[0] = prev_obv
