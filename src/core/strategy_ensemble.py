"""Strategy ensemble for combining multiple strategies with voting"""

import datetime
import pandas as pd
import backtrader as bt
from typing import List, Dict, Any, Tuple
from collections import defaultdict

from core.data_manager import DataManager
from core.run_strategy import Run_strategy


class StrategyEnsemble:
    """Combine multiple strategies using vote-based signal aggregation"""

    def __init__(self, data_manager: DataManager, strategies: List[Tuple[Any, Dict[str, Any]]],
                 vote_threshold: float = 0.5):
        """
        Initialize strategy ensemble

        Args:
            data_manager: DataManager instance for data retrieval
            strategies: List of (strategy_class, parameters) tuples
            vote_threshold: Minimum fraction of strategies that must agree (0-1)
        """
        self.data_manager = data_manager
        self.strategies = strategies
        self.vote_threshold = vote_threshold

    def run_ensemble(self, ticker: str, start_date: datetime.date,
                    end_date: datetime.date = None, interval: str = '1d') -> Dict[str, Any]:
        """Run ensemble and combine signals via voting"""
        if end_date is None:
            end_date = datetime.date.today()

        individual_results = {}

        for i, (strategy_class, params) in enumerate(self.strategies):
            strategy_name = f"{strategy_class.__name__}_{i}"

            try:
                runner = Run_strategy(params, strategy_class)
                result = runner.runstrat(ticker, start_date, interval, end_date)
                individual_results[strategy_name] = result
            except Exception as e:
                print(f"Error running {strategy_name}: {e}")
                individual_results[strategy_name] = {'error': str(e), 'trades': []}

        ensemble_trades = self._combine_signals(individual_results)

        ensemble_metrics = self._calculate_ensemble_metrics(
            ensemble_trades,
            individual_results
        )

        return {
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date,
            'interval': interval,
            'num_strategies': len(self.strategies),
            'vote_threshold': self.vote_threshold,
            'individual_results': individual_results,
            'ensemble_trades': ensemble_trades,
            'ensemble_metrics': ensemble_metrics
        }

    def _combine_signals(self, individual_results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine trade signals using voting mechanism"""
        all_signals = defaultdict(list)

        for strategy_name, result in individual_results.items():
            if 'error' in result:
                continue

            trades = result.get('trades', [])

            for trade in trades:
                entry_date = trade.get('entry_date')

                if entry_date:
                    if isinstance(entry_date, str):
                        entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d').date()

                    all_signals[entry_date].append({
                        'strategy': strategy_name,
                        'trade': trade
                    })

        ensemble_trades = []
        required_votes = max(1, int(len(self.strategies) * self.vote_threshold))

        for entry_date, signals in sorted(all_signals.items()):
            if len(signals) >= required_votes:
                avg_entry_price = sum(s['trade']['entry_price'] for s in signals) / len(signals)
                avg_exit_price = sum(s['trade']['exit_price'] for s in signals) / len(signals)
                avg_pnl = sum(s['trade']['pnl'] for s in signals) / len(signals)

                ensemble_trade = {
                    'entry_date': entry_date,
                    'exit_date': signals[0]['trade']['exit_date'],
                    'entry_price': avg_entry_price,
                    'exit_price': avg_exit_price,
                    'pnl': avg_pnl,
                    'votes': len(signals),
                    'strategies': [s['strategy'] for s in signals],
                    'type': signals[0]['trade'].get('type', 'LONG')
                }

                ensemble_trades.append(ensemble_trade)

        return ensemble_trades

    def _calculate_ensemble_metrics(self, ensemble_trades: List[Dict[str, Any]],
                                    individual_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for the ensemble"""
        if not ensemble_trades:
            return {
                'total_trades': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_pnl_per_trade': 0,
                'agreement_rate': 0
            }

        total_pnl = sum(trade['pnl'] for trade in ensemble_trades)
        winning_trades = sum(1 for trade in ensemble_trades if trade['pnl'] > 0)
        win_rate = (winning_trades / len(ensemble_trades)) * 100 if ensemble_trades else 0

        avg_votes = sum(trade['votes'] for trade in ensemble_trades) / len(ensemble_trades)
        agreement_rate = avg_votes / len(self.strategies) if self.strategies else 0

        individual_metrics = {}
        for strategy_name, result in individual_results.items():
            if 'error' not in result:
                individual_metrics[strategy_name] = {
                    'return_pct': result.get('return_pct', 0),
                    'total_trades': result.get('total_trades', 0),
                    'sharpe_ratio': result.get('sharpe_ratio')
                }

        return {
            'total_trades': len(ensemble_trades),
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'avg_pnl_per_trade': total_pnl / len(ensemble_trades) if ensemble_trades else 0,
            'agreement_rate': agreement_rate,
            'avg_votes_per_trade': avg_votes,
            'individual_metrics': individual_metrics
        }

    def run_with_weights(self, ticker: str, start_date: datetime.date,
                        end_date: datetime.date = None, interval: str = '1d',
                        weights: List[float] = None) -> Dict[str, Any]:
        """Run ensemble with weighted voting"""
        if weights is None:
            weights = [1.0] * len(self.strategies)

        if len(weights) != len(self.strategies):
            raise ValueError("Number of weights must match number of strategies")

        if end_date is None:
            end_date = datetime.date.today()

        individual_results = {}

        for i, (strategy_class, params) in enumerate(self.strategies):
            strategy_name = f"{strategy_class.__name__}_{i}"

            try:
                runner = Run_strategy(params, strategy_class)
                result = runner.runstrat(ticker, start_date, interval, end_date)
                individual_results[strategy_name] = result
            except Exception as e:
                individual_results[strategy_name] = {'error': str(e), 'trades': []}

        ensemble_trades = self._combine_signals_weighted(individual_results, weights)

        ensemble_metrics = self._calculate_ensemble_metrics(ensemble_trades, individual_results)

        return {
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date,
            'interval': interval,
            'num_strategies': len(self.strategies),
            'weights': weights,
            'individual_results': individual_results,
            'ensemble_trades': ensemble_trades,
            'ensemble_metrics': ensemble_metrics
        }

    def _combine_signals_weighted(self, individual_results: Dict[str, Dict[str, Any]],
                                  weights: List[float]) -> List[Dict[str, Any]]:
        """Combine signals using weighted voting"""
        all_signals = defaultdict(list)

        for i, (strategy_name, result) in enumerate(individual_results.items()):
            if 'error' in result:
                continue

            trades = result.get('trades', [])
            weight = weights[i] if i < len(weights) else 1.0

            for trade in trades:
                entry_date = trade.get('entry_date')

                if entry_date:
                    if isinstance(entry_date, str):
                        entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d').date()

                    all_signals[entry_date].append({
                        'strategy': strategy_name,
                        'trade': trade,
                        'weight': weight
                    })

        ensemble_trades = []
        total_weight = sum(weights)
        required_weight = total_weight * self.vote_threshold

        for entry_date, signals in sorted(all_signals.items()):
            signal_weight = sum(s['weight'] for s in signals)

            if signal_weight >= required_weight:
                weighted_entry = sum(s['trade']['entry_price'] * s['weight'] for s in signals) / signal_weight
                weighted_exit = sum(s['trade']['exit_price'] * s['weight'] for s in signals) / signal_weight
                weighted_pnl = sum(s['trade']['pnl'] * s['weight'] for s in signals) / signal_weight

                ensemble_trade = {
                    'entry_date': entry_date,
                    'exit_date': signals[0]['trade']['exit_date'],
                    'entry_price': weighted_entry,
                    'exit_price': weighted_exit,
                    'pnl': weighted_pnl,
                    'total_weight': signal_weight,
                    'strategies': [s['strategy'] for s in signals],
                    'type': signals[0]['trade'].get('type', 'LONG')
                }

                ensemble_trades.append(ensemble_trade)

        return ensemble_trades
