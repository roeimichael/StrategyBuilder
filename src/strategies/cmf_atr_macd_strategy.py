"""MACD + CMF + ATR combined strategy with stop loss and take profit"""

import math

import backtrader as bt

from src.indicators.cmf_indicator import CMF
from ..core.strategy_skeleton import Strategy_skeleton


class MACD_CMF_ATR_Strategy(Strategy_skeleton):

    def __init__(self, args):
        """Initialize MACD, CMF, and ATR indicators"""
        super(MACD_CMF_ATR_Strategy, self).__init__(args)
        self.stop_loss_long = 0
        self.take_profit_long = 0
        self.stop_loss_short = 0
        self.take_profit_short = 0
        self.is_long, self.is_short = 0, 0
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.args['macd1'],
                                       period_me2=self.args['macd2'],
                                       period_signal=self.args['macdsig'])
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.mcross_short = bt.indicators.CrossOver(self.macd.signal, self.macd.macd)
        self.atr = bt.indicators.ATR(self.data, period=self.args['atrperiod'])
        self.cmf = CMF(self.data)

    def next(self):
        """Execute strategy logic on each bar"""
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            amount_to_invest = (self.args['order_pct'] * self.broker.cash)

            if self.macd.macd[0] > 0 and self.macd.signal[0] > 0:
                if self.mcross[0] == 1.0 and self.cmf[0] > 0:
                    self.size = math.floor(amount_to_invest / self.data.close)
                    self.buy(size=self.size)
                    self.is_long = 1
                    self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
                    pdist = self.atr[0] * self.args['atrdist']
                    self.stop_loss_long = self.data.close[0] - pdist
                    self.take_profit_long = self.data.close[0] + (2 * pdist)

            elif self.macd.macd[0] < 0 and self.macd.signal[0] < 0:
                if self.mcross_short == 1.0 and self.cmf[0] < 0:
                    self.size = math.floor(amount_to_invest / self.data.close)
                    self.sell(size=self.size)
                    self.is_short = 1
                    self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
                    pdist = self.atr[0] * self.args['atrdist']
                    self.stop_loss_short = self.data.close[0] + pdist
                    self.take_profit_short = self.data.close[0] - (2 * pdist)
        else:
            pclose = self.data.close[0]
            stop_loss_long = self.stop_loss_long
            take_profit_long = self.take_profit_long
            stop_loss_short = self.stop_loss_short
            take_profit_short = self.take_profit_short

            if self.is_long == 1 and pclose >= take_profit_long:
                self.is_long = 0
                self.log('SELL CREATE (LONG), %.2f' % self.data[0])
                self.close()

            if self.is_long == 1 and pclose <= stop_loss_long:
                self.is_long = 0
                self.log('STOP CREATE (LONG), %.2f ' % self.data[0])
                self.close()

            if self.is_short == 1 and pclose <= take_profit_short:
                self.is_short = 0
                self.log('BUY CREATE (SHORT), %.2f' % self.data[0])
                self.close()

            if self.is_short == 1 and pclose >= stop_loss_short:
                self.is_short = 0
                self.log('STOP CREATE (SHORT), %.2f ' % self.data[0])
                self.close()
