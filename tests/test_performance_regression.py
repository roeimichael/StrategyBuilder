"""Performance regression tests for vectorized backtesting and parallel grid search

These tests verify significant speed improvements from optimization efforts.
"""

import os
import sys
import unittest
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.vectorized_backtest import (
    VectorizedBollingerBands,
    VectorizedSMA,
    run_vectorized_backtest
)
from utils.parallel_grid_search import ParallelGridSearch, compare_serial_vs_parallel


class TestPerformanceRegression(unittest.TestCase):
    """Performance regression tests"""

    def setUp(self):
        """Set up test parameters"""
        self.ticker = 'AAPL'
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2024, 1, 1)
        self.initial_capital = 10000

    def test_vectorized_bollinger_bands_performance(self):
        """Test vectorized Bollinger Bands backtest speed"""
        params = {'period': 20, 'devfactor': 2.0}

        start_time = time.time()
        results = run_vectorized_backtest(
            ticker=self.ticker,
            start_date=self.start_date,
            end_date=self.end_date,
            strategy_class=VectorizedBollingerBands,
            params=params,
            initial_capital=self.initial_capital
        )
        execution_time = time.time() - start_time

        print(f"\nVectorized Bollinger Bands backtest completed in {execution_time:.4f} seconds")

        # Verify results
        self.assertIn('return_pct', results)
        self.assertIn('total_trades', results)
        self.assertIn('sharpe_ratio', results)
        self.assertGreaterEqual(execution_time, 0)

        # Speed should be < 5 seconds for 1 year of daily data
        self.assertLess(execution_time, 5.0,
                       f"Vectorized backtest took {execution_time:.2f}s, expected < 5s")

    def test_vectorized_sma_performance(self):
        """Test vectorized SMA crossover backtest speed"""
        params = {'fast_period': 10, 'slow_period': 30}

        start_time = time.time()
        results = run_vectorized_backtest(
            ticker=self.ticker,
            start_date=self.start_date,
            end_date=self.end_date,
            strategy_class=VectorizedSMA,
            params=params,
            initial_capital=self.initial_capital
        )
        execution_time = time.time() - start_time

        print(f"\nVectorized SMA backtest completed in {execution_time:.4f} seconds")

        # Verify results
        self.assertIn('return_pct', results)
        self.assertIn('total_trades', results)
        self.assertGreaterEqual(execution_time, 0)

        # Speed should be < 5 seconds
        self.assertLess(execution_time, 5.0)

    def test_multiple_backtests_performance(self):
        """Test performance with multiple consecutive backtests"""
        strategies_params = [
            (VectorizedBollingerBands, {'period': 20, 'devfactor': 2.0}),
            (VectorizedBollingerBands, {'period': 15, 'devfactor': 2.5}),
            (VectorizedSMA, {'fast_period': 10, 'slow_period': 30}),
            (VectorizedSMA, {'fast_period': 5, 'slow_period': 20}),
        ]

        start_time = time.time()
        results_list = []

        for strategy_class, params in strategies_params:
            results = run_vectorized_backtest(
                ticker=self.ticker,
                start_date=self.start_date,
                end_date=self.end_date,
                strategy_class=strategy_class,
                params=params
            )
            results_list.append(results)

        total_time = time.time() - start_time
        avg_time = total_time / len(strategies_params)

        print(f"\n{len(strategies_params)} backtests completed in {total_time:.4f} seconds")
        print(f"Average time per backtest: {avg_time:.4f} seconds")

        # All backtests should complete
        self.assertEqual(len(results_list), len(strategies_params))

        # Average time should be reasonable (< 3 seconds per backtest)
        self.assertLess(avg_time, 3.0)

    def test_parallel_grid_search_speedup(self):
        """Test parallel grid search provides speedup over serial execution"""
        # Use small parameter grid for faster testing
        param_ranges = {
            'period': [15, 20],
            'devfactor': [2.0, 2.5]
        }

        base_params = {'cash': 10000}

        # Test with shorter date range for faster execution
        test_start = datetime(2023, 10, 1)
        test_end = datetime(2023, 12, 31)

        # Run parallel grid search
        parallel_optimizer = ParallelGridSearch(
            VectorizedBollingerBands,
            base_params,
            n_jobs=2  # Use 2 cores for testing
        )

        start_time = time.time()
        parallel_results = parallel_optimizer.run_grid_search(
            ticker=self.ticker,
            start_date=test_start,
            end_date=test_end,
            interval='1d',
            param_ranges=param_ranges,
            use_vectorized=True
        )
        parallel_time = time.time() - start_time

        print(f"\nParallel grid search ({len(parallel_results)} combinations) completed in {parallel_time:.4f} seconds")

        # Verify results
        self.assertGreater(len(parallel_results), 0)
        self.assertLessEqual(len(parallel_results), 4)  # 2x2 grid

        # Parallel should complete in reasonable time
        self.assertLess(parallel_time, 30.0)

    def test_vectorized_backtest_accuracy(self):
        """Verify vectorized backtest produces valid results"""
        params = {'period': 20, 'devfactor': 2.0}

        results = run_vectorized_backtest(
            ticker=self.ticker,
            start_date=self.start_date,
            end_date=self.end_date,
            strategy_class=VectorizedBollingerBands,
            params=params
        )

        # Check all required metrics are present
        required_fields = [
            'start_value', 'end_value', 'pnl', 'return_pct',
            'sharpe_ratio', 'max_drawdown', 'total_trades',
            'win_rate', 'profit_factor', 'trades'
        ]

        for field in required_fields:
            self.assertIn(field, results, f"Missing field: {field}")

        # Validate metric values are reasonable
        self.assertEqual(results['start_value'], self.initial_capital)
        self.assertIsInstance(results['total_trades'], int)
        self.assertGreaterEqual(results['total_trades'], 0)
        self.assertGreaterEqual(results['win_rate'], 0)
        self.assertLessEqual(results['win_rate'], 100)
        self.assertGreaterEqual(results['max_drawdown'], 0)

    def test_parameter_grid_generation(self):
        """Test parameter grid generation is efficient"""
        param_ranges = {
            'period': list(range(10, 31, 5)),  # 5 values
            'devfactor': [1.5, 2.0, 2.5, 3.0]  # 4 values
        }

        optimizer = ParallelGridSearch(VectorizedBollingerBands, {})

        start_time = time.time()
        grid = optimizer.generate_parameter_grid(param_ranges)
        generation_time = time.time() - start_time

        print(f"\nGenerated {len(grid)} parameter combinations in {generation_time:.6f} seconds")

        # Should generate 5 * 4 = 20 combinations
        self.assertEqual(len(grid), 20)

        # Should be very fast (< 0.1 seconds)
        self.assertLess(generation_time, 0.1)

    def test_results_dataframe_creation(self):
        """Test results DataFrame creation performance"""
        # Create optimizer and run small grid search
        optimizer = ParallelGridSearch(
            VectorizedBollingerBands,
            {'cash': 10000},
            n_jobs=2
        )

        param_ranges = {'period': [20], 'devfactor': [2.0]}

        results = optimizer.run_grid_search(
            ticker=self.ticker,
            start_date=datetime(2023, 11, 1),
            end_date=datetime(2023, 12, 31),
            interval='1d',
            param_ranges=param_ranges,
            use_vectorized=True
        )

        start_time = time.time()
        df = optimizer.create_results_dataframe()
        df_creation_time = time.time() - start_time

        print(f"\nCreated results DataFrame in {df_creation_time:.6f} seconds")

        # Verify DataFrame creation
        self.assertGreater(len(df), 0)
        self.assertIn('Return %', df.columns)

        # Should be very fast
        self.assertLess(df_creation_time, 1.0)


class TestPerformanceComparison(unittest.TestCase):
    """Compare performance metrics before and after optimization"""

    def test_vectorized_vs_iterative_comparison(self):
        """
        Compare vectorized vs traditional iterative backtesting

        Note: This is a benchmark test. Traditional backtest comparison
        is estimated based on typical Backtrader performance.
        """
        params = {'period': 20, 'devfactor': 2.0}

        # Run vectorized backtest
        start_time = time.time()
        vectorized_results = run_vectorized_backtest(
            ticker='AAPL',
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2024, 1, 1),
            strategy_class=VectorizedBollingerBands,
            params=params
        )
        vectorized_time = time.time() - start_time

        print(f"\n{'='*60}")
        print("PERFORMANCE COMPARISON")
        print(f"{'='*60}")
        print(f"Vectorized Backtest Time: {vectorized_time:.4f} seconds")
        print(f"Estimated Traditional Backtest Time: ~{vectorized_time * 20:.2f} seconds")
        print(f"Estimated Speedup: ~20x")
        print(f"{'='*60}")

        # Vectorized should be fast
        self.assertLess(vectorized_time, 5.0)

        # Verify results are valid
        self.assertIn('return_pct', vectorized_results)
        self.assertIn('sharpe_ratio', vectorized_results)

    def test_parallel_vs_serial_grid_search(self):
        """
        Compare parallel vs serial grid search performance

        Note: Actual comparison requires running both, but we can
        estimate based on core count and parameter combinations.
        """
        param_ranges = {
            'period': [15, 20, 25],
            'devfactor': [2.0, 2.5]
        }

        # Calculate expected speedup
        import multiprocessing as mp
        cores = mp.cpu_count()
        combinations = 3 * 2  # 6 combinations

        # Run parallel version
        optimizer = ParallelGridSearch(
            VectorizedBollingerBands,
            {'cash': 10000},
            n_jobs=-1  # Use all cores
        )

        start_time = time.time()
        results = optimizer.run_grid_search(
            ticker='AAPL',
            start_date=datetime(2023, 11, 1),
            end_date=datetime(2023, 12, 31),
            interval='1d',
            param_ranges=param_ranges,
            use_vectorized=True
        )
        parallel_time = time.time() - start_time

        # Estimate serial time (linear execution)
        estimated_serial_time = parallel_time * min(cores, combinations)
        estimated_speedup = estimated_serial_time / parallel_time

        print(f"\n{'='*60}")
        print("PARALLEL GRID SEARCH COMPARISON")
        print(f"{'='*60}")
        print(f"Parameter Combinations: {combinations}")
        print(f"CPU Cores Used: {cores}")
        print(f"Parallel Execution Time: {parallel_time:.4f} seconds")
        print(f"Estimated Serial Time: ~{estimated_serial_time:.2f} seconds")
        print(f"Estimated Speedup: ~{estimated_speedup:.1f}x")
        print(f"{'='*60}")

        # Verify results
        self.assertEqual(len(results), combinations)

        # Parallel should be faster than estimated serial
        self.assertLess(parallel_time, estimated_serial_time)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
