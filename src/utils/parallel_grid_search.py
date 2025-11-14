"""Parallel Grid Search for massive speed improvements in parameter optimization"""

import itertools
import multiprocessing as mp
from typing import List, Dict, Any, Optional, Callable
from functools import partial
import pandas as pd
from collections import defaultdict


class ParallelGridSearch:
    """Parallel grid search optimizer using multiprocessing"""

    def __init__(self, strategy_class, base_parameters: Dict[str, Any],
                 n_jobs: int = -1):
        """
        Initialize parallel grid search

        Args:
            strategy_class: Strategy class to optimize
            base_parameters: Base parameters for strategy
            n_jobs: Number of parallel jobs (-1 = all CPU cores)
        """
        self.strategy_class = strategy_class
        self.base_parameters = base_parameters.copy()
        self.n_jobs = mp.cpu_count() if n_jobs == -1 else n_jobs
        self.results = []

    def generate_parameter_grid(self, param_ranges: Dict[str, List]) -> List[Dict[str, Any]]:
        """Generate all parameter combinations from ranges"""
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        combinations = list(itertools.product(*param_values))

        param_grid = []
        for combo in combinations:
            params = self.base_parameters.copy()
            for name, value in zip(param_names, combo):
                params[name] = value
            param_grid.append(params)

        return param_grid

    def run_grid_search(self, ticker: str, start_date, end_date, interval: str,
                       param_ranges: Dict[str, List],
                       use_vectorized: bool = False,
                       progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Run parallel grid search over parameter combinations

        Args:
            ticker: Stock ticker symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            interval: Data interval
            param_ranges: Dictionary of parameter ranges
            use_vectorized: Use vectorized backtesting if True
            progress_callback: Optional callback function for progress updates

        Returns:
            List of result dictionaries sorted by return_pct
        """
        param_grid = self.generate_parameter_grid(param_ranges)
        total_combinations = len(param_grid)

        print(f"Running parallel grid search with {total_combinations} combinations on {self.n_jobs} cores...")

        # Create partial function with fixed arguments
        worker_func = partial(
            _run_single_backtest,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            strategy_class=self.strategy_class,
            use_vectorized=use_vectorized
        )

        # Run parallel backtests
        with mp.Pool(processes=self.n_jobs) as pool:
            self.results = pool.map(worker_func, param_grid)

        # Filter out failed results
        self.results = [r for r in self.results if r is not None and 'error' not in r]

        # Sort by return percentage
        self.results.sort(key=lambda x: x.get('return_pct', -float('inf')), reverse=True)

        if progress_callback:
            progress_callback(total_combinations, total_combinations, None)

        return self.results

    def get_top_results(self, n: int = 5, sort_by: str = 'return_pct') -> List[Dict[str, Any]]:
        """Get top N results sorted by specified metric"""
        if not self.results:
            return []

        valid_results = [r for r in self.results if r.get(sort_by) is not None]
        sorted_results = sorted(valid_results, key=lambda x: x[sort_by], reverse=True)
        return sorted_results[:n]

    def create_results_dataframe(self) -> pd.DataFrame:
        """Create DataFrame of all results for analysis"""
        if not self.results:
            return pd.DataFrame()

        data = []
        for result in self.results:
            row = {
                'Return %': result.get('return_pct', 0),
                'Sharpe Ratio': result.get('sharpe_ratio', 0),
                'Max Drawdown %': result.get('max_drawdown', 0),
                'Total Trades': result.get('total_trades', 0),
                'Win Rate %': result.get('win_rate', 0),
                'Final Value': result.get('end_value', 0),
            }

            # Add parameters
            params = result.get('parameters', {})
            for param_name, param_value in params.items():
                if param_name not in ['cash', 'order_pct', 'macd1', 'macd2', 'macdsig', 'atrperiod', 'atrdist']:
                    row[param_name] = param_value

            data.append(row)

        return pd.DataFrame(data)

    def get_parameter_sensitivity(self, param_name: str) -> Dict[Any, float]:
        """Analyze sensitivity of results to a specific parameter"""
        if not self.results:
            return {}

        param_returns = defaultdict(list)

        for result in self.results:
            params = result.get('parameters', {})
            param_value = params.get(param_name)
            if param_value is not None:
                param_returns[param_value].append(result.get('return_pct', 0))

        sensitivity = {}
        for value, returns in param_returns.items():
            sensitivity[value] = sum(returns) / len(returns) if returns else 0

        return sensitivity

    def get_best_parameters(self, metric: str = 'return_pct') -> Dict[str, Any]:
        """Get parameters that produced best results for a given metric"""
        if not self.results:
            return {}

        best_result = max(self.results, key=lambda x: x.get(metric, -float('inf')))
        return best_result.get('parameters', {})


def _run_single_backtest(params: Dict[str, Any], ticker: str, start_date, end_date,
                        interval: str, strategy_class, use_vectorized: bool = False) -> Optional[Dict[str, Any]]:
    """
    Worker function to run a single backtest (for multiprocessing)

    Args:
        params: Strategy parameters
        ticker: Stock ticker
        start_date: Start date
        end_date: End date
        interval: Data interval
        strategy_class: Strategy class
        use_vectorized: Use vectorized backtesting

    Returns:
        Result dictionary or None if failed
    """
    try:
        if use_vectorized:
            from core.vectorized_backtest import run_vectorized_backtest
            results = run_vectorized_backtest(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                strategy_class=strategy_class,
                params=params
            )
        else:
            from core.run_strategy import Run_strategy
            runner = Run_strategy(params, strategy_class)
            results = runner.runstrat(ticker, start_date, interval, end_date)

        if results:
            result_entry = {
                'parameters': params.copy(),
                'return_pct': results.get('return_pct', 0),
                'sharpe_ratio': results.get('sharpe_ratio'),
                'max_drawdown': results.get('max_drawdown'),
                'total_trades': results.get('total_trades', 0),
                'start_value': results.get('start_value', 0),
                'end_value': results.get('end_value', 0),
                'pnl': results.get('pnl', 0),
                'ticker': ticker,
                'start_date': start_date,
                'end_date': end_date,
                'interval': interval
            }

            # Calculate win rate if trades available
            trades = results.get('trades', [])
            if trades:
                winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
                result_entry['win_rate'] = (len(winning_trades) / len(trades)) * 100
            else:
                result_entry['win_rate'] = 0

            return result_entry

    except Exception as e:
        return {'error': str(e), 'parameters': params}

    return None


def compare_serial_vs_parallel(ticker: str, start_date, end_date, interval: str,
                               strategy_class, base_params: Dict[str, Any],
                               param_ranges: Dict[str, List]) -> Dict[str, Any]:
    """
    Compare performance of serial vs parallel grid search

    Returns:
        Dict with timing comparison
    """
    import time

    # Serial grid search
    from utils.grid_search import GridSearchOptimizer

    serial_optimizer = GridSearchOptimizer(strategy_class, base_params)
    start_time = time.time()
    serial_results = serial_optimizer.run_grid_search(
        ticker, start_date, end_date, interval, param_ranges
    )
    serial_time = time.time() - start_time

    # Parallel grid search
    parallel_optimizer = ParallelGridSearch(strategy_class, base_params)
    start_time = time.time()
    parallel_results = parallel_optimizer.run_grid_search(
        ticker, start_date, end_date, interval, param_ranges
    )
    parallel_time = time.time() - start_time

    speedup = serial_time / parallel_time if parallel_time > 0 else 0

    return {
        'serial_time': serial_time,
        'parallel_time': parallel_time,
        'speedup': speedup,
        'serial_results_count': len(serial_results),
        'parallel_results_count': len(parallel_results),
        'cores_used': parallel_optimizer.n_jobs
    }
