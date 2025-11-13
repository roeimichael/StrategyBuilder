from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt


class Strategy_skeleton(bt.Strategy):
    def notify_order(self, order):
        if order.status == order.Completed:
            pass

        if not order.alive():
            self.order = None  # indicate no order is pending

    def __init__(self, args):
        self.args = args
        self.size = 0

    def print_trade(self, trade):
        if trade.isclosed:
            dt = self.data.datetime.date()

            print('---------------------------- TRADE ---------------------------------')
            print("1: Data Name:                            {}".format(trade.data._name))
            print("2: Bar Num:                              {}".format(len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(trade.ref))
            print('6: PnL:                                  {}'.format(round(trade.pnl, 2)))
            print('--------------------------------------------------------------------')

    def print_next(self):
        print('---------------------------- NEXT ----------------------------------')
        print("1: Data Name:                            {}".format(self.data._name))
        print("2: Bar Num:                              {}".format(len(self.data)))
        print("3: Current date:                         {}".format(self.data.datetime.datetime()))
        print('4: Open:                                 {}'.format(self.data.open[0]))
        print('5: High:                                 {}'.format(self.data.high[0]))
        print('6: Low:                                  {}'.format(self.data.low[0]))
        print('7: Close:                                {}'.format(self.data.close[0]))
        print('8: Volume:                               {}'.format(self.data.volume[0]))
        print('9: Position Size:                       {}'.format(self.position.size))
        print('--------------------------------------------------------------------')

    def print_stats(self):
        print(" ")
        print(self.broker.getposition(self.data))
        print(" ")
        print(f"The current total cash is: {self.broker.get_cash()}")
        print(f"The current value is: {self.broker.get_value()}")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(" ")

    def log(self, txt, dt=None):

        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def start(self):
        self.order = None  # sentinel to avoid operations on pending order
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def next(self):
        pass

    def stop(self):
        # calculate the actual returns
        print(" ")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:     {:.2f}%'.format(100.0 * self.roi))
