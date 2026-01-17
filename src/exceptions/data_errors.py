from .base import StrategyBuilderError


class DataFetchError(StrategyBuilderError):
    pass


class InvalidDataError(StrategyBuilderError):
    pass


class DataNotFoundError(StrategyBuilderError):
    pass
