"""
Risk Manager Module

Implements comprehensive risk management including:
- Maximum portfolio heat (total risk exposure) limits
- Maximum drawdown stops
- Position-level risk controls
- Real-time risk monitoring during backtests
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime


class RiskManager:
    """
    Manages risk controls for trading strategies including portfolio heat,
    drawdown limits, and position sizing constraints.
    """

    def __init__(
        self,
        max_portfolio_heat: float = 0.20,
        max_drawdown_pct: float = 0.25,
        max_position_size_pct: float = 0.10,
        max_leverage: float = 1.0,
        enable_trailing_stop: bool = False,
        trailing_stop_pct: float = 0.15
    ):
        """
        Initialize Risk Manager.

        Parameters
        ----------
        max_portfolio_heat : float
            Maximum total risk exposure as fraction of portfolio (default: 0.20 = 20%)
        max_drawdown_pct : float
            Maximum drawdown before stopping trading (default: 0.25 = 25%)
        max_position_size_pct : float
            Maximum single position size as fraction of portfolio (default: 0.10 = 10%)
        max_leverage : float
            Maximum leverage allowed (default: 1.0 = no leverage)
        enable_trailing_stop : bool
            Enable trailing drawdown stop (default: False)
        trailing_stop_pct : float
            Trailing stop distance from peak (default: 0.15 = 15%)
        """
        self.max_portfolio_heat = max_portfolio_heat
        self.max_drawdown_pct = max_drawdown_pct
        self.max_position_size_pct = max_position_size_pct
        self.max_leverage = max_leverage
        self.enable_trailing_stop = enable_trailing_stop
        self.trailing_stop_pct = trailing_stop_pct

        # Internal state
        self.initial_capital = None
        self.peak_equity = None
        self.current_equity = None
        self.current_drawdown = 0.0
        self.max_drawdown_reached = 0.0
        self.trading_halted = False
        self.halt_reason = None
        self.open_positions = {}
        self.equity_history = []
        self.risk_events = []

    def initialize(self, initial_capital: float):
        """Initialize risk manager with starting capital."""
        self.initial_capital = initial_capital
        self.peak_equity = initial_capital
        self.current_equity = initial_capital
        self.current_drawdown = 0.0
        self.max_drawdown_reached = 0.0
        self.trading_halted = False
        self.halt_reason = None
        self.open_positions = {}
        self.equity_history = [(datetime.now(), initial_capital)]
        self.risk_events = []

    def update_equity(self, current_equity: float, timestamp: Optional[datetime] = None):
        """
        Update current equity and check risk limits.

        Parameters
        ----------
        current_equity : float
            Current portfolio equity value
        timestamp : datetime, optional
            Timestamp for the equity update

        Returns
        -------
        bool
            True if trading should continue, False if risk limits breached
        """
        if timestamp is None:
            timestamp = datetime.now()

        self.current_equity = current_equity
        self.equity_history.append((timestamp, current_equity))

        # Update peak equity
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        # Calculate current drawdown
        if self.peak_equity > 0:
            self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        else:
            self.current_drawdown = 0.0

        # Track maximum drawdown reached
        if self.current_drawdown > self.max_drawdown_reached:
            self.max_drawdown_reached = self.current_drawdown

        # Check drawdown limit
        if self.current_drawdown >= self.max_drawdown_pct:
            self.trading_halted = True
            self.halt_reason = f"Maximum drawdown limit breached: {self.current_drawdown:.2%} >= {self.max_drawdown_pct:.2%}"
            self.risk_events.append({
                'timestamp': timestamp,
                'event_type': 'DRAWDOWN_LIMIT_BREACHED',
                'drawdown': self.current_drawdown,
                'equity': current_equity,
                'peak_equity': self.peak_equity
            })
            return False

        # Check trailing stop if enabled
        if self.enable_trailing_stop:
            trailing_stop_level = self.peak_equity * (1 - self.trailing_stop_pct)
            if current_equity <= trailing_stop_level:
                self.trading_halted = True
                self.halt_reason = f"Trailing stop triggered: ${current_equity:,.2f} <= ${trailing_stop_level:,.2f}"
                self.risk_events.append({
                    'timestamp': timestamp,
                    'event_type': 'TRAILING_STOP_TRIGGERED',
                    'drawdown': self.current_drawdown,
                    'equity': current_equity,
                    'peak_equity': self.peak_equity,
                    'stop_level': trailing_stop_level
                })
                return False

        return True

    def can_open_position(
        self,
        position_size: float,
        stop_loss_pct: Optional[float] = None
    ) -> bool:
        """
        Check if a new position can be opened within risk limits.

        Parameters
        ----------
        position_size : float
            Size of the proposed position in dollars
        stop_loss_pct : float, optional
            Stop loss percentage for risk calculation

        Returns
        -------
        bool
            True if position can be opened, False otherwise
        """
        if self.trading_halted:
            return False

        if self.current_equity <= 0:
            return False

        # Check position size limit
        position_pct = position_size / self.current_equity
        if position_pct > self.max_position_size_pct:
            self.risk_events.append({
                'timestamp': datetime.now(),
                'event_type': 'POSITION_SIZE_LIMIT',
                'position_size': position_size,
                'position_pct': position_pct,
                'max_allowed': self.max_position_size_pct
            })
            return False

        # Check portfolio heat if stop loss provided
        if stop_loss_pct is not None:
            position_risk = position_size * abs(stop_loss_pct)
            current_heat = self.calculate_portfolio_heat()
            new_heat = (current_heat + position_risk) / self.current_equity

            if new_heat > self.max_portfolio_heat:
                self.risk_events.append({
                    'timestamp': datetime.now(),
                    'event_type': 'PORTFOLIO_HEAT_LIMIT',
                    'current_heat': current_heat / self.current_equity,
                    'new_heat': new_heat,
                    'max_allowed': self.max_portfolio_heat
                })
                return False

        # Check leverage
        total_exposure = sum(pos['size'] for pos in self.open_positions.values())
        total_exposure += position_size
        leverage = total_exposure / self.current_equity

        if leverage > self.max_leverage:
            self.risk_events.append({
                'timestamp': datetime.now(),
                'event_type': 'LEVERAGE_LIMIT',
                'leverage': leverage,
                'max_allowed': self.max_leverage
            })
            return False

        return True

    def add_position(
        self,
        position_id: str,
        size: float,
        entry_price: float,
        stop_loss: Optional[float] = None
    ):
        """
        Register a new open position.

        Parameters
        ----------
        position_id : str
            Unique identifier for the position
        size : float
            Position size in dollars
        entry_price : float
            Entry price
        stop_loss : float, optional
            Stop loss price
        """
        self.open_positions[position_id] = {
            'size': size,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'timestamp': datetime.now()
        }

    def remove_position(self, position_id: str):
        """Remove a closed position."""
        if position_id in self.open_positions:
            del self.open_positions[position_id]

    def calculate_portfolio_heat(self) -> float:
        """
        Calculate total portfolio heat (risk exposure).

        Returns
        -------
        float
            Total risk exposure in dollars
        """
        total_risk = 0.0

        for pos in self.open_positions.values():
            if pos['stop_loss'] is not None:
                risk_per_share = abs(pos['entry_price'] - pos['stop_loss'])
                shares = pos['size'] / pos['entry_price']
                position_risk = risk_per_share * shares
                total_risk += position_risk
            else:
                # Use default 2% risk if no stop loss defined
                total_risk += pos['size'] * 0.02

        return total_risk

    def get_risk_adjusted_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_per_trade_pct: float = 0.02
    ) -> float:
        """
        Calculate position size based on risk per trade.

        Parameters
        ----------
        entry_price : float
            Planned entry price
        stop_loss : float
            Planned stop loss price
        risk_per_trade_pct : float
            Risk per trade as fraction of equity (default: 0.02 = 2%)

        Returns
        -------
        float
            Recommended position size in dollars
        """
        if self.current_equity <= 0 or entry_price <= 0:
            return 0.0

        risk_amount = self.current_equity * risk_per_trade_pct
        risk_per_share = abs(entry_price - stop_loss)

        if risk_per_share == 0:
            return 0.0

        shares = risk_amount / risk_per_share
        position_size = shares * entry_price

        # Enforce maximum position size
        max_size = self.current_equity * self.max_position_size_pct
        position_size = min(position_size, max_size)

        return position_size

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get risk management statistics.

        Returns
        -------
        dict
            Risk statistics including drawdown, heat, violations
        """
        return {
            'initial_capital': self.initial_capital,
            'current_equity': self.current_equity,
            'peak_equity': self.peak_equity,
            'current_drawdown': self.current_drawdown,
            'max_drawdown_reached': self.max_drawdown_reached,
            'max_drawdown_limit': self.max_drawdown_pct,
            'trading_halted': self.trading_halted,
            'halt_reason': self.halt_reason,
            'portfolio_heat': self.calculate_portfolio_heat(),
            'portfolio_heat_pct': self.calculate_portfolio_heat() / self.current_equity if self.current_equity > 0 else 0,
            'max_portfolio_heat': self.max_portfolio_heat,
            'open_positions_count': len(self.open_positions),
            'risk_events_count': len(self.risk_events),
            'risk_events': self.risk_events
        }

    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get equity curve with drawdown data.

        Returns
        -------
        pd.DataFrame
            DataFrame with timestamp, equity, peak, and drawdown columns
        """
        if not self.equity_history:
            return pd.DataFrame()

        df = pd.DataFrame(self.equity_history, columns=['timestamp', 'equity'])
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['peak'] - df['equity']) / df['peak']
        df['drawdown_pct'] = df['drawdown'] * 100

        return df

    def reset(self):
        """Reset risk manager to initial state."""
        if self.initial_capital is not None:
            self.initialize(self.initial_capital)
