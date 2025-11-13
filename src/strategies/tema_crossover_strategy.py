import backtrader as bt
import math
from core.strategy_skeleton import Strategy_skeleton


class Tema20_tema60(Strategy_skeleton):

    def __init__(self, args):
        super(Tema20_tema60, self).__init__(args)
        self.volume_average = bt.indicators.SMA(self.data.volume, period=14)
        self.tema_20 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=20)
        self.tema_60 = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=60)
        self.tcross = bt.indicators.CrossOver(self.tema_20, self.tema_60)
        self.tcross_flag = 0
    def next(self):
        print(self.datas[0].datetime.date(0))
        print(type(self.datas[0].datetime.date(0)))
        self.log('Close, %.2f' % self.data[0])

        if self.tema_60[0] is not None:

            if self.order:
                return  # pending order execution

            if not self.position:  # not in the market

                amount_to_invest = (self.args['order_pct'] * self.broker.cash)
                if self.tcross_flag == 0:
                    if self.data.volume[0] > self.volume_average and self.tcross == 1:
                        self.tcross_flag = 1
                        self.size = math.floor(amount_to_invest / self.data.close)
                        self.order = self.buy(size=self.size)
                        print(" ")
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                        self.print_stats()

            else:
                if self.tcross == -1 and self.tcross_flag == 1:
                    self.tcross_flag = 0
                    print(" ")
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    self.log('SELL CREATE (LONG), %.2f' % self.data[0])
                    self.close()
                    self.print_stats()

