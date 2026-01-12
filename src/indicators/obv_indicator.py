import backtrader as bt

class OBV(bt.Indicator):
    lines = ('obv',)
    plotinfo = dict(plot=True, subplot=True)

    def __init__(self):
        self.addminperiod(1)

    def prenext(self):
        if len(self) == 1:
            self.lines.obv[0] = self.data.volume[0]
        else:
            self._calculate_obv()

    def next(self):
        self._calculate_obv()

    def _calculate_obv(self):
        if len(self) == 1:
            self.lines.obv[0] = self.data.volume[0]
        else:
            prev_obv = self.lines.obv[-1]
            if self.data.close[0] > self.data.close[-1]:
                self.lines.obv[0] = prev_obv + self.data.volume[0]
            elif self.data.close[0] < self.data.close[-1]:
                self.lines.obv[0] = prev_obv - self.data.volume[0]
            else:
                self.lines.obv[0] = prev_obv
