from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import yfinance as yf


# import pyfolio as pf

class Run_strategy:

    def __init__(self, parameters, strategy, data=None):
        self.cerebro = bt.Cerebro()
        self.args = parameters
        self.data = data
        self.strategy = strategy

    def add_analyzers(self, data):
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi',
                                 timeframe=bt.TimeFrame.NoTimeFrame)

        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
                                 timeframe=bt.TimeFrame.NoTimeFrame)

        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)

        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
        self.cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol

    def add_data(self, cerebro, ticker, start_date, interval, end_date=None):
        # Convert date objects to strings if necessary
        if hasattr(start_date, 'strftime'):
            start_date = start_date.strftime('%Y-%m-%d')
        if end_date and hasattr(end_date, 'strftime'):
            end_date = end_date.strftime('%Y-%m-%d')

        # Download data with proper error handling
        try:
            if end_date:
                data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
            else:
                data = yf.download(ticker, start=start_date, interval=interval, progress=False)

            if data.empty:
                raise ValueError(f"No data available for {ticker}")

            # Fix for yfinance 0.2.31+ which returns MultiIndex columns
            # Flatten MultiIndex columns to simple string names for backtrader compatibility
            import pandas as pd
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # Ensure all column names are strings (handle any remaining tuples)
            if len(data.columns) > 0 and isinstance(data.columns[0], tuple):
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

        except Exception as e:
            raise ValueError(f"Failed to download data for {ticker}: {str(e)}")

        data = bt.feeds.PandasData(dataname=data)
        self.data = data
        cerebro.adddata(data)
        return data

    def print_data(self):
        start_value = self.cerebro.broker.getvalue()
        print('Starting Portfolio Value: %.2f' % start_value)
        results = self.cerebro.run()
        end_value = self.cerebro.broker.getvalue()
        print('Final Portfolio Value: %.2f' % end_value)
        percentage = (end_value / start_value - 1) * 100
        print(f"Percentage lost/profited in time period: {round(percentage, 3)}%")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return results, start_value, end_value

    def runstrat(self, ticker, start_date, interval, end_date=None):
        self.cerebro.broker.set_cash(self.args['cash'])
        if self.data is None:
            market_data = self.add_data(self.cerebro, ticker, start_date, interval, end_date)
        self.cerebro.addstrategy(self.strategy, args=self.args)
        self.add_analyzers(self.data)
        results, start_value, end_value = self.print_data()

        # Extract detailed analytics
        strat = results[0]

        # Get analyzers
        sharpe_ratio = strat.analyzers.mysharpe.get_analysis().get('sharperatio', None)

        # Calculate returns
        pnl = end_value - start_value
        return_pct = (end_value / start_value - 1) * 100

        # Get drawdown info
        try:
            dd_info = strat.observers.drawdown._maxdrawdown
            max_drawdown = dd_info if dd_info else 0
        except:
            max_drawdown = None

        # Get trade details from strategy
        trades = []
        if hasattr(strat, 'trades'):
            trades = strat.trades

        # Return comprehensive results dictionary
        return {
            'start_value': start_value,
            'end_value': end_value,
            'pnl': pnl,
            'return_pct': return_pct,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'trades': trades,
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date if end_date else 'today',
            'interval': interval,
        }
        # self.cerebro.plot(style='candlestick')

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
