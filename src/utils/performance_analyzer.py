import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import datetime


class PerformanceAnalyzer:

    def __init__(self, trades: List[Dict[str, Any]], start_value: float, end_value: float,
                 equity_curve: Optional[pd.Series] = None):
        self.trades = trades
        self.start_value = start_value
        self.end_value = end_value
        self.equity_curve = equity_curve

    def calculate_all_metrics(self) -> Dict[str, Any]:
        if not self.trades:
            return self._get_empty_metrics()

        return {
            'win_rate': self.calculate_win_rate(),
            'profit_factor': self.calculate_profit_factor(),
            'payoff_ratio': self.calculate_payoff_ratio(),
            'calmar_ratio': self.calculate_calmar_ratio(),
            'sortino_ratio': self.calculate_sortino_ratio(),
            'max_consecutive_wins': self.calculate_max_consecutive_wins(),
            'max_consecutive_losses': self.calculate_max_consecutive_losses(),
            'avg_win': self.calculate_avg_win(),
            'avg_loss': self.calculate_avg_loss(),
            'largest_win': self.calculate_largest_win(),
            'largest_loss': self.calculate_largest_loss(),
            'avg_trade_duration': self.calculate_avg_trade_duration(),
            'recovery_periods': self.calculate_recovery_periods(),
            'expectancy': self.calculate_expectancy()
        }

    def calculate_win_rate(self) -> float:
        if not self.trades:
            return 0.0

        winning_trades = sum(1 for trade in self.trades if trade.get('pnl', 0) > 0)
        return (winning_trades / len(self.trades)) * 100

    def calculate_profit_factor(self) -> Optional[float]:
        if not self.trades:
            return None

        gross_profit = sum(trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) > 0)
        gross_loss = abs(sum(trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) < 0))

        if gross_loss == 0 or gross_profit == 0:
            return None

        return gross_profit / gross_loss

    def calculate_payoff_ratio(self) -> Optional[float]:
        avg_win = self.calculate_avg_win()
        avg_loss = abs(self.calculate_avg_loss())

        if avg_loss == 0 or avg_win == 0:
            return None

        return avg_win / avg_loss

    def calculate_calmar_ratio(self) -> Optional[float]:
        if not self.trades or self.equity_curve is None or len(self.equity_curve) == 0:
            return None

        annual_return = self._calculate_annual_return()
        max_dd = self._calculate_max_drawdown()

        if max_dd == 0:
            return None

        return annual_return / abs(max_dd)

    def calculate_sortino_ratio(self, risk_free_rate: float = 0.0) -> Optional[float]:
        if self.equity_curve is None or len(self.equity_curve) == 0:
            return None

        returns = self.equity_curve.pct_change().dropna()

        if len(returns) == 0:
            return None

        excess_returns = returns - risk_free_rate
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return None

        downside_deviation = np.sqrt(np.mean(downside_returns ** 2))

        if downside_deviation == 0:
            return None

        return np.mean(excess_returns) / downside_deviation

    def calculate_max_consecutive_wins(self) -> int:
        if not self.trades:
            return 0

        max_streak = 0
        current_streak = 0

        for trade in self.trades:
            if trade.get('pnl', 0) > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

        return max_streak

    def calculate_max_consecutive_losses(self) -> int:
        if not self.trades:
            return 0

        max_streak = 0
        current_streak = 0

        for trade in self.trades:
            if trade.get('pnl', 0) < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

        return max_streak

    def calculate_avg_win(self) -> float:
        if not self.trades:
            return 0.0

        winning_trades = [trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) > 0]

        if not winning_trades:
            return 0.0

        return sum(winning_trades) / len(winning_trades)

    def calculate_avg_loss(self) -> float:
        if not self.trades:
            return 0.0

        losing_trades = [trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) < 0]

        if not losing_trades:
            return 0.0

        return sum(losing_trades) / len(losing_trades)

    def calculate_largest_win(self) -> float:
        if not self.trades:
            return 0.0

        winning_trades = [trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) > 0]

        if not winning_trades:
            return 0.0

        return max(winning_trades)

    def calculate_largest_loss(self) -> float:
        if not self.trades:
            return 0.0

        losing_trades = [trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) < 0]

        if not losing_trades:
            return 0.0

        return min(losing_trades)

    def calculate_avg_trade_duration(self) -> Optional[float]:
        if not self.trades:
            return None

        durations = []

        for trade in self.trades:
            entry_date = trade.get('entry_date')
            exit_date = trade.get('exit_date')

            if entry_date and exit_date:
                if isinstance(entry_date, str):
                    entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d').date()
                if isinstance(exit_date, str):
                    exit_date = datetime.datetime.strptime(exit_date, '%Y-%m-%d').date()

                duration = (exit_date - entry_date).days
                durations.append(duration)

        if not durations:
            return None

        return sum(durations) / len(durations)

    def calculate_recovery_periods(self) -> List[Dict[str, Any]]:
        if self.equity_curve is None or len(self.equity_curve) == 0:
            return []

        equity = self.equity_curve.values
        peak = equity[0]
        recovery_periods = []
        drawdown_start = None

        for i, value in enumerate(equity):
            if value > peak:
                if drawdown_start is not None:
                    recovery_periods.append({
                        'drawdown_start_idx': drawdown_start,
                        'recovery_idx': i,
                        'recovery_days': i - drawdown_start,
                        'drawdown_pct': ((peak - equity[drawdown_start]) / peak) * 100
                    })
                    drawdown_start = None
                peak = value
            elif value < peak and drawdown_start is None:
                drawdown_start = i

        return recovery_periods

    def calculate_expectancy(self) -> float:
        if not self.trades:
            return 0.0

        win_rate = self.calculate_win_rate() / 100
        avg_win = self.calculate_avg_win()
        avg_loss = abs(self.calculate_avg_loss())

        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    def _calculate_annual_return(self) -> float:
        if not self.trades:
            return 0.0

        first_trade = self.trades[0]
        last_trade = self.trades[-1]

        start_date = first_trade.get('entry_date')
        end_date = last_trade.get('exit_date')

        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        if not start_date or not end_date:
            return 0.0

        days = (end_date - start_date).days

        if days <= 0:
            return 0.0

        total_return = (self.end_value - self.start_value) / self.start_value
        years = days / 365.25

        annual_return = ((1 + total_return) ** (1 / years) - 1) * 100

        return annual_return

    def _calculate_max_drawdown(self) -> float:
        if self.equity_curve is None or len(self.equity_curve) == 0:
            return 0.0

        equity = self.equity_curve.values
        peak = equity[0]
        max_dd = 0

        for value in equity:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            max_dd = max(max_dd, dd)

        return max_dd

    def _get_empty_metrics(self) -> Dict[str, Any]:
        return {
            'win_rate': 0.0,
            'profit_factor': None,
            'payoff_ratio': None,
            'calmar_ratio': None,
            'sortino_ratio': None,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'avg_trade_duration': None,
            'recovery_periods': [],
            'expectancy': 0.0
        }

    @staticmethod
    def create_equity_curve(trades: List[Dict[str, Any]], start_value: float) -> pd.Series:
        if not trades:
            return pd.Series([start_value])

        equity_values = [start_value]
        current_equity = start_value

        for trade in trades:
            current_equity += trade.get('pnl', 0)
            equity_values.append(current_equity)

        return pd.Series(equity_values)
