"""
Monte Carlo Simulation Module

Implements Monte Carlo simulation for strategy robustness testing:
- Bootstrapping historical returns
- Stress testing scenarios (2008 crash, flash crash, etc.)
- Confidence intervals and risk metrics
- Trade sequence randomization
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import warnings


@dataclass
class MonteCarloResults:
    """Results from Monte Carlo simulation."""
    simulations: List[np.ndarray]
    final_values: np.ndarray
    percentiles: Dict[str, float]
    mean_return: float
    median_return: float
    std_return: float
    max_drawdowns: List[float]
    mean_max_drawdown: float
    worst_case: np.ndarray
    best_case: np.ndarray
    confidence_95_lower: float
    confidence_95_upper: float
    probability_of_profit: float
    risk_of_ruin: float


class MonteCarloSimulator:
    """
    Monte Carlo simulator for backtesting robustness analysis.

    Supports:
    - Bootstrapping trade returns
    - Random trade sequence shuffling
    - Stress testing scenarios
    - Confidence interval estimation
    """

    def __init__(
        self,
        initial_capital: float = 10000,
        n_simulations: int = 1000,
        random_seed: Optional[int] = None
    ):
        """
        Initialize Monte Carlo Simulator.

        Parameters
        ----------
        initial_capital : float
            Starting capital for simulations (default: 10000)
        n_simulations : int
            Number of Monte Carlo simulations to run (default: 1000)
        random_seed : int, optional
            Random seed for reproducibility
        """
        self.initial_capital = initial_capital
        self.n_simulations = n_simulations
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)

    def bootstrap_returns(
        self,
        returns: np.ndarray,
        n_samples: Optional[int] = None,
        replacement: bool = True
    ) -> np.ndarray:
        """
        Bootstrap sample from historical returns.

        Parameters
        ----------
        returns : np.ndarray
            Historical returns to sample from
        n_samples : int, optional
            Number of samples to draw (default: length of returns)
        replacement : bool
            Sample with replacement (default: True)

        Returns
        -------
        np.ndarray
            Bootstrapped returns
        """
        if n_samples is None:
            n_samples = len(returns)

        if len(returns) == 0:
            return np.array([])

        indices = np.random.choice(len(returns), size=n_samples, replace=replacement)
        return returns[indices]

    def simulate_from_trades(
        self,
        trades: List[Dict[str, Any]],
        method: str = 'shuffle'
    ) -> MonteCarloResults:
        """
        Run Monte Carlo simulation from trade list.

        Parameters
        ----------
        trades : list of dict
            List of trade dictionaries with 'pnl' or 'return_pct' keys
        method : str
            Simulation method: 'shuffle' (randomize order) or 'bootstrap' (resample)

        Returns
        -------
        MonteCarloResults
            Results from all simulations
        """
        if not trades:
            raise ValueError("No trades provided for simulation")

        # Extract returns
        returns = self._extract_returns_from_trades(trades)

        if len(returns) == 0:
            raise ValueError("No valid returns found in trades")

        return self.simulate_from_returns(returns, method=method)

    def simulate_from_returns(
        self,
        returns: np.ndarray,
        method: str = 'shuffle'
    ) -> MonteCarloResults:
        """
        Run Monte Carlo simulation from returns array.

        Parameters
        ----------
        returns : np.ndarray
            Array of returns (as percentages, e.g., 5.0 for 5%)
        method : str
            Simulation method: 'shuffle' or 'bootstrap'

        Returns
        -------
        MonteCarloResults
            Results from all simulations
        """
        if len(returns) == 0:
            raise ValueError("Returns array is empty")

        simulations = []
        final_values = np.zeros(self.n_simulations)
        max_drawdowns = []

        for i in range(self.n_simulations):
            # Generate simulation returns
            if method == 'shuffle':
                sim_returns = np.random.permutation(returns)
            elif method == 'bootstrap':
                sim_returns = self.bootstrap_returns(returns)
            else:
                raise ValueError(f"Unknown method: {method}")

            # Calculate equity curve
            equity_curve = self._calculate_equity_curve(sim_returns)
            simulations.append(equity_curve)
            final_values[i] = equity_curve[-1]

            # Calculate max drawdown
            max_dd = self._calculate_max_drawdown(equity_curve)
            max_drawdowns.append(max_dd)

        # Calculate statistics
        results = self._calculate_statistics(
            simulations,
            final_values,
            max_drawdowns
        )

        return results

    def stress_test(
        self,
        returns: np.ndarray,
        scenario: str = '2008_crisis'
    ) -> MonteCarloResults:
        """
        Run stress test scenario.

        Parameters
        ----------
        returns : np.ndarray
            Base returns to stress test
        scenario : str
            Stress scenario: '2008_crisis', 'flash_crash', 'prolonged_bear', 'black_swan'

        Returns
        -------
        MonteCarloResults
            Results from stress test simulations
        """
        stress_scenarios = {
            '2008_crisis': self._apply_2008_crisis_stress,
            'flash_crash': self._apply_flash_crash_stress,
            'prolonged_bear': self._apply_prolonged_bear_stress,
            'black_swan': self._apply_black_swan_stress
        }

        if scenario not in stress_scenarios:
            raise ValueError(f"Unknown scenario: {scenario}. Available: {list(stress_scenarios.keys())}")

        simulations = []
        final_values = np.zeros(self.n_simulations)
        max_drawdowns = []

        for i in range(self.n_simulations):
            # Apply stress scenario
            stressed_returns = stress_scenarios[scenario](returns.copy())

            # Calculate equity curve
            equity_curve = self._calculate_equity_curve(stressed_returns)
            simulations.append(equity_curve)
            final_values[i] = equity_curve[-1]

            # Calculate max drawdown
            max_dd = self._calculate_max_drawdown(equity_curve)
            max_drawdowns.append(max_dd)

        # Calculate statistics
        results = self._calculate_statistics(
            simulations,
            final_values,
            max_drawdowns
        )

        return results

    def _extract_returns_from_trades(self, trades: List[Dict[str, Any]]) -> np.ndarray:
        """Extract returns from trade dictionaries."""
        returns = []

        for trade in trades:
            if 'return_pct' in trade:
                returns.append(trade['return_pct'])
            elif 'pnl' in trade and 'entry_value' in trade:
                if trade['entry_value'] != 0:
                    ret = (trade['pnl'] / abs(trade['entry_value'])) * 100
                    returns.append(ret)

        return np.array(returns)

    def _calculate_equity_curve(self, returns: np.ndarray) -> np.ndarray:
        """
        Calculate equity curve from returns.

        Parameters
        ----------
        returns : np.ndarray
            Returns in percentage form

        Returns
        -------
        np.ndarray
            Equity curve
        """
        equity = np.zeros(len(returns) + 1)
        equity[0] = self.initial_capital

        for i, ret in enumerate(returns):
            equity[i + 1] = equity[i] * (1 + ret / 100)

        return equity

    def _calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        """Calculate maximum drawdown from equity curve."""
        if len(equity_curve) == 0:
            return 0.0

        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0.0

        return max_drawdown

    def _calculate_statistics(
        self,
        simulations: List[np.ndarray],
        final_values: np.ndarray,
        max_drawdowns: List[float]
    ) -> MonteCarloResults:
        """Calculate statistics from simulations."""
        # Return statistics
        returns_pct = ((final_values - self.initial_capital) / self.initial_capital) * 100

        mean_return = np.mean(returns_pct)
        median_return = np.median(returns_pct)
        std_return = np.std(returns_pct)

        # Percentiles
        percentiles = {
            '5th': np.percentile(final_values, 5),
            '25th': np.percentile(final_values, 25),
            '50th': np.percentile(final_values, 50),
            '75th': np.percentile(final_values, 75),
            '95th': np.percentile(final_values, 95)
        }

        # Confidence intervals
        confidence_95_lower = np.percentile(final_values, 2.5)
        confidence_95_upper = np.percentile(final_values, 97.5)

        # Risk metrics
        probability_of_profit = np.sum(final_values > self.initial_capital) / len(final_values)
        risk_of_ruin = np.sum(final_values < self.initial_capital * 0.5) / len(final_values)

        # Drawdown statistics
        mean_max_drawdown = np.mean(max_drawdowns)

        # Best and worst cases
        best_idx = np.argmax(final_values)
        worst_idx = np.argmin(final_values)
        best_case = simulations[best_idx]
        worst_case = simulations[worst_idx]

        return MonteCarloResults(
            simulations=simulations,
            final_values=final_values,
            percentiles=percentiles,
            mean_return=mean_return,
            median_return=median_return,
            std_return=std_return,
            max_drawdowns=max_drawdowns,
            mean_max_drawdown=mean_max_drawdown,
            worst_case=worst_case,
            best_case=best_case,
            confidence_95_lower=confidence_95_lower,
            confidence_95_upper=confidence_95_upper,
            probability_of_profit=probability_of_profit,
            risk_of_ruin=risk_of_ruin
        )

    def _apply_2008_crisis_stress(self, returns: np.ndarray) -> np.ndarray:
        """
        Apply 2008 financial crisis stress scenario.

        Characteristics:
        - Large negative returns clustered together
        - Increased volatility (3x normal)
        - 50% of returns become negative with -20% to -5% range
        """
        stressed = returns.copy()

        # Increase volatility
        mean_return = np.mean(returns)
        stressed = (stressed - mean_return) * 3.0 + mean_return

        # Apply severe drawdown to 50% of returns
        n_stressed = len(stressed) // 2
        stress_indices = np.random.choice(len(stressed), size=n_stressed, replace=False)

        for idx in stress_indices:
            # Large negative returns
            stressed[idx] = np.random.uniform(-20, -5)

        return stressed

    def _apply_flash_crash_stress(self, returns: np.ndarray) -> np.ndarray:
        """
        Apply flash crash stress scenario.

        Characteristics:
        - Single massive drawdown (-30% to -50%)
        - Quick recovery but not to previous levels
        """
        stressed = returns.copy()

        # Insert flash crash at random point
        crash_idx = np.random.randint(len(stressed) // 4, 3 * len(stressed) // 4)

        # Massive single-period loss
        stressed[crash_idx] = np.random.uniform(-50, -30)

        # Partial recovery in next few periods
        recovery_periods = min(5, len(stressed) - crash_idx - 1)
        for i in range(1, recovery_periods + 1):
            if crash_idx + i < len(stressed):
                stressed[crash_idx + i] = abs(stressed[crash_idx + i]) * 0.5

        return stressed

    def _apply_prolonged_bear_stress(self, returns: np.ndarray) -> np.ndarray:
        """
        Apply prolonged bear market stress scenario.

        Characteristics:
        - Sustained negative bias
        - Lower average returns across all periods
        - Occasional small rallies
        """
        stressed = returns.copy()

        # Shift all returns downward
        stressed = stressed - 5.0

        # Make 70% of returns negative
        n_negative = int(len(stressed) * 0.7)
        negative_indices = np.random.choice(len(stressed), size=n_negative, replace=False)

        for idx in negative_indices:
            if stressed[idx] > 0:
                stressed[idx] = -abs(stressed[idx])

        return stressed

    def _apply_black_swan_stress(self, returns: np.ndarray) -> np.ndarray:
        """
        Apply black swan event stress scenario.

        Characteristics:
        - Extreme tail events (>4 standard deviations)
        - Multiple unexpected large moves
        - Fat tails distribution
        """
        stressed = returns.copy()
        std = np.std(returns)

        # Add 5-10 extreme events (or max available if fewer)
        max_events = min(10, len(stressed))
        min_events = min(5, len(stressed))
        n_events = np.random.randint(min_events, max_events + 1) if max_events > min_events else min_events
        event_indices = np.random.choice(len(stressed), size=n_events, replace=False)

        for idx in event_indices:
            # Extreme moves (4-6 standard deviations)
            magnitude = np.random.uniform(4, 6) * std
            direction = np.random.choice([-1, 1])
            stressed[idx] = direction * magnitude

        return stressed

    def get_summary_statistics(self, results: MonteCarloResults) -> Dict[str, Any]:
        """
        Get summary statistics from Monte Carlo results.

        Parameters
        ----------
        results : MonteCarloResults
            Results from simulation

        Returns
        -------
        dict
            Summary statistics
        """
        return {
            'initial_capital': self.initial_capital,
            'n_simulations': self.n_simulations,
            'mean_final_value': np.mean(results.final_values),
            'median_final_value': np.median(results.final_values),
            'mean_return_pct': results.mean_return,
            'median_return_pct': results.median_return,
            'std_return_pct': results.std_return,
            'best_case_final': np.max(results.final_values),
            'worst_case_final': np.min(results.final_values),
            'percentile_5th': results.percentiles['5th'],
            'percentile_95th': results.percentiles['95th'],
            'confidence_95_lower': results.confidence_95_lower,
            'confidence_95_upper': results.confidence_95_upper,
            'probability_of_profit': results.probability_of_profit,
            'risk_of_ruin': results.risk_of_ruin,
            'mean_max_drawdown': results.mean_max_drawdown,
            'max_drawdown_worst_case': np.max(results.max_drawdowns),
            'max_drawdown_best_case': np.min(results.max_drawdowns)
        }
