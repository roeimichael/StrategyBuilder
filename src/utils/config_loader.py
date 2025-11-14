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
