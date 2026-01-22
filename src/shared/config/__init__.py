from .api_config import ApiConfig
from .backtest_config import BacktestConfig
from .constants import *

class Config(ApiConfig, BacktestConfig):
    pass

__all__ = ['Config', 'ApiConfig', 'BacktestConfig']
