"""
Config Reader Utility

A centralized utility for loading domain-specific configuration files.
Each domain can have its own config file and use this utility to load it.
"""

import os
import importlib
from typing import Any, Type, TypeVar

T = TypeVar('T')


class ConfigReader:
    """
    Centralized configuration reader for domain-specific configs.

    Usage:
        from src.shared.utils.config_reader import ConfigReader
        config = ConfigReader.load_domain_config('backtests')

        # Access config values
        max_tickers = config.MAX_TICKERS_PER_SCAN
    """

    _cache = {}

    @classmethod
    def load_domain_config(cls, domain_name: str) -> Any:
        """
        Load configuration for a specific domain.

        Args:
            domain_name: Name of the domain (e.g., 'backtests', 'optimizations')

        Returns:
            Config class instance for the domain

        Example:
            config = ConfigReader.load_domain_config('backtests')
            print(config.DEFAULT_CASH)
        """
        # Check cache first
        if domain_name in cls._cache:
            return cls._cache[domain_name]

        try:
            # Import the config module for the domain
            module_path = f'src.domains.{domain_name}.config'
            config_module = importlib.import_module(module_path)

            # Get the Config class from the module
            if hasattr(config_module, 'Config'):
                config_class = getattr(config_module, 'Config')
                config_instance = config_class()

                # Cache it
                cls._cache[domain_name] = config_instance
                return config_instance
            else:
                raise AttributeError(f"Config class not found in {module_path}")

        except ImportError as e:
            raise ImportError(f"Could not load config for domain '{domain_name}': {str(e)}")

    @classmethod
    def get(cls, domain_name: str, key: str, default: Any = None) -> Any:
        """
        Get a specific config value from a domain.

        Args:
            domain_name: Name of the domain
            key: Config key to retrieve
            default: Default value if key not found

        Returns:
            Config value or default

        Example:
            max_cash = ConfigReader.get('backtests', 'MAX_CASH', 1000000)
        """
        config = cls.load_domain_config(domain_name)
        return getattr(config, key, default)

    @classmethod
    def clear_cache(cls):
        """Clear the config cache. Useful for testing."""
        cls._cache.clear()
