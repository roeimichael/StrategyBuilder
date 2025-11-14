"""
Machine Learning Strategy Module

Integrates ML models with backtesting framework for trading signal generation.
Provides end-to-end pipeline from feature engineering to prediction.
"""

from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import backtrader as bt

from .feature_engineering import FeatureEngineer
from .model_wrapper import ModelWrapper, create_model


class MLStrategy(bt.Strategy):
    """
    Machine Learning-based trading strategy.

    Uses trained ML model to generate buy/sell/hold signals based on
    technical features extracted from price data.
    """

    params = (
        ('model_type', 'random_forest'),
        ('model_path', None),
        ('min_probability', 0.60),
        ('target_forward_periods', 5),
        ('target_threshold', 0.02),
        ('retrain_interval', None),
        ('position_size_pct', 0.95),
    )

    def __init__(self):
        """Initialize ML strategy."""
        self.feature_engineer = FeatureEngineer()
        self.model = None
        self.feature_names = []
        self.order = None
        self.predictions = []
        self.trade_count = 0

        # Load model if path provided
        if self.params.model_path is not None:
            self.load_model(self.params.model_path)

    def next(self):
        """Execute on each bar."""
        # Skip if model not loaded
        if self.model is None:
            return

        # Check if we have an order pending
        if self.order:
            return

        # Get current data
        try:
            features = self._extract_features()
            if features is None:
                return

            # Get prediction
            prediction, probability = self._get_prediction(features)

            # Store prediction for analysis
            self.predictions.append({
                'datetime': self.data.datetime.datetime(0),
                'prediction': prediction,
                'probability': probability,
                'close': self.data.close[0]
            })

            # Generate signals based on prediction and probability
            if not self.position:
                # Not in market - look for buy signal
                if prediction == 1 and probability >= self.params.min_probability:
                    size = self._calculate_position_size()
                    self.order = self.buy(size=size)
                    self.trade_count += 1

            else:
                # In market - look for sell signal
                if prediction == -1 or prediction == 0:
                    self.order = self.sell(size=self.position.size)

        except Exception as e:
            # Silently handle errors to avoid stopping backtest
            pass

    def notify_order(self, order):
        """Notification of order status."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                pass
            elif order.issell():
                pass

        self.order = None

    def _extract_features(self) -> Optional[pd.DataFrame]:
        """
        Extract features from current data window.

        Returns
        -------
        pd.DataFrame or None
            Feature row for prediction, or None if insufficient data
        """
        # Need sufficient data for feature calculation
        min_bars = 200

        if len(self.data) < min_bars:
            return None

        # Convert backtrader data to DataFrame
        df = self._backtrader_to_dataframe(lookback=min_bars)

        if df is None or len(df) < min_bars:
            return None

        # Create features
        df_features = self.feature_engineer.create_features(
            df,
            target_forward_periods=self.params.target_forward_periods,
            target_threshold=self.params.target_threshold
        )

        # Get latest row (current bar)
        latest = df_features.iloc[[-1]]

        # Select only feature columns
        feature_cols = [col for col in self.feature_engineer.feature_names
                       if col in latest.columns]

        if len(feature_cols) == 0:
            return None

        features = latest[feature_cols]

        # Check for NaN values
        if features.isnull().any().any():
            return None

        return features

    def _backtrader_to_dataframe(self, lookback: int = 200) -> Optional[pd.DataFrame]:
        """
        Convert backtrader data to pandas DataFrame.

        Parameters
        ----------
        lookback : int
            Number of bars to include

        Returns
        -------
        pd.DataFrame or None
            OHLCV DataFrame
        """
        try:
            data_len = len(self.data)
            start_idx = max(0, data_len - lookback)

            dates = []
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []

            for i in range(-lookback + 1, 1):
                if abs(i) <= data_len:
                    dates.append(self.data.datetime.datetime(i))
                    opens.append(self.data.open[i])
                    highs.append(self.data.high[i])
                    lows.append(self.data.low[i])
                    closes.append(self.data.close[i])
                    volumes.append(self.data.volume[i])

            df = pd.DataFrame({
                'Open': opens,
                'High': highs,
                'Low': lows,
                'Close': closes,
                'Volume': volumes
            }, index=dates)

            return df

        except Exception as e:
            return None

    def _get_prediction(self, features: pd.DataFrame) -> Tuple[int, float]:
        """
        Get prediction from model.

        Parameters
        ----------
        features : pd.DataFrame
            Feature row

        Returns
        -------
        tuple
            (prediction, probability) where prediction is -1/0/1 and probability is float
        """
        try:
            # Get prediction
            pred = self.model.predict(features)[0]

            # Get probability
            proba = self.model.predict_proba(features)[0]

            # Get probability of predicted class
            if pred == 1:
                probability = proba[1] if len(proba) > 1 else proba[0]
            elif pred == -1:
                probability = proba[0] if len(proba) > 1 else 1 - proba[0]
            else:
                probability = 0.5

            return int(pred), float(probability)

        except Exception as e:
            return 0, 0.5

    def _calculate_position_size(self) -> int:
        """Calculate position size."""
        cash = self.broker.getcash()
        price = self.data.close[0]

        if price <= 0:
            return 0

        # Use percentage of cash
        position_value = cash * self.params.position_size_pct
        size = int(position_value / price)

        return size

    def load_model(self, filepath: str):
        """
        Load trained model from disk.

        Parameters
        ----------
        filepath : str
            Path to model file
        """
        self.model = create_model(self.params.model_type)
        self.model.load(filepath)

    def get_predictions_history(self) -> pd.DataFrame:
        """
        Get history of predictions made during backtest.

        Returns
        -------
        pd.DataFrame
            DataFrame with prediction history
        """
        if not self.predictions:
            return pd.DataFrame()

        return pd.DataFrame(self.predictions)


class MLTrainer:
    """
    Trainer for ML trading models.

    Handles data preparation, model training, and evaluation.
    """

    def __init__(
        self,
        model_type: str = 'random_forest',
        model_params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize ML trainer.

        Parameters
        ----------
        model_type : str
            Type of model to train
        model_params : dict, optional
            Model hyperparameters
        """
        self.model_type = model_type
        self.model_params = model_params or {}
        self.feature_engineer = FeatureEngineer()
        self.model = None

    def prepare_data(
        self,
        data: pd.DataFrame,
        target_forward_periods: int = 5,
        target_threshold: float = 0.02,
        test_size: float = 0.2
    ) -> Tuple:
        """
        Prepare data for training.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV data
        target_forward_periods : int
            Forward periods for target
        target_threshold : float
            Threshold for buy/sell signals
        test_size : float
            Fraction of data for testing

        Returns
        -------
        tuple
            (X_train, X_test, y_train, y_test)
        """
        # Create features
        df_features = self.feature_engineer.create_features(
            data,
            target_forward_periods=target_forward_periods,
            target_threshold=target_threshold
        )

        # Prepare ML data
        X, y = self.feature_engineer.prepare_ml_data(df_features, target_col='target')

        # Split into train/test
        split_idx = int(len(X) * (1 - test_size))

        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]

        return X_train, X_test, y_train, y_test

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        **kwargs
    ):
        """
        Train model.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training features
        y_train : pd.Series
            Training target
        **kwargs
            Additional training parameters
        """
        self.model = create_model(self.model_type, **self.model_params)
        self.model.train(X_train, y_train, **kwargs)

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict[str, float]:
        """
        Evaluate model performance.

        Parameters
        ----------
        X_test : pd.DataFrame
            Test features
        y_test : pd.Series
            Test target

        Returns
        -------
        dict
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        predictions = self.model.predict(X_test)

        # Calculate metrics
        accuracy = np.mean(predictions == y_test)

        # Per-class metrics
        buy_accuracy = np.mean(predictions[y_test == 1] == 1) if np.sum(y_test == 1) > 0 else 0
        sell_accuracy = np.mean(predictions[y_test == -1] == -1) if np.sum(y_test == -1) > 0 else 0
        hold_accuracy = np.mean(predictions[y_test == 0] == 0) if np.sum(y_test == 0) > 0 else 0

        return {
            'accuracy': accuracy,
            'buy_accuracy': buy_accuracy,
            'sell_accuracy': sell_accuracy,
            'hold_accuracy': hold_accuracy,
            'n_test_samples': len(y_test),
            'n_buy_signals': np.sum(predictions == 1),
            'n_sell_signals': np.sum(predictions == -1),
            'n_hold_signals': np.sum(predictions == 0)
        }

    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance.

        Parameters
        ----------
        top_n : int
            Number of top features to return

        Returns
        -------
        pd.DataFrame
            Feature importance DataFrame
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        importance_dict = self.model.get_feature_importance()

        df = pd.DataFrame({
            'feature': list(importance_dict.keys()),
            'importance': list(importance_dict.values())
        })

        df = df.sort_values('importance', ascending=False).head(top_n)

        return df

    def save_model(self, filepath: str):
        """Save trained model."""
        if self.model is None:
            raise ValueError("No model to save. Train model first.")

        self.model.save(filepath)

    def load_model(self, filepath: str):
        """Load trained model."""
        self.model = create_model(self.model_type, **self.model_params)
        self.model.load(filepath)
