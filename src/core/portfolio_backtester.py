"""Portfolio-level backtesting for multi-asset strategies"""

import datetime
import pandas as pd
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.data_manager import DataManager
from core.run_strategy import Run_strategy


class PortfolioBacktester:
    """Backtest strategies across multiple assets simultaneously"""

    def __init__(self, data_manager: DataManager):
        """Initialize portfolio backtester"""
        self.data_manager = data_manager

    def run_portfolio_backtest(self, tickers: List[str], strategy_class,
                               parameters: Dict[str, Any], start_date: datetime.date,
                               end_date: datetime.date = None, interval: str = '1d',
                               max_workers: int = 5) -> Dict[str, Any]:
        """Run backtest across multiple tickers in parallel"""
        if end_date is None:
            end_date = datetime.date.today()

        individual_results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(
                    self._run_single_backtest,
                    ticker,
                    strategy_class,
                    parameters,
                    start_date,
                    end_date,
                    interval
                ): ticker for ticker in tickers
            }

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    individual_results[ticker] = result
                except Exception as e:
                    individual_results[ticker] = {
                        'error': str(e),
                        'success': False
                    }

        portfolio_metrics = self._calculate_portfolio_metrics(individual_results, parameters['cash'])

        return {
            'tickers': tickers,
            'strategy': strategy_class.__name__,
            'start_date': start_date,
            'end_date': end_date,
            'interval': interval,
            'individual_results': individual_results,
            'portfolio_metrics': portfolio_metrics
        }

    def _run_single_backtest(self, ticker: str, strategy_class,
                            parameters: Dict[str, Any], start_date: datetime.date,
                            end_date: datetime.date, interval: str) -> Dict[str, Any]:
        """Run backtest for a single ticker"""
        data = self.data_manager.get_data(ticker, start_date, end_date, interval)

        if data.empty:
            raise ValueError(f"No data available for {ticker}")

        runner = Run_strategy(parameters, strategy_class)
        results = runner.runstrat(ticker, start_date, interval, end_date)

        results['success'] = True
        return results

    def _calculate_portfolio_metrics(self, individual_results: Dict[str, Dict[str, Any]],
                                    total_capital: float) -> Dict[str, Any]:
        """Calculate portfolio-level metrics"""
        successful_results = {
            ticker: result for ticker, result in individual_results.items()
            if result.get('success', False)
        }

        if not successful_results:
            return {
                'total_return': 0,
                'total_pnl': 0,
                'num_successful': 0,
                'num_failed': len(individual_results)
            }

        capital_per_asset = total_capital / len(successful_results)

        total_pnl = 0
        total_trades = 0
        weighted_sharpe_sum = 0
        max_drawdown_list = []

        for ticker, result in successful_results.items():
            pnl = result.get('pnl', 0)
            total_pnl += pnl

            total_trades += result.get('total_trades', 0)

            if result.get('sharpe_ratio'):
                weighted_sharpe_sum += result['sharpe_ratio']

            if result.get('max_drawdown'):
                max_drawdown_list.append(result['max_drawdown'])

        total_return_pct = (total_pnl / total_capital) * 100 if total_capital > 0 else 0

        avg_sharpe = weighted_sharpe_sum / len(successful_results) if successful_results else None

        max_drawdown = max(max_drawdown_list) if max_drawdown_list else None

        return {
            'total_capital': total_capital,
            'total_pnl': total_pnl,
            'total_return': total_return_pct,
            'total_trades': total_trades,
            'avg_sharpe_ratio': avg_sharpe,
            'max_portfolio_drawdown': max_drawdown,
            'num_assets': len(successful_results),
            'num_successful': len(successful_results),
            'num_failed': len(individual_results) - len(successful_results),
            'capital_per_asset': capital_per_asset,
            'individual_returns': {
                ticker: result.get('return_pct', 0)
                for ticker, result in successful_results.items()
            }
        }

    def run_equal_weight_portfolio(self, tickers: List[str], strategy_class,
                                   parameters: Dict[str, Any], start_date: datetime.date,
                                   end_date: datetime.date = None,
                                   interval: str = '1d') -> Dict[str, Any]:
        """Run backtest with equal weight allocation across assets"""
        total_capital = parameters.get('cash', 100000)
        capital_per_asset = total_capital / len(tickers)

        asset_parameters = parameters.copy()
        asset_parameters['cash'] = capital_per_asset

        return self.run_portfolio_backtest(
            tickers,
            strategy_class,
            asset_parameters,
            start_date,
            end_date,
            interval
        )

    def get_correlation_matrix(self, tickers: List[str], start_date: datetime.date,
                               end_date: datetime.date = None,
                               interval: str = '1d') -> pd.DataFrame:
        """Calculate correlation matrix for portfolio assets"""
        if end_date is None:
            end_date = datetime.date.today()

        returns_data = {}

        for ticker in tickers:
            try:
                data = self.data_manager.get_data(ticker, start_date, end_date, interval)
                returns = data['Close'].pct_change().dropna()
                returns_data[ticker] = returns
            except Exception:
                continue

        if not returns_data:
            return pd.DataFrame()

        returns_df = pd.DataFrame(returns_data)

        correlation_matrix = returns_df.corr()

        return correlation_matrix
