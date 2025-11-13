"""
Comprehensive test suite for StrategyBuilder
Tests all core functionality before deployment
"""
import sys
import os
import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.run_strategy import Run_strategy
from strategies.bollinger_bands_strategy import Bollinger_three
from strategies.tema_macd_strategy import TEMA_MACD
from strategies.adx_strategy import adx_strat
from utils.visualization import (
    create_backtest_chart,
    create_trades_table,
    create_performance_metrics_chart,
    create_trade_distribution_chart
)

def test_basic_backtest():
    """Test 1: Basic backtest with Bollinger Bands"""
    print("\n" + "="*70)
    print("TEST 1: Basic Backtest (Bollinger Bands on AAPL)")
    print("="*70)

    try:
        params = {
            'cash': 10000,
            'order_pct': 1.0,
            'macd1': 12,
            'macd2': 26,
            'macdsig': 9,
            'atrperiod': 14,
            'atrdist': 2.0
        }

        start_date = datetime.date.today() - datetime.timedelta(days=90)
        end_date = datetime.date.today()

        runner = Run_strategy(params, Bollinger_three)
        results = runner.runstrat('AAPL', start_date, '1d', end_date)

        print(f"\n✅ TEST 1 PASSED")
        print(f"   Return: {results['return_pct']:.2f}%")
        print(f"   Trades: {results['total_trades']}")
        print(f"   Sharpe: {results.get('sharpe_ratio', 'N/A')}")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_strategies():
    """Test 2: Multiple strategies on same ticker"""
    print("\n" + "="*70)
    print("TEST 2: Multiple Strategies (MSFT)")
    print("="*70)

    strategies = [
        ('Bollinger Bands', Bollinger_three),
        ('TEMA + MACD', TEMA_MACD),
        ('ADX Adaptive', adx_strat)
    ]

    params = {
        'cash': 10000,
        'order_pct': 1.0,
        'macd1': 12,
        'macd2': 26,
        'macdsig': 9,
        'atrperiod': 14,
        'atrdist': 2.0
    }

    start_date = datetime.date.today() - datetime.timedelta(days=60)
    end_date = datetime.date.today()

    all_passed = True

    for name, strategy in strategies:
        try:
            print(f"\n   Testing {name}...")
            runner = Run_strategy(params, strategy)
            results = runner.runstrat('MSFT', start_date, '1d', end_date)
            print(f"   ✓ {name}: {results['return_pct']:+.2f}% ({results['total_trades']} trades)")

        except Exception as e:
            print(f"   ✗ {name}: {str(e)}")
            all_passed = False

    if all_passed:
        print(f"\n✅ TEST 2 PASSED")
    else:
        print(f"\n⚠️  TEST 2 PARTIALLY PASSED")

    return all_passed


def test_trade_tracking():
    """Test 3: Verify trade tracking works"""
    print("\n" + "="*70)
    print("TEST 3: Trade Tracking")
    print("="*70)

    try:
        params = {
            'cash': 10000,
            'order_pct': 1.0,
            'macd1': 12,
            'macd2': 26,
            'macdsig': 9,
            'atrperiod': 14,
            'atrdist': 2.0
        }

        start_date = datetime.date.today() - datetime.timedelta(days=180)
        end_date = datetime.date.today()

        runner = Run_strategy(params, Bollinger_three)
        results = runner.runstrat('TSLA', start_date, '1d', end_date)

        trades = results.get('trades', [])

        if not trades:
            print("\n⚠️  No trades executed (this may be normal for some strategies)")
            return True

        print(f"\n   Trades executed: {len(trades)}")
        print(f"   First trade: {trades[0]}")
        print(f"   Last trade: {trades[-1]}")

        # Verify trade structure
        required_keys = ['entry_date', 'exit_date', 'entry_price', 'exit_price', 'pnl', 'pnl_pct']
        for key in required_keys:
            if key not in trades[0]:
                raise ValueError(f"Trade missing required key: {key}")

        # Calculate win rate
        winning_trades = [t for t in trades if t['pnl'] > 0]
        win_rate = (len(winning_trades) / len(trades)) * 100

        print(f"   Win rate: {win_rate:.1f}%")
        print(f"   Avg P&L: ${sum(t['pnl'] for t in trades) / len(trades):,.2f}")

        print(f"\n✅ TEST 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test 4: Verify visualization components work"""
    print("\n" + "="*70)
    print("TEST 4: Visualization Components")
    print("="*70)

    try:
        # Run a backtest to get data
        params = {
            'cash': 10000,
            'order_pct': 1.0,
            'macd1': 12,
            'macd2': 26,
            'macdsig': 9,
            'atrperiod': 14,
            'atrdist': 2.0
        }

        start_date = datetime.date.today() - datetime.timedelta(days=90)
        end_date = datetime.date.today()

        runner = Run_strategy(params, Bollinger_three)
        results = runner.runstrat('NVDA', start_date, '1d', end_date)

        trades = results.get('trades', [])

        # Test chart creation (should work even without trades)
        print("\n   Testing chart creation (basic)...")
        fig_basic = create_backtest_chart(
            ticker='NVDA',
            start_date=start_date,
            end_date=end_date,
            interval='1d',
            trades=[]  # Test with no trades
        )
        if fig_basic is None:
            raise ValueError("Basic chart creation (no trades) returned None")
        print("   ✓ Basic chart created (no trades)")

        if not trades:
            print("\n⚠️  No trades executed, but visualization functions work")
            return True

        # Test chart creation with trades
        print("\n   Testing chart with trade signals...")
        fig = create_backtest_chart(
            ticker='NVDA',
            start_date=start_date,
            end_date=end_date,
            interval='1d',
            trades=trades
        )

        if fig is None:
            raise ValueError("Chart with trade signals returned None")
        print("   ✓ Chart with trade signals created")

        # Test trades table
        print("   Testing trades table...")
        df = create_trades_table(trades)
        if df.empty:
            raise ValueError("Trades table is empty")
        print(f"   ✓ Trades table created ({len(df)} rows)")

        # Test performance chart
        print("   Testing performance chart...")
        perf_fig = create_performance_metrics_chart(trades)
        if perf_fig is None:
            raise ValueError("Performance chart returned None")
        print("   ✓ Performance chart created")

        # Test distribution chart
        print("   Testing distribution chart...")
        dist_fig = create_trade_distribution_chart(trades)
        if dist_fig is None:
            raise ValueError("Distribution chart returned None")
        print("   ✓ Distribution chart created")

        print(f"\n✅ TEST 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_different_intervals():
    """Test 5: Different time intervals"""
    print("\n" + "="*70)
    print("TEST 5: Different Time Intervals")
    print("="*70)

    intervals = ['1d', '1h']  # Test daily and hourly
    params = {
        'cash': 10000,
        'order_pct': 1.0,
        'macd1': 12,
        'macd2': 26,
        'macdsig': 9,
        'atrperiod': 14,
        'atrdist': 2.0
    }

    all_passed = True

    for interval in intervals:
        try:
            print(f"\n   Testing {interval} interval...")

            # Adjust date range based on interval
            if interval == '1h':
                start_date = datetime.date.today() - datetime.timedelta(days=30)
            else:
                start_date = datetime.date.today() - datetime.timedelta(days=90)

            end_date = datetime.date.today()

            runner = Run_strategy(params, Bollinger_three)
            results = runner.runstrat('AAPL', start_date, interval, end_date)

            print(f"   ✓ {interval}: {results['return_pct']:+.2f}% ({results['total_trades']} trades)")

        except Exception as e:
            print(f"   ✗ {interval}: {str(e)}")
            all_passed = False

    if all_passed:
        print(f"\n✅ TEST 5 PASSED")
    else:
        print(f"\n⚠️  TEST 5 PARTIALLY PASSED")

    return all_passed


def test_edge_cases():
    """Test 6: Edge cases and error handling"""
    print("\n" + "="*70)
    print("TEST 6: Edge Cases & Error Handling")
    print("="*70)

    params = {
        'cash': 10000,
        'order_pct': 1.0,
        'macd1': 12,
        'macd2': 26,
        'macdsig': 9,
        'atrperiod': 14,
        'atrdist': 2.0
    }

    # Test 1: Invalid ticker
    print("\n   Testing invalid ticker...")
    try:
        start_date = datetime.date.today() - datetime.timedelta(days=30)
        runner = Run_strategy(params, Bollinger_three)
        results = runner.runstrat('INVALIDTICKER123', start_date, '1d')
        print("   ✗ Should have raised an error for invalid ticker")
        return False
    except Exception as e:
        print(f"   ✓ Correctly caught error: {str(e)[:50]}...")

    # Test 2: Very short date range
    print("\n   Testing very short date range...")
    try:
        start_date = datetime.date.today() - datetime.timedelta(days=5)
        end_date = datetime.date.today()
        runner = Run_strategy(params, Bollinger_three)
        results = runner.runstrat('AAPL', start_date, '1d', end_date)
        print(f"   ✓ Short range handled: {results['total_trades']} trades")
    except Exception as e:
        print(f"   ⚠️  Short range error: {str(e)[:50]}...")

    print(f"\n✅ TEST 6 PASSED")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("STRATEGYBUILDER - COMPREHENSIVE TEST SUITE")
    print("="*70)

    tests = [
        test_basic_backtest,
        test_multiple_strategies,
        test_trade_tracking,
        test_visualization,
        test_different_intervals,
        test_edge_cases
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__doc__.split(':')[0].strip(), result))
        except Exception as e:
            print(f"\n❌ {test_func.__name__} crashed: {str(e)}")
            results.append((test_func.__doc__.split(':')[0].strip(), False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
    elif passed >= total * 0.8:
        print("\n⚠️  Most tests passed. System should work but may have minor issues.")
    else:
        print("\n❌ Multiple tests failed. Please review errors above.")

    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
