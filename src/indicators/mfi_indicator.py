"""Money Flow Index (MFI) Indicator"""
import backtrader as bt


class MFI(bt.Indicator):
    """
    Money Flow Index - Volume-weighted RSI
    MFI = 100 - (100 / (1 + Money Flow Ratio))
    """
    lines = ('mfi',)
    params = (('period', 14),)

    def __init__(self):
        # Typical Price = (High + Low + Close) / 3
        typical_price = (self.data.high + self.data.low + self.data.close) / 3.0
        
        # Raw Money Flow = Typical Price × Volume
        raw_money_flow = typical_price * self.data.volume
        
        # Positive and Negative Money Flow
        pos_flow = bt.If(typical_price > typical_price(-1), raw_money_flow, 0)
        neg_flow = bt.If(typical_price < typical_price(-1), raw_money_flow, 0)
        
        # Sum over period
        pos_mf = bt.ind.SumN(pos_flow, period=self.params.period)
        neg_mf = bt.ind.SumN(neg_flow, period=self.params.period)
        
        # Money Flow Ratio
        mf_ratio = pos_mf / neg_mf
        
        # Money Flow Index
        self.lines.mfi = 100.0 - (100.0 / (1.0 + mf_ratio))
