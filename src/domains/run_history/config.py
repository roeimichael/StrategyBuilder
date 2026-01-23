"""
Run History Domain Configuration

Contains all hard-coded values and settings for the run history domain.
"""

import os


class Config:
    """Configuration for run history operations."""

    # Database settings
    DB_NAME = "strategy_runs.db"
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data',
        DB_NAME
    )

    # Query limits
    DEFAULT_LIST_LIMIT = 100
    MAX_LIST_LIMIT = 1000
    DEFAULT_LIST_OFFSET = 0

    # Filters
    ALLOW_TICKER_FILTER = True
    ALLOW_STRATEGY_FILTER = True
    ALLOW_DATE_RANGE_FILTER = True

    # Retention
    MAX_RUN_HISTORY_DAYS = 365  # Keep 1 year of history
    AUTO_CLEANUP_ENABLED = False  # Automatically delete old runs

    # Replay settings
    ALLOW_PARAMETER_OVERRIDE = True
    ALLOW_DATE_OVERRIDE = True
    ALLOW_CASH_OVERRIDE = True
    SAVE_REPLAYED_RUNS = True  # Save replayed runs as new entries
