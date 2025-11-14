"""
Position Sizing Module

Implements various position sizing strategies including:
- Fixed position sizing
- Percentage-based sizing
- ATR-based volatility sizing
- Kelly Criterion
"""

from typing import Optional
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class PositionSizer(ABC):
    """Base class for position sizing strategies."""

    @abstractmethod
    def calculate_position_size(
        self,
        equity: float,
        price: float,
        **kwargs
    ) -> float:
        """
        Calculate position size.

        Parameters
        ----------
        equity : float
            Current account equity
        price : float
            Current price of the security
        **kwargs
            Additional parameters specific to sizing method

        Returns
        -------
        float
            Number of shares to trade
        """
        pass


class FixedPositionSizer(PositionSizer):
    """Fixed number of shares per trade."""

    def __init__(self, shares: int = 100):
        """
        Initialize fixed position sizer.

        Parameters
        ----------
        shares : int
            Fixed number of shares per trade
        """
        self.shares = shares

    def calculate_position_size(
        self,
        equity: float,
        price: float,
        **kwargs
    ) -> float:
        """Calculate fixed position size."""
        return self.shares


class PercentagePositionSizer(PositionSizer):
    """Percentage of equity position sizing."""

    def __init__(self, percentage: float = 0.10):
        """
        Initialize percentage position sizer.

        Parameters
        ----------
        percentage : float
            Percentage of equity to allocate per trade (default: 0.10 = 10%)
        """
        self.percentage = percentage

    def calculate_position_size(
        self,
        equity: float,
        price: float,
        **kwargs
    ) -> float:
        """Calculate position size based on percentage of equity."""
        if price <= 0:
            return 0

        position_value = equity * self.percentage
        shares = int(position_value / price)
        return shares


class ATRPositionSizer(PositionSizer):
    """
    ATR-based volatility-adjusted position sizing.

    Uses Average True Range (ATR) to adjust position size based on volatility.
    Higher volatility = smaller position size to maintain consistent risk.
    """

    def __init__(
        self,
        risk_per_trade: float = 0.02,
        atr_multiplier: float = 2.0,
        atr_period: int = 14,
        max_position_pct: float = 0.20
    ):
        """
        Initialize ATR-based position sizer.

        Parameters
        ----------
        risk_per_trade : float
            Risk per trade as fraction of equity (default: 0.02 = 2%)
        atr_multiplier : float
            ATR multiplier for stop loss distance (default: 2.0)
        atr_period : int
            Period for ATR calculation (default: 14)
        max_position_pct : float
            Maximum position size as fraction of equity (default: 0.20 = 20%)
        """
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier = atr_multiplier
        self.atr_period = atr_period
        self.max_position_pct = max_position_pct

    def calculate_atr(self, data: pd.DataFrame) -> float:
        """
        Calculate Average True Range.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame with High, Low, Close columns

        Returns
        -------
        float
            Current ATR value
        """
        if len(data) < 2:
            return 0.0

        # True Range calculation
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # Average True Range
        atr = true_range.rolling(window=self.atr_period).mean()

        return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.0

    def calculate_position_size(
        self,
        equity: float,
        price: float,
        data: Optional[pd.DataFrame] = None,
        atr: Optional[float] = None,
        **kwargs
    ) -> float:
        """
        Calculate volatility-adjusted position size using ATR.

        Parameters
        ----------
        equity : float
            Current account equity
        price : float
            Current price
        data : pd.DataFrame, optional
            Price data for ATR calculation (must have High, Low, Close)
        atr : float, optional
            Pre-calculated ATR value (if not provided, will calculate from data)
        **kwargs
            Additional parameters

        Returns
        -------
        float
            Number of shares to trade
        """
        if equity <= 0 or price <= 0:
            return 0

        # Get ATR value
        if atr is None:
            if data is None or len(data) < self.atr_period:
                # Fallback to percentage-based sizing if no ATR available
                position_value = equity * 0.10
                return int(position_value / price)

            atr = self.calculate_atr(data)

        if atr <= 0:
            # Fallback if ATR is invalid
            position_value = equity * 0.10
            return int(position_value / price)

        # Calculate position size based on ATR
        # Risk amount = equity * risk_per_trade
        # Stop distance = ATR * atr_multiplier
        # Shares = risk_amount / stop_distance
        risk_amount = equity * self.risk_per_trade
        stop_distance = atr * self.atr_multiplier

        shares = risk_amount / stop_distance

        # Apply maximum position size limit
        max_shares = int((equity * self.max_position_pct) / price)
        shares = min(shares, max_shares)

        return int(shares)


class KellyPositionSizer(PositionSizer):
    """
    Kelly Criterion position sizing.

    Calculates optimal position size based on win rate and win/loss ratio.
    """

    def __init__(
        self,
        win_rate: float = 0.55,
        avg_win_loss_ratio: float = 1.5,
        kelly_fraction: float = 0.25,
        max_position_pct: float = 0.25
    ):
        """
        Initialize Kelly Criterion position sizer.

        Parameters
        ----------
        win_rate : float
            Historical win rate (default: 0.55 = 55%)
        avg_win_loss_ratio : float
            Average win / average loss ratio (default: 1.5)
        kelly_fraction : float
            Fraction of full Kelly to use (default: 0.25 = quarter Kelly)
        max_position_pct : float
            Maximum position size as fraction of equity (default: 0.25 = 25%)
        """
        self.win_rate = win_rate
        self.avg_win_loss_ratio = avg_win_loss_ratio
        self.kelly_fraction = kelly_fraction
        self.max_position_pct = max_position_pct

    def calculate_kelly_percentage(self) -> float:
        """
        Calculate Kelly percentage.

        Kelly % = W - [(1 - W) / R]
        Where W = win rate, R = avg win / avg loss ratio

        Returns
        -------
        float
            Kelly percentage (fraction of equity to risk)
        """
        if self.avg_win_loss_ratio <= 0:
            return 0.0

        kelly_pct = self.win_rate - ((1 - self.win_rate) / self.avg_win_loss_ratio)

        # Apply Kelly fraction (conservative approach)
        kelly_pct *= self.kelly_fraction

        # Ensure non-negative and within limits
        kelly_pct = max(0.0, min(kelly_pct, self.max_position_pct))

        return kelly_pct

    def calculate_position_size(
        self,
        equity: float,
        price: float,
        **kwargs
    ) -> float:
        """Calculate position size using Kelly Criterion."""
        if equity <= 0 or price <= 0:
            return 0

        kelly_pct = self.calculate_kelly_percentage()
        position_value = equity * kelly_pct
        shares = int(position_value / price)

        return shares


class RiskParityPositionSizer(PositionSizer):
    """
    Risk parity position sizing.

    Allocates position size inversely proportional to volatility,
    ensuring equal risk contribution across positions.
    """

    def __init__(
        self,
        target_volatility: float = 0.15,
        lookback_period: int = 20,
        max_position_pct: float = 0.20
    ):
        """
        Initialize risk parity position sizer.

        Parameters
        ----------
        target_volatility : float
            Target portfolio volatility (default: 0.15 = 15%)
        lookback_period : int
            Period for volatility calculation (default: 20)
        max_position_pct : float
            Maximum position size as fraction of equity (default: 0.20 = 20%)
        """
        self.target_volatility = target_volatility
        self.lookback_period = lookback_period
        self.max_position_pct = max_position_pct

    def calculate_volatility(self, data: pd.DataFrame) -> float:
        """
        Calculate historical volatility (annualized).

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame with Close prices

        Returns
        -------
        float
            Annualized volatility
        """
        if len(data) < 2:
            return self.target_volatility

        returns = data['Close'].pct_change().dropna()

        if len(returns) < self.lookback_period:
            volatility = returns.std()
        else:
            volatility = returns.tail(self.lookback_period).std()

        # Annualize (assuming daily data)
        annualized_vol = volatility * np.sqrt(252)

        return annualized_vol if annualized_vol > 0 else self.target_volatility

    def calculate_position_size(
        self,
        equity: float,
        price: float,
        data: Optional[pd.DataFrame] = None,
        volatility: Optional[float] = None,
        **kwargs
    ) -> float:
        """
        Calculate risk parity position size.

        Parameters
        ----------
        equity : float
            Current account equity
        price : float
            Current price
        data : pd.DataFrame, optional
            Price data for volatility calculation
        volatility : float, optional
            Pre-calculated volatility
        **kwargs
            Additional parameters

        Returns
        -------
        float
            Number of shares to trade
        """
        if equity <= 0 or price <= 0:
            return 0

        # Get volatility
        if volatility is None:
            if data is None or len(data) < 2:
                volatility = self.target_volatility
            else:
                volatility = self.calculate_volatility(data)

        if volatility <= 0:
            volatility = self.target_volatility

        # Scale position size inversely to volatility
        # position_pct = target_volatility / actual_volatility
        position_pct = self.target_volatility / volatility

        # Apply limits
        position_pct = min(position_pct, self.max_position_pct)
        position_pct = max(position_pct, 0.01)  # Minimum 1%

        position_value = equity * position_pct
        shares = int(position_value / price)

        return shares
