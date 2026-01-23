# Lazy imports to avoid requiring all dependencies upfront
__all__ = ['PerformanceAnalyzer', 'log_errors', 'logger', 'ConfigReader']


def __getattr__(name):
    """Lazy import modules on demand."""
    if name == 'PerformanceAnalyzer':
        from .performance_analyzer import PerformanceAnalyzer
        return PerformanceAnalyzer
    elif name == 'log_errors':
        from .api_logger import log_errors
        return log_errors
    elif name == 'logger':
        from .api_logger import logger
        return logger
    elif name == 'ConfigReader':
        from .config_reader import ConfigReader
        return ConfigReader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
