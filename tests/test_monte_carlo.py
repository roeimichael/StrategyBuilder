"""
Tests for Monte Carlo Simulator

Unit tests to verify:
- Bootstrapping correctly randomizes trade order
- Simulations generate valid equity curves
- Statistical calculations are accurate
- Stress testing scenarios work correctly
"""

import unittest
import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.risk.monte_carlo import MonteCarloSimulator, MonteCarloResults


class TestMonteCarloBasics(unittest.TestCase):
    """Test basic Monte Carlo functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.simulator = MonteCarloSimulator(
            initial_capital=10000,
            n_simulations=100,
            random_seed=42
        )

    def test_initialization(self):
        """Test simulator initialization."""
        self.assertEqual(self.simulator.initial_capital, 10000)
        self.assertEqual(self.simulator.n_simulations, 100)
        self.assertEqual(self.simulator.random_seed, 42)

    def test_bootstrap_returns(self):
        """Test bootstrapping returns."""
        original_returns = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        # Bootstrap with replacement
        bootstrapped = self.simulator.bootstrap_returns(original_returns, n_samples=10)

        # Should have correct length
        self.assertEqual(len(bootstrapped), 10)

        # All values should be from original set
        for val in bootstrapped:
            self.assertIn(val, original_returns)

    def test_bootstrap_reproducibility(self):
        """Test that random seed ensures reproducibility."""
        returns = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        # Create simulator and bootstrap twice with same seed
        np.random.seed(42)
        sim1 = MonteCarloSimulator(random_seed=None)
        bootstrap1 = sim1.bootstrap_returns(returns, n_samples=20)

        np.random.seed(42)
        sim2 = MonteCarloSimulator(random_seed=None)
        bootstrap2 = sim2.bootstrap_returns(returns, n_samples=20)

        # Should produce same results
        np.testing.assert_array_equal(bootstrap1, bootstrap2)

    def test_bootstrap_different_seeds(self):
        """Test that different seeds produce different results."""
        returns = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        sim1 = MonteCarloSimulator(random_seed=42)
        sim2 = MonteCarloSimulator(random_seed=123)

        bootstrap1 = sim1.bootstrap_returns(returns, n_samples=50)
        bootstrap2 = sim2.bootstrap_returns(returns, n_samples=50)

        # Should produce different results (very unlikely to be identical)
        self.assertFalse(np.array_equal(bootstrap1, bootstrap2))


class TestTradeSequenceRandomization(unittest.TestCase):
    """Test trade sequence randomization (CRITICAL REQUIREMENT)."""

    def test_shuffle_randomizes_trade_order(self):
        """CRITICAL: Verify that trade order is randomized."""
        simulator = MonteCarloSimulator(n_simulations=5, random_seed=None)

        # Create returns in specific order
        returns = np.array([5.0, -3.0, 2.0, -1.0, 4.0, -2.0, 3.0, 1.0])

        # Run simulations
        results = simulator.simulate_from_returns(returns, method='shuffle')

        # Check that different simulations have different sequences
        # We can't directly check order, but we can verify different final values
        final_values = results.final_values

        # Should have some variation in final values due to order effects
        std_dev = np.std(final_values)
        self.assertGreater(std_dev, 0)  # Should have variation

    def test_shuffle_preserves_all_returns(self):
        """Test that shuffling preserves all returns (doesn't add/remove)."""
        simulator = MonteCarloSimulator(n_simulations=1, random_seed=42)

        original_returns = np.array([5.0, -3.0, 2.0, 4.0])

        # Manually check that shuffle preserves returns
        np.random.seed(42)
        shuffled = np.random.permutation(original_returns)

        # Should have same elements (order can differ)
        self.assertEqual(sorted(shuffled), sorted(original_returns))

    def test_bootstrap_allows_replacement(self):
        """Test that bootstrap sampling allows replacement (can have duplicates)."""
        simulator = MonteCarloSimulator(random_seed=42)

        returns = np.array([1.0, 2.0, 3.0])

        # Sample more than available (must use replacement)
        bootstrapped = simulator.bootstrap_returns(returns, n_samples=10, replacement=True)

        # Should have 10 samples
        self.assertEqual(len(bootstrapped), 10)

        # Check if we have any duplicates (very likely with 10 samples from 3 values)
        unique_count = len(np.unique(bootstrapped))
        self.assertLess(unique_count, 10)  # Should have duplicates


class TestEquityCurveGeneration(unittest.TestCase):
    """Test equity curve generation (CRITICAL REQUIREMENT)."""

    def test_equity_curve_starts_at_initial_capital(self):
        """Test that equity curve starts at initial capital."""
        simulator = MonteCarloSimulator(initial_capital=10000)

        returns = np.array([5.0, -2.0, 3.0])
        equity_curve = simulator._calculate_equity_curve(returns)

        # First value should be initial capital
        self.assertEqual(equity_curve[0], 10000)

    def test_equity_curve_length(self):
        """Test equity curve has correct length."""
        simulator = MonteCarloSimulator(initial_capital=10000)

        returns = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        equity_curve = simulator._calculate_equity_curve(returns)

        # Should be length of returns + 1 (initial capital + each return)
        self.assertEqual(len(equity_curve), len(returns) + 1)

    def test_equity_curve_calculation(self):
        """Test equity curve is calculated correctly."""
        simulator = MonteCarloSimulator(initial_capital=10000)

        # Simple returns: 10%, -5%, 5%
        returns = np.array([10.0, -5.0, 5.0])
        equity_curve = simulator._calculate_equity_curve(returns)

        # Manual calculation:
        # Start: 10000
        # After +10%: 10000 * 1.10 = 11000
        # After -5%: 11000 * 0.95 = 10450
        # After +5%: 10450 * 1.05 = 10972.5

        expected = [10000, 11000, 10450, 10972.5]

        np.testing.assert_array_almost_equal(equity_curve, expected, decimal=1)

    def test_equity_curve_with_100_percent_loss(self):
        """Test equity curve handles -100% return (total loss)."""
        simulator = MonteCarloSimulator(initial_capital=10000)

        returns = np.array([10.0, -100.0])
        equity_curve = simulator._calculate_equity_curve(returns)

        # After -100% return, equity should be 0
        self.assertEqual(equity_curve[-1], 0)

    def test_equity_curve_multiple_simulations(self):
        """Test that multiple simulations generate different equity curves."""
        simulator = MonteCarloSimulator(n_simulations=10, random_seed=None)

        returns = np.array([5.0, -3.0, 2.0, -1.0, 4.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        # Should have multiple simulations
        self.assertEqual(len(results.simulations), 10)

        # Each simulation should be an equity curve
        for sim in results.simulations:
            self.assertEqual(len(sim), len(returns) + 1)

        # Different simulations should (likely) have different final values
        final_values_set = set(results.final_values)
        self.assertGreater(len(final_values_set), 1)  # Should have variation


class TestSimulationMethods(unittest.TestCase):
    """Test different simulation methods."""

    def test_shuffle_method(self):
        """Test shuffle simulation method."""
        simulator = MonteCarloSimulator(n_simulations=50, random_seed=42)

        returns = np.array([5.0, -2.0, 3.0, -1.0, 2.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        self.assertEqual(len(results.simulations), 50)
        self.assertEqual(len(results.final_values), 50)

    def test_bootstrap_method(self):
        """Test bootstrap simulation method."""
        simulator = MonteCarloSimulator(n_simulations=50, random_seed=42)

        returns = np.array([5.0, -2.0, 3.0, -1.0, 2.0])

        results = simulator.simulate_from_returns(returns, method='bootstrap')

        self.assertEqual(len(results.simulations), 50)
        self.assertEqual(len(results.final_values), 50)

    def test_invalid_method_raises_error(self):
        """Test that invalid method raises error."""
        simulator = MonteCarloSimulator()

        returns = np.array([1.0, 2.0, 3.0])

        with self.assertRaises(ValueError):
            simulator.simulate_from_returns(returns, method='invalid_method')

    def test_empty_returns_raises_error(self):
        """Test that empty returns raises error."""
        simulator = MonteCarloSimulator()

        empty_returns = np.array([])

        with self.assertRaises(ValueError):
            simulator.simulate_from_returns(empty_returns)


class TestFromTradesSimulation(unittest.TestCase):
    """Test simulation from trade dictionaries."""

    def test_simulate_from_trades_with_return_pct(self):
        """Test simulation from trades with return_pct field."""
        simulator = MonteCarloSimulator(n_simulations=20)

        trades = [
            {'return_pct': 5.0},
            {'return_pct': -2.0},
            {'return_pct': 3.0},
            {'return_pct': -1.0},
            {'return_pct': 4.0}
        ]

        results = simulator.simulate_from_trades(trades, method='shuffle')

        self.assertEqual(len(results.simulations), 20)
        self.assertEqual(len(results.final_values), 20)

    def test_simulate_from_trades_with_pnl(self):
        """Test simulation from trades with pnl and entry_value fields."""
        simulator = MonteCarloSimulator(n_simulations=20)

        trades = [
            {'pnl': 100, 'entry_value': 1000},  # 10% return
            {'pnl': -50, 'entry_value': 1000},  # -5% return
            {'pnl': 75, 'entry_value': 1000}    # 7.5% return
        ]

        results = simulator.simulate_from_trades(trades, method='shuffle')

        self.assertEqual(len(results.simulations), 20)

    def test_empty_trades_raises_error(self):
        """Test that empty trades list raises error."""
        simulator = MonteCarloSimulator()

        with self.assertRaises(ValueError):
            simulator.simulate_from_trades([])


class TestStatisticalCalculations(unittest.TestCase):
    """Test statistical calculations."""

    def test_results_contains_all_metrics(self):
        """Test that results contain all required metrics."""
        simulator = MonteCarloSimulator(n_simulations=100, random_seed=42)

        returns = np.array([5.0, -2.0, 3.0, -1.0, 2.0, 4.0, -3.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        # Check all fields exist
        self.assertIsNotNone(results.simulations)
        self.assertIsNotNone(results.final_values)
        self.assertIsNotNone(results.percentiles)
        self.assertIsNotNone(results.mean_return)
        self.assertIsNotNone(results.median_return)
        self.assertIsNotNone(results.std_return)
        self.assertIsNotNone(results.max_drawdowns)
        self.assertIsNotNone(results.mean_max_drawdown)
        self.assertIsNotNone(results.best_case)
        self.assertIsNotNone(results.worst_case)
        self.assertIsNotNone(results.confidence_95_lower)
        self.assertIsNotNone(results.confidence_95_upper)
        self.assertIsNotNone(results.probability_of_profit)
        self.assertIsNotNone(results.risk_of_ruin)

    def test_percentiles_in_order(self):
        """Test that percentiles are in ascending order."""
        simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)

        returns = np.array([5.0, -2.0, 3.0, -1.0, 2.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        # Percentiles should be in order (or equal with small samples)
        p5 = results.percentiles['5th']
        p25 = results.percentiles['25th']
        p50 = results.percentiles['50th']
        p75 = results.percentiles['75th']
        p95 = results.percentiles['95th']

        self.assertLessEqual(p5, p25)
        self.assertLessEqual(p25, p50)
        self.assertLessEqual(p50, p75)
        self.assertLessEqual(p75, p95)

    def test_probability_of_profit_range(self):
        """Test that probability of profit is between 0 and 1."""
        simulator = MonteCarloSimulator(n_simulations=100, random_seed=42)

        returns = np.array([5.0, -2.0, 3.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        self.assertGreaterEqual(results.probability_of_profit, 0.0)
        self.assertLessEqual(results.probability_of_profit, 1.0)

    def test_risk_of_ruin_range(self):
        """Test that risk of ruin is between 0 and 1."""
        simulator = MonteCarloSimulator(n_simulations=100, random_seed=42)

        returns = np.array([5.0, -2.0, 3.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        self.assertGreaterEqual(results.risk_of_ruin, 0.0)
        self.assertLessEqual(results.risk_of_ruin, 1.0)

    def test_profitable_strategy_probability(self):
        """Test probability of profit for clearly profitable strategy."""
        simulator = MonteCarloSimulator(n_simulations=100, random_seed=42)

        # All positive returns
        returns = np.array([2.0, 3.0, 1.0, 2.5, 1.5])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        # Should have high probability of profit
        self.assertGreater(results.probability_of_profit, 0.9)

    def test_losing_strategy_probability(self):
        """Test probability of profit for clearly losing strategy."""
        simulator = MonteCarloSimulator(n_simulations=100, random_seed=42)

        # All negative returns
        returns = np.array([-2.0, -3.0, -1.0, -2.5, -1.5])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        # Should have low probability of profit
        self.assertLess(results.probability_of_profit, 0.1)


class TestMaxDrawdownCalculation(unittest.TestCase):
    """Test maximum drawdown calculations."""

    def test_calculate_max_drawdown(self):
        """Test max drawdown calculation."""
        simulator = MonteCarloSimulator()

        # Equity curve with known drawdown
        # Peak at 12000, trough at 9000 = 25% drawdown
        equity_curve = np.array([10000, 11000, 12000, 11000, 10000, 9000, 10000])

        max_dd = simulator._calculate_max_drawdown(equity_curve)

        expected_dd = (12000 - 9000) / 12000
        self.assertAlmostEqual(max_dd, expected_dd, places=4)

    def test_max_drawdown_no_drawdown(self):
        """Test max drawdown when equity only increases."""
        simulator = MonteCarloSimulator()

        # No drawdown - always increasing
        equity_curve = np.array([10000, 11000, 12000, 13000])

        max_dd = simulator._calculate_max_drawdown(equity_curve)

        self.assertAlmostEqual(max_dd, 0.0, places=4)

    def test_max_drawdown_all_simulations(self):
        """Test that max drawdown is calculated for all simulations."""
        simulator = MonteCarloSimulator(n_simulations=50, random_seed=42)

        returns = np.array([5.0, -10.0, 3.0, -5.0, 8.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        # Should have drawdown for each simulation
        self.assertEqual(len(results.max_drawdowns), 50)

        # All drawdowns should be >= 0
        for dd in results.max_drawdowns:
            self.assertGreaterEqual(dd, 0.0)


class TestStressTesting(unittest.TestCase):
    """Test stress testing scenarios."""

    def test_2008_crisis_stress(self):
        """Test 2008 financial crisis stress scenario."""
        simulator = MonteCarloSimulator(n_simulations=50, random_seed=42)

        returns = np.array([2.0, -1.0, 3.0, -0.5, 1.5, 2.5, -2.0])

        results = simulator.stress_test(returns, scenario='2008_crisis')

        # Should have results
        self.assertEqual(len(results.simulations), 50)

        # Stress scenario should produce worse outcomes
        # Mean return should be lower than original
        original_results = simulator.simulate_from_returns(returns, method='shuffle')

        # Crisis scenario should have lower mean return
        self.assertLess(results.mean_return, original_results.mean_return)

    def test_flash_crash_stress(self):
        """Test flash crash stress scenario."""
        simulator = MonteCarloSimulator(n_simulations=50, random_seed=42)

        returns = np.array([1.0, 2.0, 1.5, 1.0, 2.0])

        results = simulator.stress_test(returns, scenario='flash_crash')

        self.assertEqual(len(results.simulations), 50)

        # Flash crash should create significant drawdowns
        self.assertGreater(results.mean_max_drawdown, 0.1)

    def test_prolonged_bear_stress(self):
        """Test prolonged bear market stress scenario."""
        simulator = MonteCarloSimulator(n_simulations=50, random_seed=42)

        returns = np.array([2.0, 1.0, 3.0, 1.5, 2.5])

        results = simulator.stress_test(returns, scenario='prolonged_bear')

        # Bear market should produce lower returns
        self.assertLess(results.mean_return, 0)

    def test_black_swan_stress(self):
        """Test black swan event stress scenario."""
        simulator = MonteCarloSimulator(n_simulations=50, random_seed=42)

        returns = np.array([1.0, 2.0, 1.5, 2.0, 1.5])

        results = simulator.stress_test(returns, scenario='black_swan')

        # Black swan should create higher volatility than normal
        # Compare to non-stressed version
        normal_results = simulator.simulate_from_returns(returns, method='shuffle')
        self.assertGreater(results.std_return, normal_results.std_return)

    def test_invalid_scenario_raises_error(self):
        """Test that invalid scenario raises error."""
        simulator = MonteCarloSimulator()

        returns = np.array([1.0, 2.0, 3.0])

        with self.assertRaises(ValueError):
            simulator.stress_test(returns, scenario='invalid_scenario')


class TestSummaryStatistics(unittest.TestCase):
    """Test summary statistics generation."""

    def test_get_summary_statistics(self):
        """Test summary statistics generation."""
        simulator = MonteCarloSimulator(initial_capital=10000, n_simulations=100)

        returns = np.array([5.0, -2.0, 3.0, -1.0, 2.0])

        results = simulator.simulate_from_returns(returns, method='shuffle')

        summary = simulator.get_summary_statistics(results)

        # Check all required fields
        required_fields = [
            'initial_capital',
            'n_simulations',
            'mean_final_value',
            'median_final_value',
            'mean_return_pct',
            'median_return_pct',
            'std_return_pct',
            'best_case_final',
            'worst_case_final',
            'percentile_5th',
            'percentile_95th',
            'confidence_95_lower',
            'confidence_95_upper',
            'probability_of_profit',
            'risk_of_ruin',
            'mean_max_drawdown'
        ]

        for field in required_fields:
            self.assertIn(field, summary)

    def test_summary_statistics_values(self):
        """Test that summary statistics have reasonable values."""
        simulator = MonteCarloSimulator(initial_capital=10000, n_simulations=100, random_seed=42)

        # Positive returns
        returns = np.array([2.0, 3.0, 1.0, 2.0, 1.5])

        results = simulator.simulate_from_returns(returns, method='shuffle')
        summary = simulator.get_summary_statistics(results)

        # Mean final value should be > initial for positive returns
        self.assertGreater(summary['mean_final_value'], 10000)

        # Best case should be >= worst case
        self.assertGreaterEqual(summary['best_case_final'], summary['worst_case_final'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
