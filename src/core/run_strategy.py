"""Backtrader strategy execution engine"""

import backtrader as bt
import pandas as pd
import yfinance as yf
from utils.performance_analyzer import PerformanceAnalyzer


class Run_strategy:
    """Executes backtrader strategies and returns results"""

    def __init__(self, parameters, strategy, data=None):
        """Initialize strategy runner with parameters and strategy class"""
        self.cerebro = bt.Cerebro()
        self.args = parameters
        self.data = data
        self.strategy = strategy

    def add_analyzers(self, data):
        """Add performance analyzers to cerebro"""
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi',
                                timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
                                timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
        self.cerebro.addobserver(bt.observers.DrawDown)

    def add_data(self, cerebro, ticker, start_date, interval, end_date=None):
        """Download and add market data to cerebro"""
        if hasattr(start_date, 'strftime'):
            start_date = start_date.strftime('%Y-%m-%d')
        if end_date and hasattr(end_date, 'strftime'):
            end_date = end_date.strftime('%Y-%m-%d')

        try:
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False, auto_adjust=False) \
                   if end_date else yf.download(ticker, start=start_date, interval=interval, progress=False, auto_adjust=False)

            if data.empty:
                raise ValueError(f"No data available for {ticker}")

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            if len(data.columns) > 0 and isinstance(data.columns[0], tuple):
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

        except Exception as e:
            raise ValueError(f"Failed to download data for {ticker}: {str(e)}")

        data = bt.feeds.PandasData(dataname=data)
        self.data = data
        cerebro.adddata(data)
        return data

    def print_data(self):
        """Run strategy and print results"""
        start_value = self.cerebro.broker.getvalue()
        print(f'Starting Portfolio Value: ${start_value:.2f}')
        results = self.cerebro.run()
        end_value = self.cerebro.broker.getvalue()
        print(f'Final Portfolio Value: ${end_value:.2f}')
        percentage = (end_value / start_value - 1) * 100
        print(f"Return: {percentage:.2f}%")
        print("=" * 70)
        return results, start_value, end_value

    def runstrat(self, ticker, start_date, interval, end_date=None):
        """Execute strategy and return comprehensive results"""
        self.cerebro.broker.set_cash(self.args['cash'])
        if self.data is None:
            self.add_data(self.cerebro, ticker, start_date, interval, end_date)

        self.cerebro.addstrategy(self.strategy, args=self.args)
        self.add_analyzers(self.data)
        results, start_value, end_value = self.print_data()

        strat = results[0]
        sharpe_ratio = strat.analyzers.mysharpe.get_analysis().get('sharperatio', None)
        pnl = end_value - start_value
        return_pct = (end_value / start_value - 1) * 100

        try:
            max_drawdown = strat.observers.drawdown._maxdrawdown or 0
        except:
            max_drawdown = None

        trades = strat.trades if hasattr(strat, 'trades') else []

        equity_curve = PerformanceAnalyzer.create_equity_curve(trades, start_value)
        analyzer = PerformanceAnalyzer(trades, start_value, end_value, equity_curve)
        advanced_metrics = analyzer.calculate_all_metrics()

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
            'advanced_metrics': advanced_metrics,
            'equity_curve': equity_curve
        }
