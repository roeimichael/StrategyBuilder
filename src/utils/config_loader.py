"""Configuration loader for StrategyBuilder"""

import os
import yaml
from typing import Dict, Any


class ConfigLoader:
    """Load and manage YAML configuration"""

    def __init__(self, config_path: str = None):
        """Initialize configuration loader"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data_config.yaml'
            )

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            return self._get_default_config()

        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'data_manager': {
                'cache_path': './data/market_data.db',
                'update_schedule': 'daily',
                'default_interval': '1d',
                'lookback_years': 5
            },
            'backtesting': {
                'cash': 100000,
                'commission': 0.001
            },
            'walk_forward': {
                'train_period_months': 12,
                'test_period_months': 3,
                'step_months': 3,
                'min_trades': 5
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_data_manager_config(self) -> Dict[str, Any]:
        """Get data manager configuration"""
        return self.config.get('data_manager', {})

    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """Get strategy-specific configuration"""
        strategies = self.config.get('strategies', {})
        return strategies.get(strategy_name, {})

    def get_walk_forward_config(self) -> Dict[str, Any]:
        """Get walk-forward optimization configuration"""
        return self.config.get('walk_forward', {})

    def get_strategy_defaults(self, strategy_name: str) -> Dict[str, Any]:
        """Get default parameters for a strategy"""
        strategy_config = self.get_strategy_config(strategy_name)
        return strategy_config.get('defaults', {})

    def get_strategy_optimization_ranges(self, strategy_name: str) -> Dict[str, list]:
        """Get parameter ranges for optimization"""
        strategy_config = self.get_strategy_config(strategy_name)
        return strategy_config.get('optimization', {})

    def get_strategy_constraints(self, strategy_name: str) -> Dict[str, Dict[str, float]]:
        """Get parameter constraints for a strategy"""
        strategy_config = self.get_strategy_config(strategy_name)
        return strategy_config.get('constraints', {})

    def validate_parameters(self, strategy_name: str, params: Dict[str, Any]) -> bool:
        """
        Validate parameters against constraints

        Args:
            strategy_name: Name of the strategy
            params: Parameters to validate

        Returns:
            True if valid, False otherwise
        """
        constraints = self.get_strategy_constraints(strategy_name)

        for param_name, param_value in params.items():
            if param_name in constraints:
                constraint = constraints[param_name]
                min_val = constraint.get('min')
                max_val = constraint.get('max')

                if min_val is not None and param_value < min_val:
                    return False
                if max_val is not None and param_value > max_val:
                    return False

        return True

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance optimization configuration"""
        return self.config.get('performance', {})

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.config.get('api', {})

    def use_vectorized_backtesting(self) -> bool:
        """Check if vectorized backtesting is enabled"""
        return self.get('performance.use_vectorized', False)

    def get_parallel_workers(self) -> int:
        """Get number of parallel workers for grid search"""
        return self.get('performance.parallel_workers', -1)
