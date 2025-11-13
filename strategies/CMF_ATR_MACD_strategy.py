from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math
import backtrader as bt
from cmf_indicator import CMF
from strategy_skeleton import Strategy_skeleton


class MACD_CMF_ATR_Strategy(Strategy_skeleton):

    def __init__(self, args):
        super(MACD_CMF_ATR_Strategy, self).__init__(args)
        self.stop_loss_long = 0
        self.take_profit_long = 0
        self.stop_loss_short = 0
        self.take_profit_short = 0
        self.is_long, self.is_short = 0, 0
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.args.macd1,
                                       period_me2=self.args.macd2,
                                       period_signal=self.args.macdsig)
        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        self.mcross_short = bt.indicators.CrossOver(self.macd.signal, self.macd.macd)

        self.atr = bt.indicators.ATR(self.data, period=self.args.atrperiod)

        self.cmf = CMF(self.data)

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market

            amount_to_invest = (self.args.order_pct * self.broker.cash)

            if self.macd.macd[0] > 0 and self.macd.signal[0] > 0:  # testing long
                if self.mcross[0] == 1.0 and self.cmf[0] > 0:
                    self.size = math.floor(amount_to_invest / self.data.close)
                    self.buy(size=self.size)
                    self.is_long = 1
                    print(" ")
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                    pdist = self.atr[0] * self.args.atrdist
                    self.stop_loss_long = self.data.close[0] - pdist
                    self.take_profit_long = self.data.close[0] + (2 * pdist)
                    self.print_stats()

            elif self.macd.macd[0] < 0 and self.macd.signal[0] < 0:  # testing short
                if self.mcross_short == 1.0 and self.cmf[0] < 0:
                    self.size = math.floor(amount_to_invest / self.data.close)
                    self.sell(size=self.size)
                    self.is_short = 1
                    print(" ")
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
                    pdist = self.atr[0] * self.args.atrdist
                    self.stop_loss_short = self.data.close[0] + pdist
                    self.take_profit_short = self.data.close[0] - (2 * pdist)
                    self.print_stats()


        else:  # currently holding a position
            pclose = self.data.close[0]
            stop_loss_long = self.stop_loss_long
            take_profit_long = self.take_profit_long
            stop_loss_short = self.stop_loss_short
            take_profit_short = self.take_profit_short

            if self.is_long == 1 and pclose >= take_profit_long:
                # indicate that we are no longer in long position
                self.is_long = 0
                print(" ")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                self.log('SELL CREATE (LONG), %.2f' % self.data[0])
                self.close()
                self.print_stats()

            if self.is_long == 1 and pclose <= stop_loss_long:
                # indicate that we are no longer in long position
                self.is_long = 0
                print(" ")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                self.log('STOP CREATE (LONG), %.2f ' % self.data[0])
                self.close()
                self.print_stats()

            if self.is_short == 1 and pclose <= take_profit_short:
                # indicate that we are no longer in short position
                self.is_short = 0
                print(" ")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                self.log('BUY CREATE (SHORT), %.2f' % self.data[0])
                self.close()
                self.print_stats()

            if self.is_short == 1 and pclose >= stop_loss_short:
                # indicate that we are no longer in short position
                self.is_short = 0
                print(" ")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                self.log('STOP CREATE (SHORT), %.2f ' % self.data[0])
                self.close()
                self.print_stats()
