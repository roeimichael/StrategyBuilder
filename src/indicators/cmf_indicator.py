import backtrader as bt

class CMF(bt.Indicator):
    lines = ('money_flow',)
    params = (('period', 20),)
    plotinfo = dict(plot=True, subplot=True, plotyhlines=[0])

    def __init__(self):
        self.addminperiod(self.params.period)
        c = self.data.close
        h = self.data.high
        l = self.data.low
        v = self.data.volume
        hl_diff = h - l
        clv = bt.If(bt.Or(hl_diff == 0, bt.And(c == h, c == l)), 0, ((2 * c - l - h) / hl_diff) * v)
        sum_clv = bt.indicators.SumN(clv, period=self.params.period)
        sum_vol = bt.indicators.SumN(v, period=self.params.period)
        self.lines.money_flow = bt.DivByZero(sum_clv, sum_vol, zero=0.0)
