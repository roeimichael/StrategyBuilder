from typing import Dict, List, Any, Union

class ParameterConfig:
    def __init__(self, name: str, param_type: str, default: Union[int, float],
                 min_value: Union[int, float], max_value: Union[int, float],
                 step: Union[int, float], description: str):
        self.name = name
        self.param_type = param_type
        self.default = default
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.param_type,
            'default': self.default,
            'min': self.min_value,
            'max': self.max_value,
            'step': self.step,
            'description': self.description
        }

STRATEGY_OPTIMIZATION_CONFIGS: Dict[str, List[ParameterConfig]] = {
    'bollinger_bands_strategy': [
        ParameterConfig('period', 'int', 20, 10, 50, 5, 'Moving average period for Bollinger Bands'),
        ParameterConfig('devfactor', 'float', 2.0, 1.0, 3.0, 0.5, 'Standard deviation multiplier')
    ],
    'williams_r_strategy': [
        ParameterConfig('period', 'int', 14, 5, 30, 2, 'Lookback period for Williams %R'),
        ParameterConfig('oversold', 'int', -80, -95, -70, 5, 'Oversold threshold (negative value)'),
        ParameterConfig('overbought', 'int', -20, -35, -10, 5, 'Overbought threshold (negative value)')
    ],
    'rsi_stochastic_strategy': [
        ParameterConfig('rsi_period', 'int', 14, 7, 28, 7, 'RSI calculation period'),
        ParameterConfig('rsi_oversold', 'int', 30, 20, 40, 5, 'RSI oversold level'),
        ParameterConfig('rsi_overbought', 'int', 70, 60, 80, 5, 'RSI overbought level'),
        ParameterConfig('stoch_period', 'int', 14, 7, 21, 7, 'Stochastic oscillator period'),
        ParameterConfig('stoch_oversold', 'int', 20, 10, 30, 5, 'Stochastic oversold level'),
        ParameterConfig('stoch_overbought', 'int', 80, 70, 90, 5, 'Stochastic overbought level')
    ],
    'mfi_strategy': [
        ParameterConfig('period', 'int', 14, 7, 28, 7, 'Money Flow Index period'),
        ParameterConfig('oversold', 'int', 20, 10, 30, 5, 'MFI oversold level'),
        ParameterConfig('overbought', 'int', 80, 70, 90, 5, 'MFI overbought level')
    ],
    'keltner_channel_strategy': [
        ParameterConfig('ema_period', 'int', 20, 10, 40, 5, 'EMA period for centerline'),
        ParameterConfig('atr_period', 'int', 10, 5, 20, 5, 'ATR period for channel width'),
        ParameterConfig('atr_multiplier', 'float', 2.0, 1.0, 3.0, 0.5, 'ATR multiplier for band distance')
    ],
    'cci_atr_strategy': [
        ParameterConfig('cci_period', 'int', 20, 10, 30, 5, 'CCI calculation period'),
        ParameterConfig('cci_entry', 'int', -100, -150, -50, 25, 'CCI entry threshold'),
        ParameterConfig('cci_exit', 'int', 100, 50, 150, 25, 'CCI exit threshold'),
        ParameterConfig('atr_period', 'int', 14, 7, 21, 7, 'ATR period for volatility')
    ],
    'momentum_multi_strategy': [
        ParameterConfig('roc_period', 'int', 12, 6, 20, 2, 'Rate of Change period'),
        ParameterConfig('roc_threshold', 'float', 2.0, 0.5, 5.0, 0.5, 'ROC threshold for entry signal'),
        ParameterConfig('rsi_period', 'int', 14, 7, 21, 7, 'RSI period'),
        ParameterConfig('rsi_min', 'int', 40, 30, 50, 5, 'Minimum RSI for entry'),
        ParameterConfig('rsi_max', 'int', 60, 50, 70, 5, 'Maximum RSI for entry'),
        ParameterConfig('rsi_exit', 'int', 70, 60, 80, 5, 'RSI exit threshold')
    ],
    'adx_strategy': [
        ParameterConfig('ma_short_period', 'int', 20, 10, 30, 5, 'Short moving average period'),
        ParameterConfig('ma_long_period', 'int', 50, 30, 100, 10, 'Long moving average period'),
        ParameterConfig('boll_period', 'int', 14, 10, 20, 5, 'Bollinger Bands period'),
        ParameterConfig('adx_threshold', 'int', 25, 20, 30, 5, 'ADX threshold for trend strength')
    ],
    'tema_macd_strategy': [
        ParameterConfig('macd1', 'int', 12, 8, 16, 2, 'MACD fast period'),
        ParameterConfig('macd2', 'int', 26, 20, 30, 2, 'MACD slow period'),
        ParameterConfig('macdsig', 'int', 9, 5, 13, 2, 'MACD signal period'),
        ParameterConfig('tema_period', 'int', 12, 8, 20, 4, 'TEMA period')
    ],
    'tema_crossover_strategy': [
        ParameterConfig('tema_short_period', 'int', 20, 10, 30, 5, 'Short TEMA period'),
        ParameterConfig('tema_long_period', 'int', 60, 40, 80, 10, 'Long TEMA period'),
        ParameterConfig('volume_period', 'int', 14, 7, 21, 7, 'Volume SMA period')
    ],
    'alligator_strategy': [
        ParameterConfig('lips_period', 'int', 5, 3, 8, 1, 'Alligator lips (fastest MA) period'),
        ParameterConfig('teeth_period', 'int', 8, 5, 13, 2, 'Alligator teeth (medium MA) period'),
        ParameterConfig('jaws_period', 'int', 13, 8, 21, 3, 'Alligator jaws (slowest MA) period'),
        ParameterConfig('ema_period', 'int', 200, 150, 250, 25, 'Long-term EMA filter period')
    ],
    'cmf_atr_macd_strategy': [
        ParameterConfig('macd1', 'int', 12, 8, 16, 2, 'MACD fast period'),
        ParameterConfig('macd2', 'int', 26, 20, 30, 2, 'MACD slow period'),
        ParameterConfig('macdsig', 'int', 9, 5, 13, 2, 'MACD signal period'),
        ParameterConfig('atrperiod', 'int', 14, 7, 21, 7, 'ATR period'),
        ParameterConfig('atrdist', 'float', 2.0, 1.0, 3.0, 0.5, 'ATR distance multiplier for stops')
    ]
}

def get_strategy_parameters(strategy_name: str) -> List[Dict[str, Any]]:
    config = STRATEGY_OPTIMIZATION_CONFIGS.get(strategy_name, [])
    return [param.to_dict() for param in config]

def get_default_parameters(strategy_name: str) -> Dict[str, Union[int, float]]:
    config = STRATEGY_OPTIMIZATION_CONFIGS.get(strategy_name, [])
    return {param.name: param.default for param in config}
