"""Comprehensive integration tests for StrategyEnsemble"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.strategy_ensemble import StrategyEnsemble
from core.data_manager import DataManager


class TestStrategyEnsemble(unittest.TestCase):
    """Integration test suite for StrategyEnsemble class"""

    def setUp(self):
        """Set up mock data manager and strategies"""
        self.dm = MagicMock(spec=DataManager)

        # Create mock strategy classes with __name__ attribute
        self.mock_strategy_class_1 = MagicMock()
        self.mock_strategy_class_1.__name__ = 'MockStrategy1'

        self.mock_strategy_class_2 = MagicMock()
        self.mock_strategy_class_2.__name__ = 'MockStrategy2'

        self.mock_strategy_class_3 = MagicMock()
        self.mock_strategy_class_3.__name__ = 'MockStrategy3'

        self.strategies = [
            (self.mock_strategy_class_1, {'cash': 10000, 'period': 20}),
            (self.mock_strategy_class_2, {'cash': 10000, 'threshold': 0.02}),
            (self.mock_strategy_class_3, {'cash': 10000, 'devfactor': 2.0})
        ]

    def test_ensemble_initialization(self):
        """Test StrategyEnsemble initialization"""
        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=self.strategies,
            vote_threshold=0.5
        )

        self.assertEqual(ensemble.vote_threshold, 0.5)
        self.assertEqual(len(ensemble.strategies), 3)
        self.assertIsNotNone(ensemble.data_manager)

    def test_vote_threshold_validation(self):
        """Test vote threshold validation"""
        # Valid thresholds
        ensemble = StrategyEnsemble(self.dm, self.strategies, vote_threshold=0.5)
        self.assertEqual(ensemble.vote_threshold, 0.5)

        ensemble = StrategyEnsemble(self.dm, self.strategies, vote_threshold=0.67)
        self.assertEqual(ensemble.vote_threshold, 0.67)

        ensemble = StrategyEnsemble(self.dm, self.strategies, vote_threshold=1.0)
        self.assertEqual(ensemble.vote_threshold, 1.0)

    @patch('core.strategy_ensemble.Run_strategy')
    def test_signal_aggregation_majority_vote(self, mock_run_strategy):
        """Test signal aggregation with majority voting (2 out of 3)"""
        # Mock individual strategy results
        mock_instance = MagicMock()

        # Strategy 1 and 2 agree on Jan 1 trade
        results = [
            {
                'return_pct': 10.0,
                'sharpe_ratio': 1.5,
                'total_trades': 2,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 100.0,
                        'exit_price': 110.0,
                        'pnl': 100.0
                    },
                    {
                        'entry_date': datetime(2024, 2, 1),
                        'exit_date': datetime(2024, 2, 5),
                        'entry_price': 110.0,
                        'exit_price': 105.0,
                        'pnl': -50.0
                    }
                ]
            },
            {
                'return_pct': 8.0,
                'sharpe_ratio': 1.3,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 101.0,
                        'exit_price': 111.0,
                        'pnl': 95.0
                    }
                ]
            },
            {
                'return_pct': 5.0,
                'sharpe_ratio': 1.0,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 3, 1),
                        'exit_date': datetime(2024, 3, 5),
                        'entry_price': 105.0,
                        'exit_price': 108.0,
                        'pnl': 30.0
                    }
                ]
            }
        ]

        call_count = [0]

        def runstrat_side_effect(*args, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            return results[idx]

        mock_instance.runstrat.side_effect = runstrat_side_effect
        mock_run_strategy.return_value = mock_instance

        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=self.strategies,
            vote_threshold=0.67  # Requires 2 out of 3
        )

        result = ensemble.run_ensemble(
            ticker='TEST',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            interval='1d'
        )

        # Should only have Jan 1 trade (2 strategies agreed)
        ensemble_trades = result.get('ensemble_trades', [])
        self.assertEqual(len(ensemble_trades), 1)
        self.assertEqual(ensemble_trades[0]['entry_date'], datetime(2024, 1, 1))
        self.assertEqual(ensemble_trades[0]['votes'], 2)

    @patch('core.strategy_ensemble.Run_strategy')
    def test_signal_averaging(self, mock_run_strategy):
        """Test that ensemble averages entry/exit prices across agreeing strategies"""
        mock_instance = MagicMock()

        # All 3 strategies agree on same trade date
        results = [
            {
                'return_pct': 10.0,
                'sharpe_ratio': 1.5,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 100.0,
                        'exit_price': 110.0,
                        'pnl': 100.0
                    }
                ]
            },
            {
                'return_pct': 10.0,
                'sharpe_ratio': 1.5,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 102.0,
                        'exit_price': 112.0,
                        'pnl': 100.0
                    }
                ]
            },
            {
                'return_pct': 10.0,
                'sharpe_ratio': 1.5,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 101.0,
                        'exit_price': 111.0,
                        'pnl': 100.0
                    }
                ]
            }
        ]

        call_count = [0]

        def runstrat_side_effect(*args, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            return results[idx]

        mock_instance.runstrat.side_effect = runstrat_side_effect
        mock_run_strategy.return_value = mock_instance

        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=self.strategies,
            vote_threshold=0.5
        )

        result = ensemble.run_ensemble(
            ticker='TEST',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            interval='1d'
        )

        ensemble_trades = result.get('ensemble_trades', [])
        self.assertEqual(len(ensemble_trades), 1)

        # Verify averaged prices
        # Entry: (100 + 102 + 101) / 3 = 101.0
        # Exit: (110 + 112 + 111) / 3 = 111.0
        self.assertAlmostEqual(ensemble_trades[0]['entry_price'], 101.0, places=1)
        self.assertAlmostEqual(ensemble_trades[0]['exit_price'], 111.0, places=1)
        self.assertEqual(ensemble_trades[0]['votes'], 3)

    @patch('core.strategy_ensemble.Run_strategy')
    def test_unanimous_vote_requirement(self, mock_run_strategy):
        """Test ensemble with unanimous voting (100% agreement required)"""
        mock_instance = MagicMock()

        # Only strategy 1 and 2 agree
        results = [
            {
                'return_pct': 10.0,
                'sharpe_ratio': 1.5,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 100.0,
                        'exit_price': 110.0,
                        'pnl': 100.0
                    }
                ]
            },
            {
                'return_pct': 8.0,
                'sharpe_ratio': 1.3,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 101.0,
                        'exit_price': 111.0,
                        'pnl': 95.0
                    }
                ]
            },
            {
                'return_pct': 5.0,
                'sharpe_ratio': 1.0,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 2, 1),  # Different date
                        'exit_date': datetime(2024, 2, 5),
                        'entry_price': 105.0,
                        'exit_price': 108.0,
                        'pnl': 30.0
                    }
                ]
            }
        ]

        call_count = [0]

        def runstrat_side_effect(*args, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            return results[idx]

        mock_instance.runstrat.side_effect = runstrat_side_effect
        mock_run_strategy.return_value = mock_instance

        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=self.strategies,
            vote_threshold=1.0  # Requires unanimous agreement
        )

        result = ensemble.run_ensemble(
            ticker='TEST',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            interval='1d'
        )

        # No trades should pass (only 2 out of 3 agreed)
        ensemble_trades = result.get('ensemble_trades', [])
        self.assertEqual(len(ensemble_trades), 0)

    @patch('core.strategy_ensemble.Run_strategy')
    def test_individual_results_tracking(self, mock_run_strategy):
        """Test that individual strategy results are tracked"""
        mock_instance = MagicMock()

        results = [
            {'return_pct': 10.0, 'sharpe_ratio': 1.5, 'total_trades': 5, 'trades': []},
            {'return_pct': 8.0, 'sharpe_ratio': 1.3, 'total_trades': 3, 'trades': []},
            {'return_pct': 5.0, 'sharpe_ratio': 1.0, 'total_trades': 2, 'trades': []}
        ]

        call_count = [0]

        def runstrat_side_effect(*args, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            return results[idx]

        mock_instance.runstrat.side_effect = runstrat_side_effect
        mock_run_strategy.return_value = mock_instance

        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=self.strategies,
            vote_threshold=0.5
        )

        result = ensemble.run_ensemble(
            ticker='TEST',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            interval='1d'
        )

        # Verify individual results are tracked
        individual_results = result.get('individual_results', {})
        self.assertEqual(len(individual_results), 3)

        strategy_names = list(individual_results.keys())
        self.assertIn('MockStrategy1_0', strategy_names)
        self.assertIn('MockStrategy2_1', strategy_names)
        self.assertIn('MockStrategy3_2', strategy_names)

    @patch('core.strategy_ensemble.Run_strategy')
    def test_ensemble_metrics_calculation(self, mock_run_strategy):
        """Test that ensemble-level metrics are calculated"""
        mock_instance = MagicMock()

        # Create trades that all strategies agree on
        common_trades = [
            {
                'entry_date': datetime(2024, 1, 1),
                'exit_date': datetime(2024, 1, 5),
                'entry_price': 100.0,
                'exit_price': 110.0,
                'pnl': 100.0
            }
        ]

        results = [
            {'return_pct': 10.0, 'sharpe_ratio': 1.5, 'total_trades': 1, 'trades': common_trades},
            {'return_pct': 8.0, 'sharpe_ratio': 1.3, 'total_trades': 1, 'trades': common_trades},
            {'return_pct': 5.0, 'sharpe_ratio': 1.0, 'total_trades': 1, 'trades': common_trades}
        ]

        call_count = [0]

        def runstrat_side_effect(*args, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            return results[idx]

        mock_instance.runstrat.side_effect = runstrat_side_effect
        mock_run_strategy.return_value = mock_instance

        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=self.strategies,
            vote_threshold=0.5
        )

        result = ensemble.run_ensemble(
            ticker='TEST',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            interval='1d'
        )

        # Verify ensemble metrics exist
        ensemble_metrics = result.get('ensemble_metrics', {})
        self.assertIn('total_trades', ensemble_metrics)
        self.assertIn('avg_votes_per_trade', ensemble_metrics)

    def test_multiple_vote_thresholds(self):
        """Test ensemble with various vote threshold values"""
        # Test different valid thresholds
        for threshold in [0.3, 0.5, 0.67, 0.75, 1.0]:
            ensemble = StrategyEnsemble(
                data_manager=self.dm,
                strategies=self.strategies,
                vote_threshold=threshold
            )
            self.assertEqual(ensemble.vote_threshold, threshold)

    @patch('core.strategy_ensemble.Run_strategy')
    def test_no_common_signals(self, mock_run_strategy):
        """Test ensemble when no strategies agree on any trades"""
        mock_instance = MagicMock()

        # Each strategy trades on different dates
        results = [
            {
                'return_pct': 10.0,
                'sharpe_ratio': 1.5,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 1, 1),
                        'exit_date': datetime(2024, 1, 5),
                        'entry_price': 100.0,
                        'exit_price': 110.0,
                        'pnl': 100.0
                    }
                ]
            },
            {
                'return_pct': 8.0,
                'sharpe_ratio': 1.3,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 2, 1),
                        'exit_date': datetime(2024, 2, 5),
                        'entry_price': 105.0,
                        'exit_price': 115.0,
                        'pnl': 95.0
                    }
                ]
            },
            {
                'return_pct': 5.0,
                'sharpe_ratio': 1.0,
                'total_trades': 1,
                'trades': [
                    {
                        'entry_date': datetime(2024, 3, 1),
                        'exit_date': datetime(2024, 3, 5),
                        'entry_price': 108.0,
                        'exit_price': 113.0,
                        'pnl': 50.0
                    }
                ]
            }
        ]

        call_count = [0]

        def runstrat_side_effect(*args, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            return results[idx]

        mock_instance.runstrat.side_effect = runstrat_side_effect
        mock_run_strategy.return_value = mock_instance

        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=self.strategies,
            vote_threshold=0.67  # Requires 2 out of 3
        )

        result = ensemble.run_ensemble(
            ticker='TEST',
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            interval='1d'
        )

        # No trades should pass
        ensemble_trades = result.get('ensemble_trades', [])
        self.assertEqual(len(ensemble_trades), 0)

    def test_empty_strategies_list(self):
        """Test ensemble with empty strategies list"""
        ensemble = StrategyEnsemble(
            data_manager=self.dm,
            strategies=[],
            vote_threshold=0.5
        )

        self.assertEqual(len(ensemble.strategies), 0)


if __name__ == '__main__':
    unittest.main()
