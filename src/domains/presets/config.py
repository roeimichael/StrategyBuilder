"""
Presets Domain Configuration

Contains all hard-coded values and settings for the presets domain.
"""

import os


class Config:
    """Configuration for preset operations."""

    # Database settings
    DB_NAME = "presets.db"
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        DB_NAME
    )

    # Limits
    MAX_PRESETS = 1000  # Maximum number of presets per user
    MAX_PRESET_NAME_LENGTH = 100
    MAX_PRESET_DESCRIPTION_LENGTH = 500

    # Query limits
    DEFAULT_LIST_LIMIT = 100
    MAX_LIST_LIMIT = 500
    DEFAULT_LIST_OFFSET = 0

    # Default values
    DEFAULT_CASH = 10000.0
    DEFAULT_INTERVAL = "1d"

    # Validation
    REQUIRE_UNIQUE_NAMES = True
