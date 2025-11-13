import backtrader as bt
import math
from strategy_skeleton import Strategy_skeleton
from dateutil.relativedelta import relativedelta
import datetime


class TEMA_MACD_NEW(Strategy_skeleton):

    def __init__(self, args):
        super(TEMA_MACD_NEW, self).__init__(args)
        self.size = 0
        self.macd = bt.indicators.MACD(self.data)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        self.tema_open = bt.indicators.TripleExponentialMovingAverage(self.data.open, period=12)
        self.tema_close = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=12)

        self.tcross = bt.indicators.CrossOver(self.tema_close, self.tema_open)

        self.flag_tema = 0
        self.is_tradeable = 0
        self.max_macd = 0
        self.min_macd = 0
        self.is_short = 0
        self.is_long = 0
        self.first_cross = 0
        self.year_start = self.datas[0].datetime.date(0) - relativedelta(years=1)

    def next(self):

        if self.year_start > self.datas[0].datetime.date(0):
            if self.macd.macd[0] > self.max_macd:
                self.max_macd = self.macd.macd[0]
            if self.macd.macd[0] < self.min_macd:
                self.min_macd = self.macd.macd[0]
            return
        self.log('Close, %.2f' % self.data[0])

        if self.flag_tema == 1 and self.tcross == -1:
            self.flag_tema = 0  # sell signal

        if self.flag_tema == 0 and self.tcross == 1:
            self.flag_tema = 1  # buy signal

        if self.is_tradeable == 0 and (self.macd.macd[0] > self.max_macd or self.macd.macd[
            0] < self.min_macd):  # checks if the stock is good for # trading
            self.is_tradeable = 1
            self.mcross = 0
            print("stage1")
            print(self.mcross)

        if self.is_tradeable == 1 and self.mcross != 0.0:
            print("stage 2")
            self.is_tradeable = 2

        if self.tema_open[0] is not None and self.is_tradeable == 2:
            print("started")
            if self.order:
                return  # pending order execution

            if not self.position:  # not in the market
                amount_to_invest = (self.args['order_pct'] * self.broker.cash)
                if self.macd.macd[0] < 0:  # short
                    if self.flag_tema == 0:
                        if self.mcross[0] == -1:
                            self.is_short = 1
                            self.size = math.floor(amount_to_invest / self.data.close)
                            self.order = self.sell(size=self.size)
                            print(" ")
                            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                            self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
                            self.print_stats()

                if self.macd.macd[0] > 0:  # long
                    if self.flag_tema == 1:
                        if self.mcross[0] == 1:
                            self.is_short = 1
                            self.size = math.floor(amount_to_invest / self.data.close)
                            self.order = self.buy(size=self.size)
                            print(" ")
                            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                            self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                            self.print_stats()

            elif self.position:
                if self.is_short == 1:  # short selling
                    if self.flag_tema == 1:
                        if self.mcross[0] == 1:
                            self.is_short = 0
                            print(" ")
                            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                            self.log('BUY CREATE (SHORT) CLOSE POSITION, %.2f' % self.data[0])
                            self.close()
                            self.print_stats()

                if self.is_long == 1:  # long selling
                    if self.flag_tema == 0:
                        if self.mcross[0] == -1:
                            self.is_long = 0
                            print(" ")
                            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                            self.log('SELL CREATE (LONG) CLOSE POSITION, %.2f' % self.data[0])
                            self.close()
                            self.print_stats()
