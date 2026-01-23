"""
Strategies Domain Configuration

Contains all hard-coded values and settings for the strategies domain.
"""

import os


class Config:
    """Configuration for strategy operations."""

    # Directories
    STRATEGIES_DIR = os.path.join(os.path.dirname(__file__), 'implementations')

    # Default parameters
    DEFAULT_PARAMETERS = {
        'cash': 10000.0,
        'macd1': 12,
        'macd2': 26,
        'macdsig': 9,
        'atrperiod': 14,
        'atrdist': 2.0,
        'order_pct': 1.0,
    }

    # Validation
    VALIDATE_STRATEGY_EXISTS = True
    LOAD_PARAMETERS_FROM_CLASS = True
    LOAD_OPTIMIZABLE_PARAMS = True

    # Caching
    CACHE_STRATEGY_LIST = True
    CACHE_STRATEGY_INFO = True

    # Limits
    MAX_STRATEGIES = 100  # Maximum number of strategies to discover
