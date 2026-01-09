from typing import Dict, Any


class Config:
    API_TITLE = "StrategyBuilder API"
    API_VERSION = "2.0.0"
    API_HOST = "localhost"
    API_PORT = 8086

    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]

    DEFAULT_CASH = 10000.0
    DEFAULT_MACD_FAST = 12
    DEFAULT_MACD_SLOW = 26
    DEFAULT_MACD_SIGNAL = 9
    DEFAULT_ATR_PERIOD = 14
    DEFAULT_ATR_DISTANCE = 2.0
    DEFAULT_ORDER_PCT = 1.0

    DEFAULT_BACKTEST_PERIOD_YEARS = 1
    DEFAULT_INTERVAL = "1d"

    @staticmethod
    def get_default_parameters() -> Dict[str, Any]:
        return {
            'cash': Config.DEFAULT_CASH,
            'macd1': Config.DEFAULT_MACD_FAST,
            'macd2': Config.DEFAULT_MACD_SLOW,
            'macdsig': Config.DEFAULT_MACD_SIGNAL,
            'atrperiod': Config.DEFAULT_ATR_PERIOD,
            'atrdist': Config.DEFAULT_ATR_DISTANCE,
            'order_pct': Config.DEFAULT_ORDER_PCT,
        }
