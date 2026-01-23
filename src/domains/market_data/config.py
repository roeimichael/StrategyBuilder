"""
Market Data Domain Configuration

Contains all hard-coded values and settings for the market data domain.
"""

import os


class Config:
    """Configuration for market data operations."""

    # Database settings
    DB_NAME = "market_data.db"
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data',
        DB_NAME
    )

    # Default values
    DEFAULT_PERIOD = "1mo"
    DEFAULT_INTERVAL = "1d"

    # Period mappings (days)
    PERIOD_MAP = {
        '1mo': 30,
        '3mo': 90,
        '6mo': 180,
        '1y': 365,
        '2y': 730,
        '5y': 1825,
        'ytd': None,  # Calculated dynamically
        'max': 3650
    }

    # Limits
    MAX_DATA_POINTS = 10000  # Maximum data points to return
    MAX_FETCH_DURATION_DAYS = 3650  # 10 years max

    # Caching
    ENABLE_CACHE = True
    CACHE_UPDATE_SCHEDULE = "daily"  # daily, hourly, or realtime

    # Statistics
    CALCULATE_STATISTICS = True
    STATISTICS_FIELDS = ['mean', 'std', 'min', 'max', 'volume_avg']

    # Error handling
    RETRY_ON_FETCH_FAILURE = True
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 2
