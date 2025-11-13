import backtrader as bt
import math
from strategy_skeleton import Strategy_skeleton


class TEMA_MACD_strategy(Strategy_skeleton):

    def __init__(self, args):
        super(TEMA_MACD_strategy, self).__init__(args)
        self.tema_crossed = 0
        self.macd_crossed = 0

        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.args['macd1'],
                                       period_me2=self.args['macd2'],
                                       period_signal=self.args['macdsig'])
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        self.tema_open = bt.indicators.TripleExponentialMovingAverage(self.data.open, period=12)
        self.tema_close = bt.indicators.TripleExponentialMovingAverage(self.data.close, period=12)

        self.tcross = bt.indicators.CrossOver(self.tema_close, self.tema_open)

        self.flag_macd = 0
        self.flag_tema = 0

    def next(self):

        self.log('Close, %.2f' % self.data[0])
        if self.tema_open[0] is not None:

            if self.flag_tema == 1 and self.tcross == -1:
                self.flag_tema = 0

            if self.flag_macd == 1 and self.mcross == -1:
                self.flag_macd = 0

            if self.order:
                return  # pending order execution

            if not self.position:  # not in the market

                if self.flag_tema == 0 and self.tcross == 1:
                    self.flag_tema = 1

                if self.flag_macd == 0 and self.mcross == 1 and self.flag_tema == 1:
                    self.flag_macd = 1

                amount_to_invest = (self.args['order_pct'] * self.broker.cash)

                if self.flag_macd == 1 and self.flag_tema == 1:
                    self.size = math.floor(amount_to_invest / self.data.close)
                    self.order = self.buy(size=self.size)
                    print(" ")
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                    self.print_stats()

            elif self.position:
                if self.flag_tema != 1 or self.flag_macd != 1:
                    print(" ")
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    self.log('SELL CREATE (LONG), %.2f' % self.data[0])
                    self.close()
                    self.print_stats()
