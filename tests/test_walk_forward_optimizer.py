"""Comprehensive unit tests for WalkForwardOptimizer"""

import os
import sys
import unittest
import datetime
import pandas as pd
from unittest.mock import MagicMock, patch
from dateutil.relativedelta import relativedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.walk_forward_optimizer import WalkForwardOptimizer
from core.data_manager import DataManager


class TestWalkForwardOptimizer(unittest.TestCase):
    """Test suite for WalkForwardOptimizer class"""

    def setUp(self):
        """Set up test optimizer"""
        self.dm = MagicMock(spec=DataManager)
        self.optimizer = WalkForwardOptimizer(
            data_manager=self.dm,
            train_months=12,
            test_months=3,
            step_months=3
        )

    def test_init(self):
        """Test WalkForwardOptimizer initialization"""
        self.assertEqual(self.optimizer.train_months, 12)
        self.assertEqual(self.optimizer.test_months, 3)
        self.assertEqual(self.optimizer.step_months, 3)
        self.assertIsNotNone(self.optimizer.data_manager)

    def test_split_periods_basic(self):
        """Test period splitting with basic parameters"""
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2022, 1, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        self.assertIsInstance(periods, list)
        self.assertGreater(len(periods), 0)

        for period in periods:
            self.assertIn('train_start', period)
            self.assertIn('train_end', period)
            self.assertIn('test_start', period)
            self.assertIn('test_end', period)

    def test_split_periods_count(self):
        """Test correct number of periods are generated"""
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2022, 1, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        expected_periods = 4
        self.assertEqual(len(periods), expected_periods)

    def test_split_periods_dates_sequential(self):
        """Test that periods are sequential"""
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2022, 1, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        for i in range(len(periods)):
            self.assertLess(periods[i]['train_start'], periods[i]['train_end'])
            self.assertLessEqual(periods[i]['train_end'], periods[i]['test_start'])
            self.assertLess(periods[i]['test_start'], periods[i]['test_end'])

    def test_split_periods_train_test_adjacent(self):
        """Test that train and test periods are adjacent"""
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2022, 1, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        for period in periods:
            self.assertEqual(period['train_end'], period['test_start'])

    def test_split_periods_train_duration(self):
        """Test that training periods have correct duration"""
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2022, 1, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        for period in periods:
            train_duration = period['train_end'] - period['train_start']
            expected_duration = relativedelta(months=self.optimizer.train_months)

            self.assertAlmostEqual(
                train_duration.days,
                (period['train_start'] + expected_duration - period['train_start']).days,
                delta=5
            )

    def test_split_periods_insufficient_data(self):
        """Test splitting with insufficient data"""
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 6, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        self.assertEqual(len(periods), 0)

    def test_split_periods_step_size(self):
        """Test that step size is correct"""
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2022, 1, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        for i in range(len(periods) - 1):
            step = periods[i + 1]['train_start'] - periods[i]['train_start']
            expected_step = relativedelta(months=self.optimizer.step_months)

            self.assertAlmostEqual(
                step.days,
                (periods[i]['train_start'] + expected_step - periods[i]['train_start']).days,
                delta=5
            )

    def test_generate_param_combinations_empty(self):
        """Test parameter combination generation with empty grid"""
        param_grid = {}
        combinations = self.optimizer._generate_param_combinations(param_grid)

        self.assertEqual(len(combinations), 1)
        self.assertEqual(combinations[0], {})

    def test_generate_param_combinations_single_param(self):
        """Test parameter combinations with single parameter"""
        param_grid = {'period': [10, 20, 30]}
        combinations = self.optimizer._generate_param_combinations(param_grid)

        self.assertEqual(len(combinations), 3)
        self.assertIn({'period': 10}, combinations)
        self.assertIn({'period': 20}, combinations)
        self.assertIn({'period': 30}, combinations)

    def test_generate_param_combinations_multiple_params(self):
        """Test parameter combinations with multiple parameters"""
        param_grid = {
            'period': [10, 20],
            'devfactor': [1.5, 2.0]
        }
        combinations = self.optimizer._generate_param_combinations(param_grid)

        self.assertEqual(len(combinations), 4)
        self.assertIn({'period': 10, 'devfactor': 1.5}, combinations)
        self.assertIn({'period': 10, 'devfactor': 2.0}, combinations)
        self.assertIn({'period': 20, 'devfactor': 1.5}, combinations)
        self.assertIn({'period': 20, 'devfactor': 2.0}, combinations)

    def test_generate_param_combinations_three_params(self):
        """Test parameter combinations with three parameters"""
        param_grid = {
            'period': [10, 20],
            'devfactor': [1.5, 2.0],
            'order_pct': [0.5, 1.0]
        }
        combinations = self.optimizer._generate_param_combinations(param_grid)

        self.assertEqual(len(combinations), 8)

    def test_calculate_summary_empty(self):
        """Test summary calculation with no results"""
        summary = self.optimizer._calculate_summary([])

        self.assertEqual(summary, {})

    def test_calculate_summary_basic(self):
        """Test summary calculation with basic results"""
        results = [
            {
                'test_return': 10.0,
                'test_sharpe': 1.5
            },
            {
                'test_return': -5.0,
                'test_sharpe': 0.8
            },
            {
                'test_return': 15.0,
                'test_sharpe': 2.0
            }
        ]

        summary = self.optimizer._calculate_summary(results)

        self.assertEqual(summary['total_periods'], 3)
        self.assertAlmostEqual(summary['avg_test_return'], 6.67, places=1)
        self.assertAlmostEqual(summary['avg_test_sharpe'], 1.43, places=1)
        self.assertAlmostEqual(summary['win_rate'], 0.67, places=2)

    def test_calculate_summary_win_rate(self):
        """Test win rate calculation in summary"""
        results = [
            {'test_return': 10.0, 'test_sharpe': 1.5},
            {'test_return': 5.0, 'test_sharpe': 1.2},
            {'test_return': -3.0, 'test_sharpe': 0.5},
            {'test_return': -2.0, 'test_sharpe': 0.3}
        ]

        summary = self.optimizer._calculate_summary(results)

        self.assertEqual(summary['win_rate'], 0.5)

    def test_calculate_summary_with_none_sharpe(self):
        """Test summary calculation with None Sharpe ratios"""
        results = [
            {'test_return': 10.0, 'test_sharpe': 1.5},
            {'test_return': 5.0, 'test_sharpe': None},
            {'test_return': 8.0, 'test_sharpe': 1.2}
        ]

        summary = self.optimizer._calculate_summary(results)

        self.assertIsNotNone(summary['avg_test_sharpe'])
        self.assertAlmostEqual(summary['avg_test_sharpe'], 1.35, places=2)

    def test_calculate_summary_best_worst_periods(self):
        """Test identification of best and worst periods"""
        results = [
            {'test_return': 10.0, 'test_sharpe': 1.5, 'period': 1},
            {'test_return': -5.0, 'test_sharpe': 0.8, 'period': 2},
            {'test_return': 15.0, 'test_sharpe': 2.0, 'period': 3}
        ]

        summary = self.optimizer._calculate_summary(results)

        self.assertEqual(summary['best_period']['test_return'], 15.0)
        self.assertEqual(summary['worst_period']['test_return'], -5.0)

    @patch('core.walk_forward_optimizer.Run_strategy')
    def test_run_backtest(self, mock_run_strategy):
        """Test running a single backtest"""
        mock_instance = MagicMock()
        mock_instance.runstrat.return_value = {
            'return_pct': 10.5,
            'sharpe_ratio': 1.8,
            'total_trades': 25
        }
        mock_run_strategy.return_value = mock_instance

        mock_strategy_class = MagicMock()
        params = {'cash': 10000, 'period': 20}

        result = self.optimizer._run_backtest(
            'TEST',
            mock_strategy_class,
            params,
            datetime.date(2024, 1, 1),
            datetime.date(2024, 12, 31),
            '1d'
        )

        self.assertEqual(result['return_pct'], 10.5)
        self.assertEqual(result['sharpe_ratio'], 1.8)
        mock_instance.runstrat.assert_called_once()

    @patch('core.walk_forward_optimizer.Run_strategy')
    def test_find_best_params(self, mock_run_strategy):
        """Test finding best parameters on training data"""
        mock_instance = MagicMock()

        sharpe_values = [1.0, 1.5, 0.8]
        call_count = [0]

        def runstrat_side_effect(*args, **kwargs):
            idx = call_count[0] % len(sharpe_values)
            call_count[0] += 1
            return {
                'return_pct': 10.0,
                'sharpe_ratio': sharpe_values[idx]
            }

        mock_instance.runstrat.side_effect = runstrat_side_effect
        mock_run_strategy.return_value = mock_instance

        mock_strategy_class = MagicMock()
        param_grid = {'period': [10, 20, 30]}

        mock_data = pd.DataFrame({
            'Close': [100, 101, 102]
        }, index=pd.date_range('2024-01-01', periods=3))

        result = self.optimizer._find_best_params(
            'TEST',
            mock_strategy_class,
            param_grid,
            mock_data,
            datetime.date(2024, 1, 1),
            datetime.date(2024, 12, 31),
            '1d'
        )

        self.assertIn('params', result)
        self.assertIn('return_pct', result)
        self.assertEqual(result['sharpe_ratio'], 1.5)

    def test_split_periods_edge_case_exact_fit(self):
        """Test period splitting when date range fits exactly"""
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2021, 3, 1)

        periods = self.optimizer.split_periods(start_date, end_date)

        self.assertGreater(len(periods), 0)

    def test_custom_train_test_months(self):
        """Test optimizer with custom train/test durations"""
        optimizer = WalkForwardOptimizer(
            data_manager=self.dm,
            train_months=6,
            test_months=2,
            step_months=2
        )

        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date(2021, 1, 1)

        periods = optimizer.split_periods(start_date, end_date)

        self.assertGreater(len(periods), 0)

        for period in periods:
            train_duration = period['train_end'] - period['train_start']
            test_duration = period['test_end'] - period['test_start']

            self.assertGreater(train_duration.days, 150)
            self.assertGreater(test_duration.days, 50)


if __name__ == '__main__':
    unittest.main()
