"""
Portfolios Domain Configuration

Contains all hard-coded values and settings for the portfolios domain.
"""

import os


class Config:
    """Configuration for portfolio operations."""

    # Database settings
    DB_NAME = "portfolios.db"
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data',
        DB_NAME
    )

    # Limits
    MAX_PORTFOLIOS = 50  # Maximum number of portfolios per user
    MAX_HOLDINGS_PER_PORTFOLIO = 100  # Maximum stocks per portfolio
    MIN_HOLDINGS_PER_PORTFOLIO = 1
    MAX_PORTFOLIO_NAME_LENGTH = 100
    MAX_PORTFOLIO_DESCRIPTION_LENGTH = 500

    # Validation
    REQUIRE_UNIQUE_NAMES = True
    VALIDATE_WEIGHTS_SUM_TO_ONE = False  # Weights don't have to sum to 1.0

    # Backtest settings
    DEFAULT_USE_WEIGHTS = False  # Don't use weights for aggregation by default
    SAVE_PORTFOLIO_BACKTEST_RUNS = False  # Don't save individual ticker runs

    # Performance
    PARALLEL_PORTFOLIO_BACKTEST = False  # Process tickers sequentially by default
    MAX_WORKERS = 5  # Number of parallel workers if enabled
