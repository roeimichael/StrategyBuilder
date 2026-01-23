"""
Market Scans Domain Configuration

Contains all hard-coded values and settings for the market scans domain.
"""


class Config:
    """Configuration for market scan operations."""

    # Limits
    MAX_TICKERS_PER_SCAN = 500
    MIN_TICKERS_PER_SCAN = 1

    # Results
    TOP_PERFORMERS_COUNT = 20  # Number of top performers to return

    # Default values
    DEFAULT_CASH = 10000.0
    DEFAULT_INTERVAL = "1d"

    # Filtering
    DEFAULT_MIN_RETURN_PCT = None  # No filter by default
    DEFAULT_MIN_SHARPE_RATIO = None  # No filter by default

    # Performance
    SAVE_SCAN_RUNS = False  # Don't save individual scan runs to run history
    BATCH_SIZE = 50  # Process tickers in batches for memory efficiency

    # Timeouts
    MAX_SCAN_DURATION_MINUTES = 120  # 2 hours max for 500 tickers

    # Error handling
    CONTINUE_ON_TICKER_ERROR = True  # Continue scanning if one ticker fails
