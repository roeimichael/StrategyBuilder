"""
Model Wrapper Module

Provides unified interface for different ML models (RandomForest, XGBoost, etc.)
with training, prediction, and evaluation capabilities.
"""

from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import pickle
import json
from pathlib import Path


class ModelWrapper(ABC):
    """Base class for ML model wrappers."""

    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """Train the model."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate predictions."""
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Generate probability predictions."""
        pass

    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        pass

    @abstractmethod
    def save(self, filepath: str):
        """Save model to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str):
        """Load model from disk."""
        pass


class RandomForestWrapper(ModelWrapper):
    """Wrapper for RandomForest classifier."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 10,
        min_samples_split: int = 5,
        random_state: int = 42
    ):
        """
        Initialize RandomForest wrapper.

        Parameters
        ----------
        n_estimators : int
            Number of trees (default: 100)
        max_depth : int, optional
            Maximum tree depth (default: 10)
        min_samples_split : int
            Minimum samples required to split (default: 5)
        random_state : int
            Random seed (default: 42)
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.model = None
        self.feature_names = None

        # Try to import sklearn
        try:
            from sklearn.ensemble import RandomForestClassifier
            self.RandomForestClassifier = RandomForestClassifier
            self.sklearn_available = True
        except ImportError:
            self.sklearn_available = False
            self.RandomForestClassifier = None

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        sample_weight: Optional[np.ndarray] = None,
        **kwargs
    ):
        """
        Train RandomForest model.

        Parameters
        ----------
        X : pd.DataFrame
            Feature matrix
        y : pd.Series
            Target variable
        sample_weight : np.ndarray, optional
            Sample weights
        **kwargs
            Additional sklearn parameters
        """
        if not self.sklearn_available:
            raise ImportError("scikit-learn is required for RandomForest. "
                            "Install with: pip install scikit-learn")

        self.feature_names = list(X.columns)

        self.model = self.RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            random_state=self.random_state,
            **kwargs
        )

        self.model.fit(X, y, sample_weight=sample_weight)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate class predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Generate probability predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        return self.model.predict_proba(X)

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances))

    def save(self, filepath: str):
        """Save model to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train model first.")

        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names,
                'params': {
                    'n_estimators': self.n_estimators,
                    'max_depth': self.max_depth,
                    'min_samples_split': self.min_samples_split,
                    'random_state': self.random_state
                }
            }, f)

    def load(self, filepath: str):
        """Load model from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.feature_names = data['feature_names']

        if 'params' in data:
            params = data['params']
            self.n_estimators = params.get('n_estimators', self.n_estimators)
            self.max_depth = params.get('max_depth', self.max_depth)
            self.min_samples_split = params.get('min_samples_split', self.min_samples_split)
            self.random_state = params.get('random_state', self.random_state)


class XGBoostWrapper(ModelWrapper):
    """Wrapper for XGBoost classifier."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        """
        Initialize XGBoost wrapper.

        Parameters
        ----------
        n_estimators : int
            Number of boosting rounds (default: 100)
        max_depth : int
            Maximum tree depth (default: 6)
        learning_rate : float
            Learning rate (default: 0.1)
        random_state : int
            Random seed (default: 42)
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model = None
        self.feature_names = None

        # Try to import xgboost
        try:
            import xgboost as xgb
            self.xgb = xgb
            self.xgboost_available = True
        except ImportError:
            self.xgboost_available = False
            self.xgb = None

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        eval_set: Optional[Tuple] = None,
        **kwargs
    ):
        """
        Train XGBoost model.

        Parameters
        ----------
        X : pd.DataFrame
            Feature matrix
        y : pd.Series
            Target variable
        eval_set : tuple, optional
            Validation set (X_val, y_val)
        **kwargs
            Additional XGBoost parameters
        """
        if not self.xgboost_available:
            raise ImportError("xgboost is required. Install with: pip install xgboost")

        self.feature_names = list(X.columns)

        self.model = self.xgb.XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
            **kwargs
        )

        self.model.fit(X, y, eval_set=eval_set, verbose=False)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate class predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Generate probability predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        return self.model.predict_proba(X)

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances))

    def save(self, filepath: str):
        """Save model to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train model first.")

        self.model.save_model(filepath)

        # Save metadata
        metadata_path = Path(filepath).with_suffix('.json')
        metadata = {
            'feature_names': self.feature_names,
            'params': {
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'learning_rate': self.learning_rate,
                'random_state': self.random_state
            }
        }

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

    def load(self, filepath: str):
        """Load model from disk."""
        if not self.xgboost_available:
            raise ImportError("xgboost is required. Install with: pip install xgboost")

        self.model = self.xgb.XGBClassifier()
        self.model.load_model(filepath)

        # Load metadata
        metadata_path = Path(filepath).with_suffix('.json')
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            self.feature_names = metadata.get('feature_names', [])

            if 'params' in metadata:
                params = metadata['params']
                self.n_estimators = params.get('n_estimators', self.n_estimators)
                self.max_depth = params.get('max_depth', self.max_depth)
                self.learning_rate = params.get('learning_rate', self.learning_rate)
                self.random_state = params.get('random_state', self.random_state)


def create_model(
    model_type: str = 'random_forest',
    **kwargs
) -> ModelWrapper:
    """
    Factory function to create ML model wrapper.

    Parameters
    ----------
    model_type : str
        Type of model: 'random_forest' or 'xgboost'
    **kwargs
        Model-specific parameters

    Returns
    -------
    ModelWrapper
        Initialized model wrapper
    """
    if model_type.lower() == 'random_forest':
        return RandomForestWrapper(**kwargs)
    elif model_type.lower() == 'xgboost':
        return XGBoostWrapper(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}. "
                        f"Available: 'random_forest', 'xgboost'")
