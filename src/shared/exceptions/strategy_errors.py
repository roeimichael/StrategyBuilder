from .base import StrategyBuilderError


class StrategyNotFoundError(StrategyBuilderError):
    """Raised when a strategy cannot be found"""
    pass


class StrategyLoadError(StrategyBuilderError):
    """Raised when a strategy cannot be loaded"""
    pass


class InvalidStrategyError(StrategyBuilderError):
    """Raised when a strategy is invalid"""
    pass
