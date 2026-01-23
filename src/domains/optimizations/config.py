"""
Optimizations Domain Configuration

Contains all hard-coded values and settings for the optimizations domain.
"""


class Config:
    """Configuration for optimization operations."""

    # Default values
    DEFAULT_CASH = 10000.0
    DEFAULT_INTERVAL = "1d"

    # Limits
    MAX_PARAMETER_COMBINATIONS = 1000  # Maximum combinations to test
    MIN_PARAMETER_COMBINATIONS = 1

    # Results
    TOP_RESULTS_COUNT = 20  # Number of top results to return

    # Timeouts
    MAX_OPTIMIZATION_DURATION_MINUTES = 60

    # Performance
    PARALLEL_OPTIMIZATION = False  # Enable parallel processing
    MAX_WORKERS = 4  # Number of parallel workers if enabled
