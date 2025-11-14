"""Money Flow Index (MFI) Indicator"""

import backtrader as bt


class MFI(bt.Indicator):
    """Money Flow Index - Volume-weighted RSI"""
    lines = ('mfi',)
    params = (('period', 14),)

    def __init__(self):
        """Initialize MFI indicator calculation"""
        typical_price = (self.data.high + self.data.low + self.data.close) / 3.0
        raw_money_flow = typical_price * self.data.volume
        pos_flow = bt.If(typical_price > typical_price(-1), raw_money_flow, 0)
        neg_flow = bt.If(typical_price < typical_price(-1), raw_money_flow, 0)
        pos_mf = bt.ind.SumN(pos_flow, period=self.params.period)
        neg_mf = bt.ind.SumN(neg_flow, period=self.params.period)
        mf_ratio = pos_mf / neg_mf
        self.lines.mfi = 100.0 - (100.0 / (1.0 + mf_ratio))
