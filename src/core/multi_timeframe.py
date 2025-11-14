"""Multi-timeframe analysis support for strategies"""

import backtrader as bt
import pandas as pd
import yfinance as yf
from typing import List, Dict, Any
import datetime


class MultiTimeframeData:
    """Helper class for managing multiple timeframe data feeds"""

    def __init__(self, ticker: str, start_date, end_date=None):
        """Initialize multi-timeframe data manager"""
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date if end_date else datetime.date.today()
        self.data_feeds = {}

    def add_timeframe(self, interval: str, name: str = None) -> bt.feeds.PandasData:
        """Add a timeframe data feed"""
        if name is None:
            name = interval

        data = self._download_data(interval)
        bt_feed = bt.feeds.PandasData(dataname=data, name=name)
        self.data_feeds[name] = bt_feed

        return bt_feed

    def _download_data(self, interval: str) -> pd.DataFrame:
        """Download data for specific timeframe"""
        if hasattr(self.start_date, 'strftime'):
            start_str = self.start_date.strftime('%Y-%m-%d')
        else:
            start_str = self.start_date

        if hasattr(self.end_date, 'strftime'):
            end_str = self.end_date.strftime('%Y-%m-%d')
        else:
            end_str = self.end_date

        data = yf.download(
            self.ticker,
            start=start_str,
            end=end_str,
            interval=interval,
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            raise ValueError(f"No data available for {self.ticker} at interval {interval}")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        return data

    def get_feed(self, name: str) -> bt.feeds.PandasData:
        """Get a specific data feed by name"""
        return self.data_feeds.get(name)


class MultiTimeframeStrategy(bt.Strategy):
    """Base strategy class with multi-timeframe support"""

    params = (
        ('timeframes', None),
    )

    def __init__(self, args):
        """Initialize strategy with multiple timeframes"""
        self.args = args
        self.timeframes = {}

        for i, data in enumerate(self.datas):
            if hasattr(data, '_name'):
                self.timeframes[data._name] = data
            else:
                self.timeframes[f'data{i}'] = data

        self.primary_data = self.datas[0]

    def get_timeframe_data(self, name: str):
        """Get data for specific timeframe"""
        return self.timeframes.get(name, self.primary_data)

    def is_data_synchronized(self, timeframe_name: str) -> bool:
        """Check if specific timeframe data is available at current bar"""
        data = self.get_timeframe_data(timeframe_name)

        if data is None:
            return False

        try:
            _ = data.close[0]
            return True
        except:
            return False


class MultiTimeframeRunner:
    """Runner for strategies using multiple timeframes"""

    def __init__(self, strategy_class, parameters: Dict[str, Any]):
        """Initialize multi-timeframe runner"""
        self.strategy_class = strategy_class
        self.parameters = parameters
        self.cerebro = bt.Cerebro()

    def add_timeframes(self, ticker: str, timeframes: List[str],
                      start_date, end_date=None) -> None:
        """Add multiple timeframe data feeds to cerebro"""
        mtf_data = MultiTimeframeData(ticker, start_date, end_date)

        for i, interval in enumerate(timeframes):
            feed = mtf_data.add_timeframe(interval, name=f"tf_{interval}")

            if i == 0:
                self.cerebro.adddata(feed, name=interval)
                self.primary_data = feed
            else:
                self.cerebro.adddata(feed, name=interval)

    def run(self, ticker: str, timeframes: List[str], start_date,
           end_date=None) -> Dict[str, Any]:
        """Run backtest with multiple timeframes"""
        self.add_timeframes(ticker, timeframes, start_date, end_date)

        self.cerebro.broker.set_cash(self.parameters.get('cash', 100000))

        self.cerebro.addstrategy(self.strategy_class, args=self.parameters)

        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        start_value = self.cerebro.broker.getvalue()
        results = self.cerebro.run()
        end_value = self.cerebro.broker.getvalue()

        strat = results[0]

        sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio')
        dd_analysis = strat.analyzers.drawdown.get_analysis()

        return {
            'ticker': ticker,
            'timeframes': timeframes,
            'start_value': start_value,
            'end_value': end_value,
            'pnl': end_value - start_value,
            'return_pct': ((end_value - start_value) / start_value) * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown': dd_analysis.get('max', {}).get('drawdown', 0),
            'trades': strat.trades if hasattr(strat, 'trades') else []
        }


def create_multi_timeframe_strategy(primary_interval: str, higher_interval: str):
    """Create a strategy that uses two timeframes (helper function)"""

    class DualTimeframeStrategy(MultiTimeframeStrategy):
        """Example dual timeframe strategy"""

        def __init__(self, args):
            super().__init__(args)

            self.primary = self.datas[0]
            self.higher = self.datas[1] if len(self.datas) > 1 else self.datas[0]

            self.primary_sma = bt.indicators.SMA(self.primary.close, period=20)
            self.higher_sma = bt.indicators.SMA(self.higher.close, period=50)

            self.order = None
            self.trades = []

        def next(self):
            """Strategy logic using both timeframes"""
            if self.order:
                return

            if not self.position:
                if self.primary.close[0] > self.primary_sma[0] and self.higher.close[0] > self.higher_sma[0]:
                    self.order = self.buy()

            else:
                if self.primary.close[0] < self.primary_sma[0]:
                    self.order = self.sell()

    return DualTimeframeStrategy
