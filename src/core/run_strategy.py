from typing import Dict, Optional, Type, List, Any
from datetime import date

import backtrader as bt
import pandas as pd
import yfinance as yf

from src.core.extractors.chart_data_extractor import ChartDataExtractor


class Run_strategy:
    """
    Lightweight orchestrator for running backtests.
    Delegates data extraction to specialized extractor classes.
    """
    def __init__(self, parameters: Dict[str, float], strategy: Type[bt.Strategy], data: Optional[bt.feeds.PandasData] = None):
        self.cerebro = bt.Cerebro()
        self.args = parameters
        self.data = data
        self.strategy = strategy
        self.chart_extractor = ChartDataExtractor()

    def add_analyzers(self, data: bt.feeds.PandasData) -> None:
        """Add Backtrader analyzers for performance metrics"""
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi',
                                timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
                                timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn',
                                timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addobserver(bt.observers.DrawDown)

    def add_data(self, cerebro: bt.Cerebro, ticker: str, start_date: date, interval: str, end_date: Optional[date] = None) -> bt.feeds.PandasData:
        """
        Fetch and add market data to Cerebro.

        Args:
            cerebro: Backtrader Cerebro instance
            ticker: Ticker symbol
            start_date: Start date for data
            interval: Data interval (1d, 1h, etc.)
            end_date: Optional end date

        Returns:
            Backtrader PandasData feed
        """
        start_str = start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)
        end_str = end_date.strftime('%Y-%m-%d') if end_date and hasattr(end_date, 'strftime') else None

        try:
            data = yf.download(ticker, start=start_str, end=end_str, interval=interval, progress=False, auto_adjust=False) \
                   if end_str else yf.download(ticker, start=start_str, interval=interval, progress=False, auto_adjust=False)

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

    def print_data(self) -> tuple:
        """
        Run the backtest and return results.

        Returns:
            Tuple of (results, start_value, end_value)
        """
        start_value = self.cerebro.broker.getvalue()
        results = self.cerebro.run()
        end_value = self.cerebro.broker.getvalue()
        return results, start_value, end_value

    def runstrat(self, ticker: str, start_date: date, interval: str, end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Execute a complete backtest.

        Args:
            ticker: Ticker symbol
            start_date: Backtest start date
            interval: Data interval
            end_date: Optional backtest end date

        Returns:
            Dictionary containing all backtest results and metrics
        """
        # Setup
        self.cerebro.broker.set_cash(self.args['cash'])

        if self.data is None:
            self.add_data(self.cerebro, ticker, start_date, interval, end_date)

        sizer_percent = self.args.get('position_size_pct', 95)
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer_percent)

        self.cerebro.addstrategy(self.strategy, args=self.args)
        self.add_analyzers(self.data)

        # Execute
        results, start_value, end_value = self.print_data()
        strat = results[0]

        # Extract basic metrics
        sharpe_ratio = strat.analyzers.mysharpe.get_analysis().get('sharperatio', None)
        pnl = end_value - start_value
        return_pct = (end_value / start_value - 1) * 100

        dd_analyzer = strat.analyzers.drawdown.get_analysis()
        max_drawdown = dd_analyzer.get('max', {}).get('drawdown', None)

        trade_analysis = strat.analyzers.tradeanalyzer.get_analysis()

        # Build equity curve
        time_returns = strat.analyzers.timereturn.get_analysis()
        equity_curve = self._build_equity_curve(time_returns, start_value)

        # Get trades from strategy
        trades = strat.trades if hasattr(strat, 'trades') else []

        # Calculate advanced metrics
        advanced_metrics = self._extract_advanced_metrics(
            trade_analysis, trades, start_value, end_value, equity_curve
        )

        total_trades = trade_analysis.get('total', {}).get('total', len(trades))

        # Extract chart data using the extractor
        chart_data = self.chart_extractor.extract(strat, self.data)

        return {
            'start_value': start_value,
            'end_value': end_value,
            'pnl': pnl,
            'return_pct': return_pct,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'trades': trades,
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date if end_date else 'today',
            'interval': interval,
            'advanced_metrics': advanced_metrics,
            'equity_curve': equity_curve,
            'chart_data': chart_data
        }

    def _build_equity_curve(self, time_returns: Dict, start_value: float) -> List[Dict[str, Any]]:
        """
        Build equity curve from time returns.

        Args:
            time_returns: Dictionary of date to return values
            start_value: Starting portfolio value

        Returns:
            List of equity curve points
        """
        equity_curve = []
        current_value = start_value

        for date_key, ret in time_returns.items():
            current_value = current_value * (1 + ret)
            equity_curve.append({
                'date': date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key),
                'value': current_value
            })

        if not equity_curve:
            equity_curve = [{'date': 'start', 'value': start_value}]

        return equity_curve

    def _extract_advanced_metrics(self, trade_analysis: Dict, trades: List, start_value: float,
                                   end_value: float, equity_curve: List) -> Dict[str, Any]:
        """
        Extract advanced performance metrics.

        Args:
            trade_analysis: Backtrader trade analysis results
            trades: List of trade dictionaries
            start_value: Starting portfolio value
            end_value: Ending portfolio value
            equity_curve: Equity curve data

        Returns:
            Dictionary of advanced metrics
        """
        total = trade_analysis.get('total', {})
        won = trade_analysis.get('won', {})
        lost = trade_analysis.get('lost', {})
        streak = trade_analysis.get('streak', {})

        total_trades = total.get('total', 0)
        win_rate = (won.get('total', 0) / total_trades * 100) if total_trades > 0 else 0.0

        gross_profit = won.get('pnl', {}).get('total', 0)
        gross_loss = abs(lost.get('pnl', {}).get('total', 0))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

        avg_win = won.get('pnl', {}).get('average', 0.0)
        avg_loss = abs(lost.get('pnl', {}).get('average', 0.0))
        payoff_ratio = (avg_win / avg_loss) if avg_loss > 0 else None

        max_consecutive_wins = streak.get('won', {}).get('longest', 0)
        max_consecutive_losses = streak.get('lost', {}).get('longest', 0)

        largest_win = won.get('pnl', {}).get('max', 0.0)
        largest_loss = lost.get('pnl', {}).get('max', 0.0)

        total_return = (end_value - start_value) / start_value if start_value > 0 else 0
        days_traded = len(equity_curve)
        years = days_traded / 365.25 if days_traded > 0 else 1
        annual_return = ((1 + total_return) ** (1 / years) - 1) * 100 if years > 0 else 0

        max_dd = self._calculate_max_drawdown_from_curve(equity_curve)
        calmar_ratio = (annual_return / abs(max_dd)) if max_dd and max_dd != 0 else None

        sortino_ratio = self._calculate_sortino_ratio(equity_curve)

        expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * avg_loss) if total_trades > 0 else 0.0

        return {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'payoff_ratio': payoff_ratio,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'avg_trade_duration': None,
            'recovery_periods': [],
            'expectancy': expectancy
        }

    def _calculate_max_drawdown_from_curve(self, equity_curve: List[Dict]) -> Optional[float]:
        """Calculate maximum drawdown from equity curve"""
        if not equity_curve:
            return None

        values = [point['value'] for point in equity_curve]
        peak = values[0]
        max_dd = 0

        for value in values:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)

        return max_dd if max_dd > 0 else None

    def _calculate_sortino_ratio(self, equity_curve: List[Dict], risk_free_rate: float = 0.0) -> Optional[float]:
        """Calculate Sortino ratio from equity curve"""
        if len(equity_curve) < 2:
            return None

        values = [point['value'] for point in equity_curve]
        returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values)) if values[i-1] > 0]

        if not returns:
            return None

        downside_returns = [r for r in returns if r < 0]
        if not downside_returns:
            return None

        import math
        avg_return = sum(returns) / len(returns)
        downside_dev = math.sqrt(sum(r ** 2 for r in downside_returns) / len(downside_returns))

        if downside_dev == 0:
            return None

        return (avg_return - risk_free_rate) / downside_dev
