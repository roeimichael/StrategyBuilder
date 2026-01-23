"""
Backtests Domain Configuration

Contains all hard-coded values and settings for the backtests domain.
"""


class Config:
    """Configuration for backtest operations."""

    # Default values
    DEFAULT_CASH = 10000.0
    DEFAULT_INTERVAL = "1d"
    DEFAULT_BACKTEST_PERIOD_YEARS = 1

    # Chart data settings
    DEFAULT_INCLUDE_CHART_DATA = False
    DEFAULT_COLUMNAR_FORMAT = True

    # Position sizing
    DEFAULT_POSITION_SIZE_PCT = 95  # Percentage of cash to use per position

    # Limits
    MAX_BACKTEST_DURATION_DAYS = 3650  # 10 years max
    MIN_BACKTEST_DURATION_DAYS = 1

    # Performance settings
    MAX_CONCURRENT_BACKTESTS = 10  # For parallel processing if needed

    # Database settings
    SAVE_RUNS_BY_DEFAULT = True
