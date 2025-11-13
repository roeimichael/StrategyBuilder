from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import yfinance as yf
# import pyfolio as pf
import pandas as pd


class Run_strategy:

    def __init__(self, strategy):
        self.cerebro = bt.Cerebro()
        # self.args = parameters
        self.data = None
        self.data1 = None
        self.data2 = None
        self.data_ratio = None
        self.strategy = strategy

    def add_analyzers(self, data):
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi',
                                 timeframe=bt.TimeFrame.NoTimeFrame)

        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
                                 timeframe=bt.TimeFrame.NoTimeFrame)

        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)

        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
        self.cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol

    def add_data(self, cerebro, ticker, start_date, interval):
        data = yf.download(ticker, start=start_date, interval=interval)
        data = bt.feeds.PandasData(dataname=data)
        self.data = data
        cerebro.adddata(data)

    def add_pair_data(self, cerebro, ticker_x, ticker_y, start_date, interval):
        data1 = yf.download(ticker_x, start=start_date, interval=interval)
        data1 = bt.feeds.PandasData(dataname=data1)
        data2 = yf.download(ticker_y, start=start_date, interval=interval)
        data2 = bt.feeds.PandasData(dataname=data2)
        cerebro.adddata(data1)
        cerebro.adddata(data2)
        self.data1 = data1
        self.data2 = data2
        print(self.data1)
        print(self.data2)
        self.data_ratio = self.data1.div(self.data2)
        print(self.data_ratio)

    def print_data(self):
        start_value = self.cerebro.broker.getvalue()
        print('Starting Portfolio Value: %.2f' % start_value)
        self.cerebro.run()
        end_value = self.cerebro.broker.getvalue()
        print('Final Portfolio Value: %.2f' % end_value)
        percentage = (end_value / start_value - 1) * 100
        print(f"Percentage lost/profited in time period{round(percentage, 3)}%")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    def runstrat(self, ticker_x, ticker_y, start_date, interval):
        self.cerebro.broker.set_cash(10000)
        if self.strategy.__str__() == 'pairs_bollinger':
            self.add_pair_data(self.cerebro, ticker_x, ticker_y, start_date, interval)
        else:
            self.add_data(self.cerebro, ticker_x, start_date, interval)
        self.cerebro.addstrategy(self.strategy)  # , args=self.args
        self.add_analyzers(self.data_ratio)
        self.print_data()
        self.cerebro.plot(style='candlestick')

        # self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        #
        # results = self.cerebro.run()
        # strat = results[0]
        #
        # pyfoliozer = strat.analyzers.getbyname('pyfolio')
        #
        # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
        # pf.create_full_tear_sheet(
        #     returns,
        #     positions=positions,
        #     transactions=transactions,
        #
        #     live_start_date='2021-09-01',
        #     round_trips=True)
