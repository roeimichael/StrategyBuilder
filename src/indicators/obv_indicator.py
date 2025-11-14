"""On-Balance Volume (OBV) Indicator"""
import backtrader as bt


class OBV(bt.Indicator):
    """
    On-Balance Volume
    OBV accumulates volume when price closes higher, subtracts when lower
    """
    lines = ('obv',)

    def __init__(self):
        # Calculate price change direction
        self.change = self.data.close - self.data.close(-1)
        
    def next(self):
        if len(self) == 1:
            # First bar - set OBV to volume
            self.lines.obv[0] = self.data.volume[0]
        else:
            # Accumulate or subtract volume based on price direction
            prev_obv = self.lines.obv[-1]
            
            if self.change[0] > 0:
                # Price up - add volume
                self.lines.obv[0] = prev_obv + self.data.volume[0]
            elif self.change[0] < 0:
                # Price down - subtract volume
                self.lines.obv[0] = prev_obv - self.data.volume[0]
            else:
                # Price unchanged - keep same OBV
                self.lines.obv[0] = prev_obv
