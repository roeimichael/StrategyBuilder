"""
StrategyBuilder - Main entry point for backtesting strategies
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import datetime
import yaml
from dateutil.relativedelta import relativedelta

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from core.run_strategy import Run_strategy
from strategies.bollinger_bands_strategy import Bollinger_three
from strategies.tema_macd_strategy import TEMA_MACD
from strategies.alligator_strategy import Alligator_strategy
from strategies.adx_strategy import ADX_strategy
from strategies.cmf_atr_macd_strategy import CMF_ATR_MACD


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file"""
    if config_path is None:
        # Default to config.yaml in project root
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')

    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        print("Using default parameters...")
        return get_default_config()


def get_default_config() -> dict:
    """Return default configuration if config.yaml is missing"""
    return {
        'backtesting': {'cash': 10000, 'order_percentage': 1.0},
        'indicators': {
            'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
            'atr': {'period': 14, 'distance': 2.0}
        },
        'data': {'default_interval': '1d', 'default_lookback_years': 1}
    }


def main():
    """Main execution function"""

    # Load configuration
    config = load_config()

    # Extract parameters from config
    backtesting_config = config.get('backtesting', {})
    indicator_config = config.get('indicators', {})
    data_config = config.get('data', {})

    # Build parameters dictionary for strategy
    parameters = {
        'cash': backtesting_config.get('cash', 10000),
        'macd1': indicator_config.get('macd', {}).get('fast_period', 12),
        'macd2': indicator_config.get('macd', {}).get('slow_period', 26),
        'macdsig': indicator_config.get('macd', {}).get('signal_period', 9),
        'atrperiod': indicator_config.get('atr', {}).get('period', 14),
        'atrdist': indicator_config.get('atr', {}).get('distance', 2.0),
        'order_pct': backtesting_config.get('order_percentage', 1.0),
    }

    # Backtest configuration
    ticker = "AAPL"  # Change this to test different tickers
    start_date = datetime.date.today() - relativedelta(
        years=data_config.get('default_lookback_years', 1)
    )
    interval = data_config.get('default_interval', '1d')

    # Select strategy (change this to test different strategies)
    strategy = Bollinger_three

    print(f"{'='*60}")
    print(f"StrategyBuilder - Backtesting Engine")
    print(f"{'='*60}")
    print(f"Ticker: {ticker}")
    print(f"Start Date: {start_date}")
    print(f"Interval: {interval}")
    print(f"Strategy: {strategy.__name__}")
    print(f"Initial Cash: ${parameters['cash']:,.2f}")
    print(f"{'='*60}\n")

    # Run backtest
    run_cerebro = Run_strategy(parameters, strategy)
    run_cerebro.runstrat(ticker, start_date, interval)


if __name__ == '__main__':
    main()
