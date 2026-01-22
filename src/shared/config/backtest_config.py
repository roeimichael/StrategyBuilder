from typing import Dict, Any


class BacktestConfig:
    DEFAULT_CASH = 10000.0
    DEFAULT_COMMISSION = 0.001
    DEFAULT_POSITION_SIZE_PCT = 95.0
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
            'cash': BacktestConfig.DEFAULT_CASH,
            'commission': BacktestConfig.DEFAULT_COMMISSION,
            'position_size_pct': BacktestConfig.DEFAULT_POSITION_SIZE_PCT,
            'macd1': BacktestConfig.DEFAULT_MACD_FAST,
            'macd2': BacktestConfig.DEFAULT_MACD_SLOW,
            'macdsig': BacktestConfig.DEFAULT_MACD_SIGNAL,
            'atrperiod': BacktestConfig.DEFAULT_ATR_PERIOD,
            'atrdist': BacktestConfig.DEFAULT_ATR_DISTANCE,
            'order_pct': BacktestConfig.DEFAULT_ORDER_PCT,
        }
