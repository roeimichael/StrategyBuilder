"""
System Domain Configuration

Contains all hard-coded values and settings for the system domain.
"""


class Config:
    """Configuration for system-level operations."""

    # API Information
    API_TITLE = "StrategyBuilder API"
    API_VERSION = "2.0.0"
    API_DESCRIPTION = "Algorithmic Trading Backtesting Platform"

    # Health check
    HEALTH_CHECK_ENABLED = True
    INCLUDE_TIMESTAMP = True

    # Default parameters endpoint
    PROVIDE_DEFAULT_PARAMETERS = True
