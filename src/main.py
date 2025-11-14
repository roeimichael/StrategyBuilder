"""StrategyBuilder - Interactive Backtesting CLI"""

import os
import sys
import datetime
import yaml
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(__file__))

from core.run_strategy import Run_strategy
from strategies.bollinger_bands_strategy import Bollinger_three
from strategies.tema_macd_strategy import TEMA_MACD
from strategies.alligator_strategy import Alligator_strategy
from strategies.adx_strategy import adx_strat
from strategies.cmf_atr_macd_strategy import MACD_CMF_ATR_Strategy
from strategies.tema_crossover_strategy import Tema20_tema60

STRATEGIES = {
    '1': ('Bollinger Bands', Bollinger_three, 'Mean reversion using Bollinger Bands'),
    '2': ('TEMA + MACD', TEMA_MACD, 'Triple EMA crossover with MACD confirmation'),
    '3': ('Alligator', Alligator_strategy, 'Bill Williams Alligator indicator'),
    '4': ('ADX Adaptive', adx_strat, 'Adaptive strategy for trending vs ranging markets'),
    '5': ('CMF + ATR + MACD', MACD_CMF_ATR_Strategy, 'Multi-indicator with volume and volatility'),
    '6': ('TEMA Crossover', Tema20_tema60, 'TEMA 20/60 crossover with volume filter'),
}

INTERVALS = {
    '1': ('1 hour', '1h'),
    '2': ('1 day', '1d'),
    '3': ('1 week', '1wk'),
    '4': ('5 minutes', '5m'),
    '5': ('15 minutes', '15m'),
    '6': ('30 minutes', '30m'),
    '7': ('90 minutes', '90m'),
}


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')

    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        print("Using default parameters...")
        return get_default_config()


def get_default_config() -> dict:
    """Return default configuration"""
    return {
        'backtesting': {'cash': 10000, 'order_percentage': 1.0, 'commission': 0.001},
        'indicators': {
            'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
            'atr': {'period': 14, 'distance': 2.0},
            'moving_averages': {'short_period': 20, 'medium_period': 50, 'long_period': 200},
            'bollinger': {'period': 20, 'std_dev': 2},
        },
        'data': {'default_interval': '1d', 'default_lookback_years': 1}
    }


def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print(" " * 15 + "STRATEGYBUILDER - BACKTESTING ENGINE")
    print("="*70 + "\n")


def get_tickers() -> List[str]:
    """Get list of tickers from user"""
    print("STOCK SELECTION")
    print("-" * 70)
    user_input = input("Enter stock ticker(s) (comma-separated for multiple, e.g., AAPL,MSFT,TSLA): ").strip().upper()

    if not user_input:
        print("No ticker entered. Using default: AAPL")
        return ['AAPL']

    tickers = [t.strip() for t in user_input.split(',')]
    print(f"Selected {len(tickers)} ticker(s): {', '.join(tickers)}\n")
    return tickers


def get_interval() -> str:
    """Get time interval from user"""
    print("TIME INTERVAL")
    print("-" * 70)
    for key, (name, _) in INTERVALS.items():
        print(f"  [{key}] {name}")

    choice = input("\nSelect interval (1-7) [default: 2]: ").strip()

    if not choice or choice not in INTERVALS:
        print("Using default: 1 day\n")
        return '1d'

    name, interval = INTERVALS[choice]
    print(f"Selected: {name}\n")
    return interval


def get_dates() -> tuple:
    """Get start and end dates from user"""
    print("DATE RANGE")
    print("-" * 70)

    start_input = input("Enter start date (YYYY-MM-DD) or days back (e.g., 365) [default: 365 days]: ").strip()

    if not start_input:
        start_date = datetime.date.today() - datetime.timedelta(days=365)
        print(f"Using default start date: {start_date}")
    elif start_input.isdigit():
        days = int(start_input)
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        print(f"Start date: {start_date} ({days} days ago)")
    else:
        try:
            start_date = datetime.datetime.strptime(start_input, '%Y-%m-%d').date()
            print(f"Start date: {start_date}")
        except ValueError:
            print("Invalid date format. Using default (365 days ago)")
            start_date = datetime.date.today() - datetime.timedelta(days=365)

    end_input = input("Enter end date (YYYY-MM-DD) [default: today]: ").strip()

    if not end_input:
        end_date = datetime.date.today()
        print(f"Using default end date: {end_date}\n")
    else:
        try:
            end_date = datetime.datetime.strptime(end_input, '%Y-%m-%d').date()
            print(f"End date: {end_date}\n")
        except ValueError:
            print("Invalid date format. Using today")
            end_date = datetime.date.today()

    return start_date, end_date


def get_strategy() -> tuple:
    """Get strategy selection from user"""
    print("STRATEGY SELECTION")
    print("-" * 70)
    for key, (name, _, description) in STRATEGIES.items():
        print(f"  [{key}] {name}")
        print(f"      {description}")

    choice = input("\nSelect strategy (1-6) [default: 1]: ").strip()

    if not choice or choice not in STRATEGIES:
        print("Using default: Bollinger Bands\n")
        return STRATEGIES['1'][0], STRATEGIES['1'][1]

    name, strategy_class, _ = STRATEGIES[choice]
    print(f"Selected: {name}\n")
    return name, strategy_class


def get_starting_cash() -> float:
    """Get starting cash from user"""
    print("STARTING CAPITAL")
    print("-" * 70)
    cash_input = input("Enter starting cash amount [default: $10,000]: $").strip()

    if not cash_input:
        print("Using default: $10,000\n")
        return 10000.0

    try:
        cash = float(cash_input.replace(',', ''))
        print(f"Starting cash: ${cash:,.2f}\n")
        return cash
    except ValueError:
        print("Invalid amount. Using default: $10,000\n")
        return 10000.0


def get_additional_params(config: dict) -> dict:
    """Get additional configurable parameters"""
    print("ADDITIONAL PARAMETERS")
    print("-" * 70)
    print("Configure additional parameters? (y/n) [default: n]: ", end='')

    if input().strip().lower() != 'y':
        print("Using default parameters from config.yaml\n")
        return {}

    print("\nAdjustable parameters:")
    params = {}

    print("\n1. Position Size (% of capital per trade)")
    order_pct = input("   Enter percentage (0-100) [default: 100]: ").strip()
    if order_pct:
        try:
            params['order_pct'] = float(order_pct) / 100
        except ValueError:
            pass

    print("\n2. MACD Parameters")
    macd_fast = input("   Fast period [default: 12]: ").strip()
    macd_slow = input("   Slow period [default: 26]: ").strip()
    macd_signal = input("   Signal period [default: 9]: ").strip()

    if macd_fast:
        try:
            params['macd1'] = int(macd_fast)
        except ValueError:
            pass
    if macd_slow:
        try:
            params['macd2'] = int(macd_slow)
        except ValueError:
            pass
    if macd_signal:
        try:
            params['macdsig'] = int(macd_signal)
        except ValueError:
            pass

    print("\n3. ATR (Average True Range) Parameters")
    atr_period = input("   Period [default: 14]: ").strip()
    atr_dist = input("   Distance multiplier [default: 2.0]: ").strip()

    if atr_period:
        try:
            params['atrperiod'] = int(atr_period)
        except ValueError:
            pass
    if atr_dist:
        try:
            params['atrdist'] = float(atr_dist)
        except ValueError:
            pass

    print("\nCustom parameters configured\n")
    return params


def build_parameters(config: dict, cash: float, custom_params: dict) -> dict:
    """Build complete parameters dictionary"""
    backtesting_config = config.get('backtesting', {})
    indicator_config = config.get('indicators', {})

    parameters = {
        'cash': cash,
        'macd1': indicator_config.get('macd', {}).get('fast_period', 12),
        'macd2': indicator_config.get('macd', {}).get('slow_period', 26),
        'macdsig': indicator_config.get('macd', {}).get('signal_period', 9),
        'atrperiod': indicator_config.get('atr', {}).get('period', 14),
        'atrdist': indicator_config.get('atr', {}).get('distance', 2.0),
        'order_pct': backtesting_config.get('order_percentage', 1.0),
    }

    parameters.update(custom_params)

    return parameters


def print_summary(tickers: List[str], start_date, end_date, interval: str,
                 strategy_name: str, parameters: dict):
    """Print backtest configuration summary"""
    print("\n" + "="*70)
    print(" " * 25 + "BACKTEST CONFIGURATION")
    print("="*70)
    print(f"Ticker(s):        {', '.join(tickers)}")
    print(f"Strategy:         {strategy_name}")
    print(f"Date Range:       {start_date} to {end_date}")
    print(f"Interval:         {interval}")
    print(f"Starting Cash:    ${parameters['cash']:,.2f}")
    print(f"Position Size:    {parameters['order_pct']*100:.0f}%")
    print(f"MACD:             {parameters['macd1']}/{parameters['macd2']}/{parameters['macdsig']}")
    print(f"ATR:              Period={parameters['atrperiod']}, Distance={parameters['atrdist']}")
    print("="*70 + "\n")

    input("Press Enter to start backtesting...")
    print()


def run_backtest(ticker: str, start_date, end_date, interval: str,
                strategy_class, parameters: dict) -> Dict[str, Any]:
    """Run backtest for a single ticker"""
    print(f"\n{'='*70}")
    print(f"Running backtest for {ticker}...")
    print(f"{'='*70}\n")

    try:
        run_cerebro = Run_strategy(parameters, strategy_class)
        results = run_cerebro.runstrat(ticker, start_date, interval, end_date)
        return results
    except Exception as e:
        print(f"Error running backtest for {ticker}: {str(e)}\n")
        return None


def print_results_summary(all_results: Dict[str, Dict[str, Any]]):
    """Print comprehensive summary of all backtests"""
    print("\n" + "="*70)
    print(" " * 20 + "BACKTEST RESULTS SUMMARY")
    print("="*70 + "\n")

    for ticker, results in all_results.items():
        if results is None:
            continue

        print(f"{'-'*70}")
        print(f"  {ticker}")
        print(f"{'-'*70}")
        print(f"  Starting Value:        ${results['start_value']:,.2f}")
        print(f"  Final Value:           ${results['end_value']:,.2f}")
        print(f"  Total Return:          {results['return_pct']:+.2f}%")
        print(f"  Total Profit/Loss:     ${results['pnl']:+,.2f}")

        if results.get('sharpe_ratio'):
            print(f"  Sharpe Ratio:          {results['sharpe_ratio']:.3f}")

        if results.get('max_drawdown'):
            print(f"  Max Drawdown:          {results['max_drawdown']:.2f}%")

        if results.get('total_trades'):
            print(f"  Total Trades:          {results['total_trades']}")

        print()

    print("="*70 + "\n")


def main():
    """Main execution function"""
    print_banner()

    config = load_config()

    tickers = get_tickers()
    interval = get_interval()
    start_date, end_date = get_dates()
    strategy_name, strategy_class = get_strategy()
    cash = get_starting_cash()
    custom_params = get_additional_params(config)

    parameters = build_parameters(config, cash, custom_params)

    print_summary(tickers, start_date, end_date, interval, strategy_name, parameters)

    all_results = {}
    for ticker in tickers:
        results = run_backtest(ticker, start_date, end_date, interval, strategy_class, parameters)
        all_results[ticker] = results

    print_results_summary(all_results)

    print("Backtesting complete!\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBacktesting interrupted by user. Exiting...\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}\n")
        sys.exit(1)
