

from typing import Optional
import backtrader as bt

class OBV(bt.Indicator):
    
    lines = ('obv',)

    def __init__(self):
        
        self.change = self.data.close - self.data.close(-1)

    def next(self):
        
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
