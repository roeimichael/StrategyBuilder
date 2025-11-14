"""
Feature Engineering Module

Creates technical features from price data for machine learning models.
Includes indicators, patterns, and derived features.
"""

from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np


class FeatureEngineer:
    """
    Feature engineering for machine learning trading strategies.

    Creates technical indicators and derived features from OHLCV data.
    """

    def __init__(self, include_patterns: bool = True):
        """
        Initialize Feature Engineer.

        Parameters
        ----------
        include_patterns : bool
            Include pattern recognition features (default: True)
        """
        self.include_patterns = include_patterns
        self.feature_names = []

    def create_features(
        self,
        data: pd.DataFrame,
        target_forward_periods: int = 5,
        target_threshold: float = 0.02
    ) -> pd.DataFrame:
        """
        Create all features from price data.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV data with columns: Open, High, Low, Close, Volume
        target_forward_periods : int
            Number of periods to look ahead for target creation (default: 5)
        target_threshold : float
            Price change threshold for buy/sell signals (default: 0.02 = 2%)

        Returns
        -------
        pd.DataFrame
            Data with all features added
        """
        df = data.copy()

        # Price-based features
        df = self._add_price_features(df)

        # Moving averages
        df = self._add_moving_averages(df)

        # Momentum indicators
        df = self._add_momentum_indicators(df)

        # Volatility indicators
        df = self._add_volatility_indicators(df)

        # Volume indicators
        df = self._add_volume_indicators(df)

        # Trend indicators
        df = self._add_trend_indicators(df)

        # Pattern features
        if self.include_patterns:
            df = self._add_pattern_features(df)

        # Create target variable
        df = self._create_target(df, target_forward_periods, target_threshold)

        # Store feature names
        self.feature_names = [col for col in df.columns if col not in
                             ['Open', 'High', 'Low', 'Close', 'Volume', 'target', 'target_binary']]

        return df

    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic price-derived features."""
        # Returns
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))

        # Price position
        df['close_to_high_ratio'] = df['Close'] / df['High']
        df['close_to_low_ratio'] = df['Close'] / df['Low']

        # Candle body and wick
        df['body'] = df['Close'] - df['Open']
        df['body_pct'] = df['body'] / df['Open']
        df['upper_wick'] = df['High'] - df[['Close', 'Open']].max(axis=1)
        df['lower_wick'] = df[['Close', 'Open']].min(axis=1) - df['Low']

        # Range
        df['high_low_range'] = df['High'] - df['Low']
        df['high_low_pct'] = df['high_low_range'] / df['Low']

        return df

    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving average features."""
        periods = [5, 10, 20, 50, 200]

        for period in periods:
            # Simple Moving Average
            df[f'sma_{period}'] = df['Close'].rolling(window=period).mean()

            # Exponential Moving Average
            df[f'ema_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

            # Distance from MA
            df[f'close_sma_{period}_ratio'] = df['Close'] / df[f'sma_{period}']
            df[f'close_ema_{period}_ratio'] = df['Close'] / df[f'ema_{period}']

        # MA crossovers
        df['sma_5_20_cross'] = (df['sma_5'] > df['sma_20']).astype(int)
        df['sma_20_50_cross'] = (df['sma_20'] > df['sma_50']).astype(int)
        df['ema_5_20_cross'] = (df['ema_5'] > df['ema_20']).astype(int)

        return df

    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum indicators."""
        # RSI (Relative Strength Index)
        df = self._calculate_rsi(df, period=14)
        df = self._calculate_rsi(df, period=7)

        # MACD
        df = self._calculate_macd(df)

        # Rate of Change
        for period in [5, 10, 20]:
            df[f'roc_{period}'] = ((df['Close'] - df['Close'].shift(period)) /
                                   df['Close'].shift(period)) * 100

        # Stochastic Oscillator
        df = self._calculate_stochastic(df)

        return df

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI."""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        df[f'rsi_{period}'] = 100 - (100 / (1 + rs))

        return df

    def _calculate_macd(
        self,
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """Calculate MACD."""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()

        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        return df

    def _calculate_stochastic(
        self,
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> pd.DataFrame:
        """Calculate Stochastic Oscillator."""
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()

        df['stoch_k'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()

        return df

    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility indicators."""
        # Bollinger Bands
        df = self._calculate_bollinger_bands(df)

        # ATR (Average True Range)
        df = self._calculate_atr(df)

        # Historical Volatility
        for period in [10, 20, 30]:
            df[f'volatility_{period}'] = df['returns'].rolling(window=period).std()

        return df

    def _calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        df['bb_middle'] = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()

        df['bb_upper'] = df['bb_middle'] + (std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (std * std_dev)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / df['bb_width']

        return df

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range."""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df[f'atr_{period}'] = true_range.rolling(window=period).mean()

        return df

    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume indicators."""
        # Volume moving averages
        df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_20']

        # On-Balance Volume (OBV)
        df['obv'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

        # Volume Price Trend
        df['vpt'] = (df['Volume'] * ((df['Close'] - df['Close'].shift(1)) /
                                     df['Close'].shift(1))).fillna(0).cumsum()

        return df

    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend indicators."""
        # ADX (Average Directional Index)
        df = self._calculate_adx(df)

        # Trend strength
        for period in [10, 20, 50]:
            df[f'trend_{period}'] = (df['Close'] > df['Close'].shift(period)).astype(int)

        return df

    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate ADX."""
        high_diff = df['High'].diff()
        low_diff = -df['Low'].diff()

        pos_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        neg_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        # Calculate ATR for this
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        atr = true_range.rolling(window=period).mean()

        pos_di = 100 * (pos_dm.rolling(window=period).mean() / atr)
        neg_di = 100 * (neg_dm.rolling(window=period).mean() / atr)

        dx = 100 * np.abs(pos_di - neg_di) / (pos_di + neg_di)
        df['adx'] = dx.rolling(window=period).mean()

        return df

    def _add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add candlestick pattern features."""
        # Doji
        df['is_doji'] = (np.abs(df['body']) < df['high_low_range'] * 0.1).astype(int)

        # Hammer/Hanging Man
        body_size = np.abs(df['body'])
        df['is_hammer'] = ((df['lower_wick'] > body_size * 2) &
                           (df['upper_wick'] < body_size * 0.3)).astype(int)

        # Engulfing patterns
        df['is_bullish_engulfing'] = ((df['body'] > 0) &
                                       (df['body'].shift(1) < 0) &
                                       (df['body'] > np.abs(df['body'].shift(1)))).astype(int)

        df['is_bearish_engulfing'] = ((df['body'] < 0) &
                                       (df['body'].shift(1) > 0) &
                                       (np.abs(df['body']) > df['body'].shift(1))).astype(int)

        return df

    def _create_target(
        self,
        df: pd.DataFrame,
        forward_periods: int,
        threshold: float
    ) -> pd.DataFrame:
        """
        Create target variable for ML training.

        Parameters
        ----------
        df : pd.DataFrame
            Data with features
        forward_periods : int
            Number of periods to look ahead
        threshold : float
            Price change threshold for signals

        Returns
        -------
        pd.DataFrame
            Data with target variables
        """
        # Future return
        df['future_return'] = df['Close'].shift(-forward_periods) / df['Close'] - 1

        # Classification target (Buy=1, Hold=0, Sell=-1)
        df['target'] = 0  # Hold
        df.loc[df['future_return'] > threshold, 'target'] = 1  # Buy
        df.loc[df['future_return'] < -threshold, 'target'] = -1  # Sell

        # Binary classification (Buy=1, Not Buy=0)
        df['target_binary'] = (df['target'] == 1).astype(int)

        return df

    def get_feature_importance_names(self) -> List[str]:
        """Get list of feature names for model training."""
        return self.feature_names.copy()

    def prepare_ml_data(
        self,
        df: pd.DataFrame,
        target_col: str = 'target',
        dropna: bool = True
    ) -> tuple:
        """
        Prepare data for ML training.

        Parameters
        ----------
        df : pd.DataFrame
            Data with features and target
        target_col : str
            Name of target column (default: 'target')
        dropna : bool
            Drop rows with NaN values (default: True)

        Returns
        -------
        tuple
            (X, y) where X is features DataFrame and y is target Series
        """
        if dropna:
            df = df.dropna()

        # Get feature columns
        feature_cols = [col for col in self.feature_names if col in df.columns]

        X = df[feature_cols]
        y = df[target_col]

        return X, y
