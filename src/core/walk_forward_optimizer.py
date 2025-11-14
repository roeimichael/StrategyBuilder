"""Walk-forward optimization to prevent overfitting"""

import datetime
import pandas as pd
from typing import List, Dict, Any, Tuple
from dateutil.relativedelta import relativedelta

from core.data_manager import DataManager
from core.run_strategy import Run_strategy


class WalkForwardOptimizer:
    """Implements walk-forward analysis for strategy validation"""

    def __init__(self, data_manager: DataManager, train_months: int = 12,
                 test_months: int = 3, step_months: int = 3):
        """Initialize walk-forward optimizer"""
        self.data_manager = data_manager
        self.train_months = train_months
        self.test_months = test_months
        self.step_months = step_months

    def split_periods(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """Split date range into training and testing periods"""
        periods = []
        current_start = start_date

        while current_start < end_date:
            train_end = current_start + relativedelta(months=self.train_months)

            if train_end >= end_date:
                break

            test_start = train_end
            test_end = test_start + relativedelta(months=self.test_months)

            if test_end > end_date:
                test_end = end_date

            if test_end <= test_start:
                break

            periods.append({
                'train_start': current_start,
                'train_end': train_end,
                'test_start': test_start,
                'test_end': test_end
            })

            current_start += relativedelta(months=self.step_months)

        return periods

    def optimize(self, ticker: str, strategy_class, param_grid: Dict[str, List[Any]],
                start_date: datetime.date, end_date: datetime.date,
                interval: str = '1d') -> Dict[str, Any]:
        """Run walk-forward optimization"""
        periods = self.split_periods(start_date, end_date)

        if not periods:
            raise ValueError("Not enough data for walk-forward analysis")

        all_results = []

        for i, period in enumerate(periods):
            print(f"\nWalk-Forward Period {i+1}/{len(periods)}")
            print(f"  Train: {period['train_start']} to {period['train_end']}")
            print(f"  Test:  {period['test_start']} to {period['test_end']}")

            train_data = self.data_manager.get_data(
                ticker,
                period['train_start'],
                period['train_end'],
                interval
            )

            if train_data.empty:
                print(f"  Skipping: No training data available")
                continue

            best_params = self._find_best_params(
                ticker,
                strategy_class,
                param_grid,
                train_data,
                period['train_start'],
                period['train_end'],
                interval
            )

            test_data = self.data_manager.get_data(
                ticker,
                period['test_start'],
                period['test_end'],
                interval
            )

            if test_data.empty:
                print(f"  Skipping: No test data available")
                continue

            test_results = self._run_backtest(
                ticker,
                strategy_class,
                best_params,
                period['test_start'],
                period['test_end'],
                interval
            )

            all_results.append({
                'period': i + 1,
                'train_start': period['train_start'],
                'train_end': period['train_end'],
                'test_start': period['test_start'],
                'test_end': period['test_end'],
                'best_params': best_params['params'],
                'train_return': best_params['return_pct'],
                'test_return': test_results['return_pct'],
                'test_sharpe': test_results['sharpe_ratio'],
                'test_max_dd': test_results['max_drawdown'],
                'test_trades': test_results['total_trades']
            })

            print(f"  Best Params: {best_params['params']}")
            print(f"  Train Return: {best_params['return_pct']:.2f}%")
            print(f"  Test Return:  {test_results['return_pct']:.2f}%")

        return {
            'ticker': ticker,
            'strategy': strategy_class.__name__,
            'periods': all_results,
            'summary': self._calculate_summary(all_results)
        }

    def _find_best_params(self, ticker: str, strategy_class, param_grid: Dict[str, List[Any]],
                         train_data: pd.DataFrame, start_date: datetime.date,
                         end_date: datetime.date, interval: str) -> Dict[str, Any]:
        """Find best parameters on training data"""
        param_combinations = self._generate_param_combinations(param_grid)

        best_result = None
        best_sharpe = float('-inf')

        for params in param_combinations:
            try:
                result = self._run_backtest(ticker, strategy_class, params, start_date, end_date, interval)

                sharpe = result.get('sharpe_ratio', 0) or 0

                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_result = {
                        'params': params,
                        'return_pct': result['return_pct'],
                        'sharpe_ratio': sharpe
                    }

            except Exception:
                continue

        if best_result is None:
            raise ValueError("No valid parameter combinations found")

        return best_result

    def _run_backtest(self, ticker: str, strategy_class, params: Dict[str, Any],
                     start_date: datetime.date, end_date: datetime.date,
                     interval: str) -> Dict[str, Any]:
        """Run single backtest with given parameters"""
        runner = Run_strategy(params, strategy_class)
        results = runner.runstrat(ticker, start_date, interval, end_date)
        return results

    def _generate_param_combinations(self, param_grid: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """Generate all parameter combinations from grid"""
        if not param_grid:
            return [{}]

        keys = list(param_grid.keys())
        values = list(param_grid.values())

        combinations = []

        def generate(index: int, current: Dict[str, Any]):
            if index == len(keys):
                combinations.append(current.copy())
                return

            key = keys[index]
            for value in values[index]:
                current[key] = value
                generate(index + 1, current)

        generate(0, {})
        return combinations

    def _calculate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics across all periods"""
        if not results:
            return {}

        test_returns = [r['test_return'] for r in results]
        test_sharpes = [r['test_sharpe'] for r in results if r['test_sharpe'] is not None]

        return {
            'total_periods': len(results),
            'avg_test_return': sum(test_returns) / len(test_returns) if test_returns else 0,
            'avg_test_sharpe': sum(test_sharpes) / len(test_sharpes) if test_sharpes else None,
            'win_rate': len([r for r in results if r['test_return'] > 0]) / len(results) if results else 0,
            'best_period': max(results, key=lambda x: x['test_return']) if results else None,
            'worst_period': min(results, key=lambda x: x['test_return']) if results else None
        }
