"""Comprehensive strategy testing - Test all 12 strategies with multiple configurations"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import datetime
import pandas as pd
from typing import Dict, List, Any

from config import STRATEGIES
from core.run_strategy import Run_strategy


TEST_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
START_DATE = datetime.date.today() - datetime.timedelta(days=365)
END_DATE = datetime.date.today()
INTERVAL = '1d'
BASE_CASH = 10000

STRATEGY_VARIATIONS = {
    'Bollinger Bands': [
        {'period': 10, 'devfactor': 1.5},
        {'period': 15, 'devfactor': 2.0},
        {'period': 20, 'devfactor': 2.0},
        {'period': 25, 'devfactor': 2.5},
        {'period': 30, 'devfactor': 3.0},
    ],
    'TEMA + MACD': [
        {'macd1': 8, 'macd2': 20, 'macdsig': 7},
        {'macd1': 10, 'macd2': 24, 'macdsig': 9},
        {'macd1': 12, 'macd2': 26, 'macdsig': 9},
        {'macd1': 14, 'macd2': 28, 'macdsig': 11},
        {'macd1': 16, 'macd2': 32, 'macdsig': 11},
    ],
    'Alligator': [
        {},
        {},
        {},
        {},
        {},
    ],
    'ADX Adaptive': [
        {'atrperiod': 10, 'atrdist': 1.5},
        {'atrperiod': 12, 'atrdist': 2.0},
        {'atrperiod': 14, 'atrdist': 2.0},
        {'atrperiod': 16, 'atrdist': 2.5},
        {'atrperiod': 18, 'atrdist': 3.0},
    ],
    'CMF + ATR + MACD': [
        {},
        {},
        {},
        {},
        {},
    ],
    'TEMA Crossover': [
        {},
        {},
        {},
        {},
        {},
    ],
    'RSI + Stochastic': [
        {'rsi_period': 10, 'rsi_oversold': 25, 'rsi_overbought': 75},
        {'rsi_period': 12, 'rsi_oversold': 30, 'rsi_overbought': 70},
        {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70},
        {'rsi_period': 16, 'rsi_oversold': 35, 'rsi_overbought': 65},
        {'rsi_period': 20, 'rsi_oversold': 35, 'rsi_overbought': 65},
    ],
    'Williams %R': [
        {'period': 10, 'oversold': -85, 'overbought': -15},
        {'period': 12, 'oversold': -80, 'overbought': -20},
        {'period': 14, 'oversold': -80, 'overbought': -20},
        {'period': 16, 'oversold': -75, 'overbought': -25},
        {'period': 20, 'oversold': -70, 'overbought': -30},
    ],
    'MFI (Money Flow)': [
        {'period': 10, 'oversold': 15, 'overbought': 85},
        {'period': 12, 'oversold': 20, 'overbought': 80},
        {'period': 14, 'oversold': 20, 'overbought': 80},
        {'period': 16, 'oversold': 25, 'overbought': 75},
        {'period': 20, 'oversold': 30, 'overbought': 70},
    ],
    'CCI + ATR': [
        {'cci_period': 15, 'cci_entry': -120, 'cci_exit': 120, 'atr_period': 12},
        {'cci_period': 18, 'cci_entry': -110, 'cci_exit': 110, 'atr_period': 14},
        {'cci_period': 20, 'cci_entry': -100, 'cci_exit': 100, 'atr_period': 14},
        {'cci_period': 22, 'cci_entry': -90, 'cci_exit': 90, 'atr_period': 16},
        {'cci_period': 25, 'cci_entry': -80, 'cci_exit': 80, 'atr_period': 18},
    ],
    'Momentum Multi': [
        {'roc_period': 10, 'roc_threshold': 1.5, 'rsi_period': 12},
        {'roc_period': 12, 'roc_threshold': 2.0, 'rsi_period': 14},
        {'roc_period': 12, 'roc_threshold': 2.0, 'rsi_period': 14},
        {'roc_period': 14, 'roc_threshold': 2.5, 'rsi_period': 16},
        {'roc_period': 16, 'roc_threshold': 3.0, 'rsi_period': 18},
    ],
    'Keltner Channel': [
        {'ema_period': 15, 'atr_period': 8, 'atr_multiplier': 1.5},
        {'ema_period': 18, 'atr_period': 10, 'atr_multiplier': 2.0},
        {'ema_period': 20, 'atr_period': 10, 'atr_multiplier': 2.0},
        {'ema_period': 22, 'atr_period': 12, 'atr_multiplier': 2.5},
        {'ema_period': 25, 'atr_period': 14, 'atr_multiplier': 3.0},
    ],
}


def build_parameters(base_params: Dict[str, Any], strategy_params: Dict[str, Any]) -> Dict[str, Any]:
    """Build complete parameter dictionary"""
    params = {
        'cash': BASE_CASH,
        'order_pct': 1.0,
        'macd1': 12,
        'macd2': 26,
        'macdsig': 9,
        'atrperiod': 14,
        'atrdist': 2.0,
    }
    params.update(base_params)
    params.update(strategy_params)
    return params


def run_single_test(strategy_name: str, stock: str, config_idx: int, params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single backtest and return results"""
    strategy_info = STRATEGIES[strategy_name]
    strategy_class = strategy_info['class']

    full_params = build_parameters(strategy_info.get('params', {}), params)

    try:
        runner = Run_strategy(full_params, strategy_class)
        results = runner.runstrat(stock, START_DATE, INTERVAL, END_DATE)

        return {
            'strategy': strategy_name,
            'stock': stock,
            'config_idx': config_idx,
            'params': params,
            'status': 'SUCCESS',
            'return_pct': results.get('return_pct', 0),
            'sharpe_ratio': results.get('sharpe_ratio', None),
            'total_trades': results.get('total_trades', 0),
            'max_drawdown': results.get('max_drawdown', None),
            'error': None
        }
    except Exception as e:
        return {
            'strategy': strategy_name,
            'stock': stock,
            'config_idx': config_idx,
            'params': params,
            'status': 'FAILED',
            'return_pct': None,
            'sharpe_ratio': None,
            'total_trades': None,
            'max_drawdown': None,
            'error': str(e)
        }


def run_comprehensive_tests():
    """Run comprehensive tests for all strategies"""
    print("=" * 80)
    print("COMPREHENSIVE STRATEGY TESTING")
    print("=" * 80)
    print(f"Testing {len(STRATEGIES)} strategies × 5 configurations × {len(TEST_STOCKS)} stocks")
    print(f"Total tests: {len(STRATEGIES) * 5 * len(TEST_STOCKS)}")
    print(f"Date range: {START_DATE} to {END_DATE}")
    print(f"Interval: {INTERVAL}")
    print("=" * 80)
    print()

    all_results = []
    total_tests = len(STRATEGIES) * 5 * len(TEST_STOCKS)
    current_test = 0

    for strategy_name in STRATEGIES.keys():
        print(f"\n{'='*80}")
        print(f"TESTING STRATEGY: {strategy_name}")
        print(f"{'='*80}")

        variations = STRATEGY_VARIATIONS.get(strategy_name, [{}, {}, {}, {}, {}])

        for config_idx, params in enumerate(variations, 1):
            for stock in TEST_STOCKS:
                current_test += 1
                progress = (current_test / total_tests) * 100

                print(f"[{current_test}/{total_tests}] ({progress:.1f}%) "
                      f"{strategy_name} | Config #{config_idx} | {stock}...", end=' ')

                result = run_single_test(strategy_name, stock, config_idx, params)
                all_results.append(result)

                if result['status'] == 'SUCCESS':
                    print(f"PASSED Return: {result['return_pct']:+.2f}% | Trades: {result['total_trades']}")
                else:
                    print(f"FAILED: {result['error'][:50]}")

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    successful_tests = [r for r in all_results if r['status'] == 'SUCCESS']
    failed_tests = [r for r in all_results if r['status'] == 'FAILED']

    print(f"Total Tests: {len(all_results)}")
    print(f"Successful: {len(successful_tests)} ({len(successful_tests)/len(all_results)*100:.1f}%)")
    print(f"Failed: {len(failed_tests)} ({len(failed_tests)/len(all_results)*100:.1f}%)")

    if successful_tests:
        print(f"\nPerformance Statistics:")
        returns = [r['return_pct'] for r in successful_tests if r['return_pct'] is not None]
        if returns:
            print(f"  Average Return: {sum(returns)/len(returns):.2f}%")
            print(f"  Best Return: {max(returns):.2f}%")
            print(f"  Worst Return: {min(returns):.2f}%")

        trades = [r['total_trades'] for r in successful_tests]
        print(f"  Average Trades: {sum(trades)/len(trades):.1f}")

    print(f"\n{'='*80}")
    print("STRATEGY-LEVEL SUMMARY")
    print(f"{'='*80}")

    for strategy_name in STRATEGIES.keys():
        strategy_results = [r for r in all_results if r['strategy'] == strategy_name]
        strategy_success = [r for r in strategy_results if r['status'] == 'SUCCESS']

        if strategy_success:
            avg_return = sum(r['return_pct'] for r in strategy_success) / len(strategy_success)
            success_rate = len(strategy_success) / len(strategy_results) * 100
            print(f"{strategy_name:30} | Tests: {len(strategy_results)} | "
                  f"Success: {success_rate:.1f}% | Avg Return: {avg_return:+.2f}%")
        else:
            print(f"{strategy_name:30} | Tests: {len(strategy_results)} | All FAILED")

    df = pd.DataFrame(all_results)
    output_file = 'test_results_comprehensive.csv'
    df.to_csv(output_file, index=False)
    print(f"\nDetailed results saved to: {output_file}")

    print("\n" + "=" * 80)

    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
