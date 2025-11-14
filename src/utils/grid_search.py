"""Grid Search Utility for Strategy Parameter Optimization"""

import itertools
from collections import defaultdict
from typing import List, Dict, Any

import pandas as pd


class GridSearchOptimizer:
    """Performs grid search optimization on strategy parameters"""

    def __init__(self, strategy_class, base_parameters: Dict[str, Any]):
        """Initialize grid search optimizer with strategy class and base parameters"""
        self.strategy_class = strategy_class
        self.base_parameters = base_parameters.copy()
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
                       progress_callback=None) -> List[Dict[str, Any]]:
        """Run grid search over parameter combinations"""
        from core.run_strategy import Run_strategy

        param_grid = self.generate_parameter_grid(param_ranges)
        total_combinations = len(param_grid)
        self.results = []

        for idx, params in enumerate(param_grid):
            if progress_callback:
                progress_callback(idx + 1, total_combinations, params)

            try:
                runner = Run_strategy(params, self.strategy_class)
                results = runner.runstrat(ticker, start_date, interval, end_date)

                if results:
                    result_entry = {
                        'parameters': params.copy(),
                        'return_pct': results['return_pct'],
                        'sharpe_ratio': results.get('sharpe_ratio'),
                        'max_drawdown': results.get('max_drawdown'),
                        'total_trades': results['total_trades'],
                        'start_value': results['start_value'],
                        'end_value': results['end_value'],
                        'pnl': results['pnl'],
                        'trades': results.get('trades', []),
                        'ticker': ticker,
                        'start_date': start_date,
                        'end_date': end_date,
                        'interval': interval
                    }

                    trades = results.get('trades', [])
                    if trades:
                        winning_trades = [t for t in trades if t['pnl'] > 0]
                        result_entry['win_rate'] = (len(winning_trades) / len(trades)) * 100
                        result_entry['avg_pnl'] = sum(t['pnl'] for t in trades) / len(trades)
                    else:
                        result_entry['win_rate'] = 0
                        result_entry['avg_pnl'] = 0

                    self.results.append(result_entry)

            except Exception as e:
                if progress_callback:
                    print(f"Failed: {str(e)[:50]}")
                continue

        self.results.sort(key=lambda x: x['return_pct'], reverse=True)
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
                'Return %': result['return_pct'],
                'Sharpe Ratio': result.get('sharpe_ratio', 0),
                'Max Drawdown %': result.get('max_drawdown', 0),
                'Total Trades': result['total_trades'],
                'Win Rate %': result.get('win_rate', 0),
                'Avg P&L': result.get('avg_pnl', 0),
                'Final Value': result['end_value'],
            }

            for param_name, param_value in result['parameters'].items():
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
            param_value = result['parameters'].get(param_name)
            if param_value is not None:
                param_returns[param_value].append(result['return_pct'])

        sensitivity = {}
        for value, returns in param_returns.items():
            sensitivity[value] = sum(returns) / len(returns)

        return sensitivity


def create_parameter_ranges(strategy_name: str, custom_ranges: Dict[str, List] = None) -> Dict[str, List]:
    """Create default parameter ranges for common strategies"""
    default_ranges = {
        'Bollinger Bands': {
            'period': [10, 15, 20, 25, 30],
            'devfactor': [1.5, 2.0, 2.5, 3.0]
        },
        'TEMA + MACD': {
            'macd1': [8, 12, 16],
            'macd2': [20, 26, 32],
            'macdsig': [7, 9, 11]
        },
        'ADX Adaptive': {
            'atrperiod': [10, 14, 18],
            'atrdist': [1.5, 2.0, 2.5]
        }
    }

    if custom_ranges:
        return custom_ranges

    return default_ranges.get(strategy_name, {})
