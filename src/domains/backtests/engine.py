from typing import Dict, Optional, Type, List, Any, Union
from datetime import date
import datetime
import backtrader as bt
import pandas as pd
from src.domains.market_data.manager import DataManager
from src.domains.backtests.extractors.chart_data_extractor import ChartDataExtractor
from src.shared.utils.performance_analyzer import PerformanceAnalyzer


class Run_strategy:
    def __init__(self, parameters: Dict[str, Union[int, float]], strategy: Type[bt.Strategy],
                 data: Optional[bt.feeds.PandasData] = None, data_manager: Optional[DataManager] = None):
        self.cerebro = bt.Cerebro()
        self.args = parameters
        self.data = data
        self.strategy = strategy
        self.chart_extractor = ChartDataExtractor()
        self.data_manager = data_manager or DataManager()

    def add_analyzers(self, data: bt.feeds.PandasData) -> None:
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi', timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
                                 timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn', timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addobserver(bt.observers.DrawDown)

    def _fetch_and_add_data(self, ticker: str, start_date: date, interval: str,
                            end_date: Optional[date] = None) -> bt.feeds.PandasData:
        if isinstance(start_date, datetime.date) and not isinstance(start_date, datetime.datetime):
            start_date_obj = start_date
        else:
            start_date_obj = start_date
        if end_date:
            if isinstance(end_date, datetime.date) and not isinstance(end_date, datetime.datetime):
                end_date_obj = end_date
            else:
                end_date_obj = end_date
        else:
            end_date_obj = datetime.date.today()
        try:
            data_df = self.data_manager.get_data(ticker=ticker, start_date=start_date_obj,
                                                 end_date=end_date_obj, interval=interval)
            if data_df.empty:
                raise ValueError(f"No data available for {ticker}")
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")
        data_feed = bt.feeds.PandasData(dataname=data_df)
        self.data = data_feed
        self.cerebro.adddata(data_feed)
        return data_feed

    def _execute_backtest(self) -> tuple:
        start_value = self.cerebro.broker.getvalue()
        results = self.cerebro.run()
        end_value = self.cerebro.broker.getvalue()
        return results, start_value, end_value

    def runstrat(self, ticker: str, start_date: date, interval: str, end_date: Optional[date] = None) -> Dict[str, Any]:
        self.cerebro.broker.set_cash(self.args['cash'])
        if self.data is None:
            self._fetch_and_add_data(ticker, start_date, interval, end_date)
        sizer_percent = self.args.get('position_size_pct', 95)
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer_percent)
        self.cerebro.addstrategy(self.strategy, args=self.args)
        self.add_analyzers(self.data)
        results, start_value, end_value = self._execute_backtest()
        strat = results[0]
        sharpe_ratio = strat.analyzers.mysharpe.get_analysis().get('sharperatio', None)
        pnl = end_value - start_value
        return_pct = (end_value / start_value - 1) * 100
        dd_analyzer = strat.analyzers.drawdown.get_analysis()
        max_drawdown = dd_analyzer.get('max', {}).get('drawdown', None)
        trade_analysis = strat.analyzers.tradeanalyzer.get_analysis()
        total_trades = trade_analysis.get('total', {}).get('total', 0)
        trades = strat.trades if hasattr(strat, 'trades') else []
        time_returns = strat.analyzers.timereturn.get_analysis()
        equity_curve_list = self._build_equity_curve_list(time_returns, start_value)
        advanced_metrics = self._calculate_metrics_with_analyzer(trades, start_value, end_value, equity_curve_list)
        chart_data = self.chart_extractor.extract(strat, self.data)
        return {
            'start_value': start_value, 'end_value': end_value, 'pnl': pnl, 'return_pct': return_pct,
            'sharpe_ratio': sharpe_ratio, 'max_drawdown': max_drawdown,
            'total_trades': total_trades if total_trades > 0 else len(trades), 'trades': trades,
            'ticker': ticker, 'start_date': start_date, 'end_date': end_date if end_date else 'today',
            'interval': interval, 'advanced_metrics': advanced_metrics, 'equity_curve': equity_curve_list,
            'chart_data': chart_data
        }

    def _build_equity_curve_list(self, time_returns: Dict, start_value: float) -> List[Dict[str, Any]]:
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

    def _calculate_metrics_with_analyzer(self, trades: List[Dict[str, Any]], start_value: float,
                                         end_value: float, equity_curve_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not trades:
            return {
                'win_rate': 0.0, 'profit_factor': None, 'payoff_ratio': None, 'calmar_ratio': None,
                'sortino_ratio': None, 'max_consecutive_wins': 0, 'max_consecutive_losses': 0,
                'avg_win': 0.0, 'avg_loss': 0.0, 'largest_win': 0.0, 'largest_loss': 0.0,
                'avg_trade_duration': None, 'recovery_periods': [], 'expectancy': 0.0
            }
        equity_values = [start_value] + [point['value'] for point in equity_curve_list]
        equity_series = pd.Series(equity_values)
        analyzer = PerformanceAnalyzer(trades=trades, start_value=start_value,
                                       end_value=end_value, equity_curve=equity_series)
        return analyzer.calculate_all_metrics()
