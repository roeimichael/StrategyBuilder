"""Comprehensive integration tests for PerformanceAnalyzer"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.performance_analyzer import PerformanceAnalyzer


class TestPerformanceAnalyzer(unittest.TestCase):
    """Integration test suite for PerformanceAnalyzer class"""

    def setUp(self):
        """Set up mock backtest result data"""
        self.start_value = 10000.0
        self.end_value = 12000.0

        # Create mock trades with known outcomes
        self.mock_trades = [
            {
                'entry_date': datetime(2024, 1, 1),
                'exit_date': datetime(2024, 1, 5),
                'entry_price': 100.0,
                'exit_price': 110.0,
                'pnl': 100.0,
                'pnl_pct': 10.0
            },
            {
                'entry_date': datetime(2024, 1, 10),
                'exit_date': datetime(2024, 1, 15),
                'entry_price': 110.0,
                'exit_price': 105.0,
                'pnl': -50.0,
                'pnl_pct': -4.55
            },
            {
                'entry_date': datetime(2024, 1, 20),
                'exit_date': datetime(2024, 1, 25),
                'entry_price': 105.0,
                'exit_price': 120.0,
                'pnl': 150.0,
                'pnl_pct': 14.29
            },
            {
                'entry_date': datetime(2024, 2, 1),
                'exit_date': datetime(2024, 2, 5),
                'entry_price': 120.0,
                'exit_price': 115.0,
                'pnl': -50.0,
                'pnl_pct': -4.17
            },
            {
                'entry_date': datetime(2024, 2, 10),
                'exit_date': datetime(2024, 2, 15),
                'entry_price': 115.0,
                'exit_price': 130.0,
                'pnl': 150.0,
                'pnl_pct': 13.04
            }
        ]

        # Create equity curve
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        values = np.concatenate([
            np.linspace(10000, 10100, 20),  # Win
            np.linspace(10100, 10050, 10),  # Loss
            np.linspace(10050, 10200, 20),  # Win
            np.linspace(10200, 10150, 10),  # Loss
            np.linspace(10150, 10300, 20),  # Win
            np.linspace(10300, 10400, 20)   # Gradual rise
        ])
        self.equity_curve = pd.Series(values, index=dates)

        self.analyzer = PerformanceAnalyzer(
            trades=self.mock_trades,
            start_value=self.start_value,
            end_value=self.end_value,
            equity_curve=self.equity_curve
        )

    def test_win_rate_calculation(self):
        """Test win rate calculation with known trades"""
        win_rate = self.analyzer.calculate_win_rate()

        # 3 wins, 2 losses = 60% win rate
        self.assertAlmostEqual(win_rate, 60.0, places=1)

    def test_profit_factor_calculation(self):
        """Test profit factor calculation"""
        profit_factor = self.analyzer.calculate_profit_factor()

        # Gross profit: 100 + 150 + 150 = 400
        # Gross loss: 50 + 50 = 100
        # Profit factor: 400 / 100 = 4.0
        self.assertAlmostEqual(profit_factor, 4.0, places=1)

    def test_payoff_ratio_calculation(self):
        """Test payoff ratio (avg win / avg loss)"""
        payoff_ratio = self.analyzer.calculate_payoff_ratio()

        # Avg win: (100 + 150 + 150) / 3 = 133.33
        # Avg loss: (50 + 50) / 2 = 50.0
        # Payoff ratio: 133.33 / 50.0 = 2.67
        self.assertAlmostEqual(payoff_ratio, 2.67, places=1)

    def test_calmar_ratio_calculation(self):
        """Test Calmar ratio calculation"""
        calmar_ratio = self.analyzer.calculate_calmar_ratio()

        # Should return a positive value
        self.assertIsNotNone(calmar_ratio)
        if calmar_ratio is not None:
            self.assertGreater(calmar_ratio, 0)

    def test_sortino_ratio_calculation(self):
        """Test Sortino ratio calculation"""
        sortino_ratio = self.analyzer.calculate_sortino_ratio()

        # Should return a value
        self.assertIsNotNone(sortino_ratio)

    def test_consecutive_wins_calculation(self):
        """Test maximum consecutive wins"""
        max_consecutive_wins = self.analyzer.calculate_max_consecutive_wins()

        # From mock trades: Win, Loss, Win, Loss, Win
        # Max consecutive wins = 1
        self.assertEqual(max_consecutive_wins, 1)

    def test_consecutive_losses_calculation(self):
        """Test maximum consecutive losses"""
        max_consecutive_losses = self.analyzer.calculate_max_consecutive_losses()

        # From mock trades: Win, Loss, Win, Loss, Win
        # Max consecutive losses = 1
        self.assertEqual(max_consecutive_losses, 1)

    def test_expectancy_calculation(self):
        """Test trade expectancy calculation"""
        expectancy = self.analyzer.calculate_expectancy()

        # Expectancy = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)
        # = (0.6 * 133.33) - (0.4 * 50.0)
        # = 80.0 - 20.0 = 60.0
        self.assertAlmostEqual(expectancy, 60.0, places=0)

    def test_recovery_periods_calculation(self):
        """Test recovery period identification"""
        recovery_periods = self.analyzer.calculate_recovery_periods()

        # Should identify multiple recovery periods
        self.assertIsInstance(recovery_periods, list)
        self.assertGreater(len(recovery_periods), 0)

        for period in recovery_periods:
            self.assertIn('drawdown_start_idx', period)
            self.assertIn('recovery_idx', period)
            self.assertIn('recovery_days', period)
            self.assertIn('drawdown_pct', period)

    def test_calculate_all_metrics_integration(self):
        """Integration test: verify all metrics are calculated together"""
        all_metrics = self.analyzer.calculate_all_metrics()

        # Verify all required metrics are present
        required_metrics = [
            'win_rate',
            'profit_factor',
            'payoff_ratio',
            'calmar_ratio',
            'sortino_ratio',
            'max_consecutive_wins',
            'max_consecutive_losses',
            'expectancy',
            'avg_win',
            'avg_loss',
            'largest_win',
            'largest_loss',
            'recovery_periods'
        ]

        for metric in required_metrics:
            self.assertIn(metric, all_metrics)

        # Verify metric values match individual calculations
        self.assertAlmostEqual(all_metrics['win_rate'], 60.0, places=1)
        self.assertAlmostEqual(all_metrics['profit_factor'], 4.0, places=1)
        self.assertAlmostEqual(all_metrics['payoff_ratio'], 2.67, places=1)
        self.assertEqual(all_metrics['max_consecutive_wins'], 1)
        self.assertEqual(all_metrics['max_consecutive_losses'], 1)

    def test_empty_trades_handling(self):
        """Test analyzer handles empty trades gracefully"""
        analyzer = PerformanceAnalyzer([], 10000, 10000)

        metrics = analyzer.calculate_all_metrics()

        self.assertEqual(metrics['win_rate'], 0.0)
        self.assertIsNone(metrics['profit_factor'])
        self.assertIsNone(metrics['payoff_ratio'])
        self.assertEqual(metrics['avg_win'], 0.0)
        self.assertEqual(metrics['avg_loss'], 0.0)

    def test_only_winning_trades(self):
        """Test analyzer with only winning trades"""
        winning_trades = [
            {'pnl': 100.0},
            {'pnl': 150.0},
            {'pnl': 200.0}
        ]

        analyzer = PerformanceAnalyzer(winning_trades, 10000, 10450)

        self.assertEqual(analyzer.calculate_win_rate(), 100.0)
        self.assertIsNone(analyzer.calculate_profit_factor())  # No losses
        self.assertEqual(analyzer.calculate_max_consecutive_wins(), 3)

    def test_only_losing_trades(self):
        """Test analyzer with only losing trades"""
        losing_trades = [
            {'pnl': -50.0},
            {'pnl': -75.0},
            {'pnl': -100.0}
        ]

        analyzer = PerformanceAnalyzer(losing_trades, 10000, 9775)

        self.assertEqual(analyzer.calculate_win_rate(), 0.0)
        self.assertIsNone(analyzer.calculate_profit_factor())  # No wins
        self.assertEqual(analyzer.calculate_max_consecutive_losses(), 3)

    def test_create_equity_curve_static_method(self):
        """Test static method for creating equity curve from trades"""
        equity_curve = PerformanceAnalyzer.create_equity_curve(
            self.mock_trades,
            self.start_value
        )

        self.assertIsInstance(equity_curve, pd.Series)
        self.assertEqual(equity_curve.iloc[0], self.start_value)
        self.assertGreater(len(equity_curve), len(self.mock_trades))

    def test_largest_win_loss_tracking(self):
        """Test largest win and loss identification"""
        all_metrics = self.analyzer.calculate_all_metrics()

        self.assertEqual(all_metrics['largest_win'], 150.0)
        self.assertEqual(all_metrics['largest_loss'], -50.0)

    def test_avg_win_loss_calculation(self):
        """Test average win and loss calculation"""
        all_metrics = self.analyzer.calculate_all_metrics()

        # Avg win: (100 + 150 + 150) / 3 = 133.33
        self.assertAlmostEqual(all_metrics['avg_win'], 133.33, places=1)

        # Avg loss: (-50 + -50) / 2 = -50.0 (negative because losses are negative)
        self.assertAlmostEqual(all_metrics['avg_loss'], -50.0, places=1)

    def test_consecutive_wins_with_long_streak(self):
        """Test consecutive wins with extended winning streak"""
        winning_streak_trades = [
            {'pnl': 100.0},
            {'pnl': 150.0},
            {'pnl': 120.0},
            {'pnl': 80.0},
            {'pnl': -50.0},
            {'pnl': 90.0}
        ]

        analyzer = PerformanceAnalyzer(winning_streak_trades, 10000, 10490)
        max_wins = analyzer.calculate_max_consecutive_wins()

        # First 4 trades are wins
        self.assertEqual(max_wins, 4)


if __name__ == '__main__':
    unittest.main()
