"""Generate comparison tables for multiple backtest results"""

import pandas as pd
from typing import List, Dict, Any, Optional
from tabulate import tabulate


class ComparisonTableGenerator:
    """Generate comparison tables for strategy performance"""

    def __init__(self, results: List[Dict[str, Any]], result_names: Optional[List[str]] = None):
        """Initialize comparison table generator"""
        self.results = results
        self.result_names = result_names or [f"Result_{i+1}" for i in range(len(results))]

    def generate_basic_comparison(self) -> pd.DataFrame:
        """Generate basic performance comparison table"""
        data = []

        for name, result in zip(self.result_names, self.results):
            row = {
                'Strategy': name,
                'Return %': result.get('return_pct', 0),
                'Total Trades': result.get('total_trades', 0),
                'Sharpe Ratio': result.get('sharpe_ratio'),
                'Max Drawdown %': result.get('max_drawdown', 0)
            }
            data.append(row)

        df = pd.DataFrame(data)

        df = df.sort_values('Return %', ascending=False)

        return df

    def generate_advanced_comparison(self) -> pd.DataFrame:
        """Generate advanced performance comparison with all metrics"""
        data = []

        for name, result in zip(self.result_names, self.results):
            advanced = result.get('advanced_metrics', {})

            row = {
                'Strategy': name,
                'Return %': result.get('return_pct', 0),
                'Sharpe': result.get('sharpe_ratio'),
                'Sortino': advanced.get('sortino_ratio'),
                'Calmar': advanced.get('calmar_ratio'),
                'Win Rate %': advanced.get('win_rate', 0),
                'Profit Factor': advanced.get('profit_factor'),
                'Payoff Ratio': advanced.get('payoff_ratio'),
                'Total Trades': result.get('total_trades', 0),
                'Max DD %': result.get('max_drawdown', 0),
                'Avg Win': advanced.get('avg_win', 0),
                'Avg Loss': advanced.get('avg_loss', 0),
                'Expectancy': advanced.get('expectancy', 0)
            }
            data.append(row)

        df = pd.DataFrame(data)

        df = df.sort_values('Return %', ascending=False)

        return df

    def generate_risk_metrics_comparison(self) -> pd.DataFrame:
        """Generate risk-focused comparison table"""
        data = []

        for name, result in zip(self.result_names, self.results):
            advanced = result.get('advanced_metrics', {})

            row = {
                'Strategy': name,
                'Max Drawdown %': result.get('max_drawdown', 0),
                'Sharpe Ratio': result.get('sharpe_ratio'),
                'Sortino Ratio': advanced.get('sortino_ratio'),
                'Calmar Ratio': advanced.get('calmar_ratio'),
                'Max Consecutive Losses': advanced.get('max_consecutive_losses', 0),
                'Largest Loss': advanced.get('largest_loss', 0)
            }
            data.append(row)

        df = pd.DataFrame(data)

        df = df.sort_values('Max Drawdown %', ascending=True)

        return df

    def generate_trade_analysis_comparison(self) -> pd.DataFrame:
        """Generate trade-focused comparison table"""
        data = []

        for name, result in zip(self.result_names, self.results):
            advanced = result.get('advanced_metrics', {})

            row = {
                'Strategy': name,
                'Total Trades': result.get('total_trades', 0),
                'Win Rate %': advanced.get('win_rate', 0),
                'Profit Factor': advanced.get('profit_factor'),
                'Payoff Ratio': advanced.get('payoff_ratio'),
                'Avg Win': advanced.get('avg_win', 0),
                'Avg Loss': advanced.get('avg_loss', 0),
                'Largest Win': advanced.get('largest_win', 0),
                'Largest Loss': advanced.get('largest_loss', 0),
                'Max Consecutive Wins': advanced.get('max_consecutive_wins', 0),
                'Max Consecutive Losses': advanced.get('max_consecutive_losses', 0)
            }
            data.append(row)

        df = pd.DataFrame(data)

        df = df.sort_values('Win Rate %', ascending=False)

        return df

    def print_comparison(self, comparison_type: str = 'basic') -> None:
        """Print formatted comparison table to console"""
        if comparison_type == 'basic':
            df = self.generate_basic_comparison()
        elif comparison_type == 'advanced':
            df = self.generate_advanced_comparison()
        elif comparison_type == 'risk':
            df = self.generate_risk_metrics_comparison()
        elif comparison_type == 'trades':
            df = self.generate_trade_analysis_comparison()
        else:
            raise ValueError(f"Unknown comparison type: {comparison_type}")

        print("\n" + "="*100)
        print(f"{comparison_type.upper()} COMPARISON TABLE")
        print("="*100)
        print(tabulate(df, headers='keys', tablefmt='grid', floatfmt='.2f', showindex=False))
        print("="*100 + "\n")

    def highlight_best_worst(self, df: pd.DataFrame, metric: str) -> pd.DataFrame:
        """Add best/worst indicators to dataframe"""
        df = df.copy()

        if metric in df.columns:
            max_val = df[metric].max()
            min_val = df[metric].min()

            df[f'{metric}_Rank'] = df[metric].rank(ascending=False).astype(int)

            df['Highlight'] = ''
            df.loc[df[metric] == max_val, 'Highlight'] = 'BEST'
            df.loc[df[metric] == min_val, 'Highlight'] = 'WORST'

        return df

    def generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate summary statistics across all results"""
        returns = [r.get('return_pct', 0) for r in self.results]
        sharpes = [r.get('sharpe_ratio') for r in self.results if r.get('sharpe_ratio') is not None]

        return {
            'num_strategies': len(self.results),
            'avg_return': sum(returns) / len(returns) if returns else 0,
            'best_return': max(returns) if returns else 0,
            'worst_return': min(returns) if returns else 0,
            'avg_sharpe': sum(sharpes) / len(sharpes) if sharpes else None,
            'positive_returns': sum(1 for r in returns if r > 0),
            'negative_returns': sum(1 for r in returns if r < 0)
        }

    @staticmethod
    def compare_walk_forward_results(wf_results: Dict[str, Any]) -> pd.DataFrame:
        """Generate comparison table for walk-forward optimization results"""
        periods = wf_results.get('periods', [])

        if not periods:
            return pd.DataFrame()

        data = []

        for period in periods:
            row = {
                'Period': period['period'],
                'Train Start': period['train_start'],
                'Test End': period['test_end'],
                'Train Return %': period['train_return'],
                'Test Return %': period['test_return'],
                'Test Sharpe': period.get('test_sharpe'),
                'Test Max DD %': period.get('test_max_dd'),
                'Test Trades': period.get('test_trades', 0)
            }
            data.append(row)

        df = pd.DataFrame(data)

        return df

    @staticmethod
    def compare_ensemble_results(ensemble_results: Dict[str, Any]) -> pd.DataFrame:
        """Generate comparison table for ensemble results"""
        individual = ensemble_results.get('individual_results', {})

        if not individual:
            return pd.DataFrame()

        data = []

        for strategy_name, result in individual.items():
            if 'error' in result:
                continue

            row = {
                'Strategy': strategy_name,
                'Return %': result.get('return_pct', 0),
                'Total Trades': result.get('total_trades', 0),
                'Sharpe Ratio': result.get('sharpe_ratio')
            }
            data.append(row)

        ensemble_metrics = ensemble_results.get('ensemble_metrics', {})
        data.append({
            'Strategy': 'ENSEMBLE',
            'Return %': None,
            'Total Trades': ensemble_metrics.get('total_trades', 0),
            'Sharpe Ratio': None
        })

        df = pd.DataFrame(data)

        return df

    def export_to_csv(self, filename: str, comparison_type: str = 'advanced') -> None:
        """Export comparison table to CSV file"""
        if comparison_type == 'basic':
            df = self.generate_basic_comparison()
        elif comparison_type == 'advanced':
            df = self.generate_advanced_comparison()
        elif comparison_type == 'risk':
            df = self.generate_risk_metrics_comparison()
        elif comparison_type == 'trades':
            df = self.generate_trade_analysis_comparison()
        else:
            raise ValueError(f"Unknown comparison type: {comparison_type}")

        df.to_csv(filename, index=False)
        print(f"Comparison table exported to {filename}")
