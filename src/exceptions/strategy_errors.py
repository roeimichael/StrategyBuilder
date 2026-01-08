from .base import StrategyBuilderError

class StrategyNotFoundError(StrategyBuilderError):
    pass

class StrategyLoadError(StrategyBuilderError):
    pass

class InvalidStrategyError(StrategyBuilderError):
    pass
