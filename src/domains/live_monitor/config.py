"""
Live Monitor Domain Configuration

Contains all hard-coded values and settings for the live monitor domain.
"""


class Config:
    """Configuration for live price monitoring."""

    # Limits
    MAX_TICKERS_PER_REQUEST = 50
    MIN_TICKERS_PER_REQUEST = 1

    # Timeouts
    TICKER_FETCH_TIMEOUT_SECONDS = 5  # Timeout per ticker
    MAX_REQUEST_DURATION_SECONDS = 30  # Total request timeout

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    CACHE_DURATION_SECONDS = 5  # Cache prices for 5 seconds

    # Error handling
    CONTINUE_ON_TICKER_ERROR = True  # Return partial results if some fail
    INCLUDE_ERROR_DETAILS = True  # Include error messages in response

    # Data provider settings
    USE_FAST_INFO = True  # Use yfinance fast_info for better performance
    FALLBACK_TO_INFO = True  # Fallback to regular info if fast_info fails
