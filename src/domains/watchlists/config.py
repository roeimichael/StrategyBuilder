"""
Watchlists Domain Configuration

Contains all hard-coded values and settings for the watchlists domain.
"""

import os


class Config:
    """Configuration for watchlist operations."""

    # Database settings
    DB_NAME = "watchlists.db"
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data',
        DB_NAME
    )

    # Limits
    MAX_WATCHLISTS = 100  # Maximum number of watchlists per user
    MAX_WATCHLIST_NAME_LENGTH = 100
    MAX_WATCHLIST_DESCRIPTION_LENGTH = 500

    # Default values
    DEFAULT_CASH = 10000.0
    DEFAULT_INTERVAL = "1d"
    DEFAULT_ACTIVE = True

    # EOD (End of Day) update settings
    EOD_UPDATE_TIME = "16:00"  # 4:00 PM market close
    EOD_UPDATE_TIMEZONE = "America/New_York"
    EOD_UPDATE_ENABLED = True

    # Position tracking
    TRACK_OPEN_POSITIONS = True
    TRACK_CLOSED_POSITIONS = True
    MAX_POSITION_HISTORY_DAYS = 365  # Keep 1 year of history

    # Performance
    MAX_CONCURRENT_EOD_UPDATES = 10  # Process watchlists in parallel

    # Query limits
    DEFAULT_ACTIVE_ONLY = False
