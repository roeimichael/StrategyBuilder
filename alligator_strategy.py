import backtrader as bt
import math
from strategy_skeleton import Strategy_skeleton


class Alligator_strategy(Strategy_skeleton):

    def __init__(self, args):
        super(Alligator_strategy, self).__init__(args)
        self.lips = bt.indicators.SmoothedMovingAverage(self.data.close, period=5)
        self.teeth = bt.indicators.SmoothedMovingAverage(self.data.close, period=8)
        self.jaws = bt.indicators.SmoothedMovingAverage(self.data.close, period=13)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=200)
        self.cross_up = bt.indicators.CrossOver(self.lips, self.teeth)
        self.cross_down = bt.indicators.CrossOver(self.teeth, self.lips)
        self.short_position = 0
        self.long_position = 0

    def next(self):
        print(self.datas[0].datetime.date(0))
        print(type(self.datas[0].datetime.date(0)))
        self.log('Close, %.2f' % self.data[0])

        if self.ema[0] is not None:  # biggest indicator to be calculated (200 days)

            if self.order:
                return  # pending order execution

            if not self.position:  # not in the market

                amount_to_invest = (self.args['order_pct'] * self.broker.cash)
                if self.data.close[0] > self.ema[0] and (self.jaws[0] < self.teeth[0] < self.lips[0]):  # if the graph is above the ema we can buy long
                    if self.lips[0] > self.data.close[0] > self.teeth[0]:
                        # if self.lips[0] > self.data.teeth[0] and self.lips[0] > self.jaws[0]:
                        self.long_position = 1
                        self.size = math.floor(amount_to_invest / self.data.close)
                        self.order = self.buy(size=self.size)
                        print(" ")
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                        self.print_stats()
                if self.data.close[0] < self.ema[0] and (self.jaws[0] > self.teeth[0] > self.lips[0]):  # if the graph is under the ema we can buy short
                    if self.lips[0] < self.data.close[0] < self.teeth[0]:
                        self.short_position = 1
                        self.size = math.floor(amount_to_invest / self.data.close)
                        self. order = self.sell(size=self.size)
                        print(" ")
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
                        self.print_stats()

            else:  # selling
                if self.long_position == 1:  # we have a long position opened
                    if self.data.close[0] >= self.lips[0]:  # checking if the sl/tp is happening
                        self.long_position = 0
                        print(" ")
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        self.log('SELL CREATE (LONG), %.2f' % self.data[0])
                        self.close()
                        self.print_stats()
                elif self.short_position == 1:  # we have a short position
                    if self.data.close[0] <= self.lips[0]:  # checking if the sl/tp is happening
                        self.short_position = 0
                        print(" ")
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        self.log('BUY CREATE (SHORT), %.2f' % self.data[0])
                        self.close()
                        self.print_stats()
