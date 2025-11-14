"""Configuration and constants for StrategyBuilder Pro"""

from strategies.adx_strategy import adx_strat
from strategies.alligator_strategy import Alligator_strategy
from strategies.bollinger_bands_strategy import Bollinger_three
from strategies.cci_atr_strategy import CCI_ATR_Strategy
from strategies.cmf_atr_macd_strategy import MACD_CMF_ATR_Strategy
from strategies.keltner_channel_strategy import Keltner_Channel
from strategies.mfi_strategy import MFI_Strategy
from strategies.momentum_multi_strategy import Momentum_Multi
from strategies.rsi_stochastic_strategy import RSI_Stochastic
from strategies.tema_crossover_strategy import Tema20_tema60
from strategies.tema_macd_strategy import TEMA_MACD
from strategies.williams_r_strategy import Williams_R

STRATEGIES = {
    'Bollinger Bands': {
        'class': Bollinger_three,
        'description': 'Mean reversion using Bollinger Bands',
        'params': {'period': 20, 'devfactor': 2}
    },
    'TEMA + MACD': {
        'class': TEMA_MACD,
        'description': 'Triple EMA crossover with MACD confirmation',
        'params': {}
    },
    'Alligator': {
        'class': Alligator_strategy,
        'description': 'Bill Williams Alligator indicator',
        'params': {}
    },
    'ADX Adaptive': {
        'class': adx_strat,
        'description': 'Adaptive strategy for trending vs ranging markets',
        'params': {}
    },
    'CMF + ATR + MACD': {
        'class': MACD_CMF_ATR_Strategy,
        'description': 'Multi-indicator with volume and volatility',
        'params': {}
    },
    'TEMA Crossover': {
        'class': Tema20_tema60,
        'description': 'TEMA 20/60 crossover with volume filter',
        'params': {}
    },
    'RSI + Stochastic': {
        'class': RSI_Stochastic,
        'description': 'Oversold/overbought using RSI and Stochastic oscillators',
        'params': {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70,
                   'stoch_period': 14, 'stoch_oversold': 20, 'stoch_overbought': 80}
    },
    'Williams %R': {
        'class': Williams_R,
        'description': 'Mean reversion using Williams %R momentum indicator',
        'params': {'period': 14, 'oversold': -80, 'overbought': -20}
    },
    'MFI (Money Flow)': {
        'class': MFI_Strategy,
        'description': 'Volume-weighted RSI for price/volume divergence',
        'params': {'period': 14, 'oversold': 20, 'overbought': 80}
    },
    'CCI + ATR': {
        'class': CCI_ATR_Strategy,
        'description': 'Volatility breakout using CCI and ATR',
        'params': {'cci_period': 20, 'cci_entry': -100, 'cci_exit': 100, 'atr_period': 14}
    },
    'Momentum Multi': {
        'class': Momentum_Multi,
        'description': 'Multi-indicator momentum: ROC + RSI + OBV',
        'params': {'roc_period': 12, 'roc_threshold': 2.0, 'rsi_period': 14,
                   'rsi_min': 40, 'rsi_max': 60, 'rsi_exit': 70}
    },
    'Keltner Channel': {
        'class': Keltner_Channel,
        'description': 'Dynamic channel breakout using EMA and ATR',
        'params': {'ema_period': 20, 'atr_period': 10, 'atr_multiplier': 2.0}
    },
}

DEFAULT_PARAMS = {
    'cash': 100000,
    'commission': 0.001,
}

INTERVALS = ['1d', '1wk', '1mo', '1h', '5m', '15m', '30m', '60m']
