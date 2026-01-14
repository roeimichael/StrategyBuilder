from .base import StrategyBuilderError


class DataFetchError(StrategyBuilderError):
    """Raised when data cannot be fetched"""
    pass


class InvalidDataError(StrategyBuilderError):
    """Raised when data is invalid"""
    pass


class DataNotFoundError(StrategyBuilderError):
    """Raised when data cannot be found"""
    pass
