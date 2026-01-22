import backtrader as bt

class MFI(bt.Indicator):
    lines = ('mfi',)
    params = (('period', 14),)
    plotinfo = dict(plot=True, subplot=True)
    plotlines = dict(mfi=dict(_plotskip=False,))

    def __init__(self):
        self.addminperiod(self.params.period + 1)
        typical_price = (self.data.high + self.data.low + self.data.close) / 3.0
        raw_money_flow = typical_price * self.data.volume
        self.tp_change = typical_price - typical_price(-1)
        pos_flow = bt.If(self.tp_change > 0, raw_money_flow, 0)
        neg_flow = bt.If(self.tp_change < 0, raw_money_flow, 0)
        pos_mf = bt.ind.SumN(pos_flow, period=self.params.period)
        neg_mf = bt.ind.SumN(neg_flow, period=self.params.period)
        mf_ratio = bt.DivByZero(pos_mf, neg_mf, zero=1.0)
        self.lines.mfi = 100.0 - (100.0 / (1.0 + mf_ratio))
