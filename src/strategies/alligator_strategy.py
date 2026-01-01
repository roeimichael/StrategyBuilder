

from typing import Dict
import math

import backtrader as bt

from core.strategy_skeleton import Strategy_skeleton

class Alligator_strategy(Strategy_skeleton):

    def __init__(self, args: Dict[str, float]):
        
        super(Alligator_strategy, self).__init__(args)
        self.lips = bt.indicators.SmoothedMovingAverage(self.data.close, period=5)
        self.teeth = bt.indicators.SmoothedMovingAverage(self.data.close, period=8)
        self.jaws = bt.indicators.SmoothedMovingAverage(self.data.close, period=13)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=200)
        self.cross_up = bt.indicators.CrossOver(self.lips, self.teeth)
        self.cross_down = bt.indicators.CrossOver(self.teeth, self.lips)
        self.short_position = 0
        self.long_position = 0

    def next(self) -> None:        if self.ema[0] is not None:
            if self.order:
                return
            if not self.position:
                amount_to_invest = (self.args['order_pct'] * self.broker.cash)
                if self.data.close[0] > self.ema[0] and (self.jaws[0] < self.teeth[0] < self.lips[0]):
                    if self.lips[0] > self.data.close[0] > self.teeth[0]:
                        self.long_position = 1
                        self.size = math.floor(amount_to_invest / self.data.close)
                        self.order = self.buy(size=self.size)
                        self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                if self.data.close[0] < self.ema[0] and (self.jaws[0] > self.teeth[0] > self.lips[0]):
                    if self.lips[0] < self.data.close[0] < self.teeth[0]:
                        self.short_position = 1
                        self.size = math.floor(amount_to_invest / self.data.close)
                        self.order = self.sell(size=self.size)
                        self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
            else:
                if self.long_position == 1:
                    if self.data.close[0] >= self.lips[0]:
                        self.long_position = 0
                        self.log('SELL CREATE (LONG), %.2f' % self.data[0])
                        self.close()
                elif self.short_position == 1:
                    if self.data.close[0] <= self.lips[0]:
                        self.short_position = 0
                        self.log('BUY CREATE (SHORT), %.2f' % self.data[0])
                        self.close()
