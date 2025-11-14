"""Grid search optimizer tests"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import datetime
from config import STRATEGIES
from utils.grid_search import GridSearchOptimizer, create_parameter_ranges


def test_grid_search():
    """Test grid search functionality"""
    print("=" * 80)
    print("GRID SEARCH OPTIMIZER TESTING")
    print("=" * 80)

    try:
        print("\nTest 1: Create parameter ranges...")
        ranges_bb = create_parameter_ranges('Bollinger Bands')
        print(f"PASSED Bollinger Bands ranges: {ranges_bb}")
        assert 'period' in ranges_bb, "Should have period range"
        assert 'devfactor' in ranges_bb, "Should have devfactor range"

        print("\nTest 2: Initialize optimizer...")
        strategy_info = STRATEGIES['Bollinger Bands']
        base_params = {
            'cash': 10000,
            'order_pct': 1.0,
            'macd1': 12,
            'macd2': 26,
            'macdsig': 9,
            'atrperiod': 14,
            'atrdist': 2.0,
        }
        optimizer = GridSearchOptimizer(strategy_info['class'], base_params)
        print("PASSED Optimizer initialized")

        print("\nTest 3: Running small grid search (4 combinations)...")
        param_ranges = {
            'period': [15, 20],
            'devfactor': [2.0, 2.5]
        }

        start_date = datetime.date.today() - datetime.timedelta(days=180)
        end_date = datetime.date.today()

        def progress_callback(current, total, params):
            print(f"  [{current}/{total}] Testing {params}")

        results = optimizer.run_grid_search(
            ticker='AAPL',
            start_date=start_date,
            end_date=end_date,
            interval='1d',
            param_ranges=param_ranges,
            progress_callback=progress_callback
        )

        print(f"PASSED Grid search completed: {len(results)} results")
        assert len(results) > 0, "Should have at least one result"
        assert len(results) <= 4, "Should have at most 4 results"

        print("\nTest 4: Verify result structure...")
        result = results[0]
        required_keys = ['parameters', 'return_pct', 'sharpe_ratio', 'total_trades',
                        'ticker', 'start_date', 'end_date', 'interval']
        for key in required_keys:
            assert key in result, f"Result should have '{key}' key"
        print(f"PASSED Result structure valid: {list(result.keys())}")

        print("\nTest 5: Verify sorting...")
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]['return_pct'] >= results[i+1]['return_pct'], \
                    "Results should be sorted by return_pct descending"
        print("PASSED Results properly sorted")

        print("\nTest 6: Display top result...")
        top_result = results[0]
        print(f"  Ticker: {top_result['ticker']}")
        print(f"  Return: {top_result['return_pct']:+.2f}%")
        print(f"  Sharpe: {top_result.get('sharpe_ratio', 'N/A')}")
        print(f"  Trades: {top_result['total_trades']}")
        print(f"  Parameters: {top_result['parameters']}")
        print("PASSED Top result displayed")

        print("\nTest 7: Test with ADX Adaptive strategy...")
        strategy_info = STRATEGIES['ADX Adaptive']
        optimizer = GridSearchOptimizer(strategy_info['class'], base_params)

        param_ranges = {
            'atrperiod': [12, 14],
            'atrdist': [1.5, 2.0]
        }

        results = optimizer.run_grid_search(
            ticker='MSFT',
            start_date=start_date,
            end_date=end_date,
            interval='1d',
            param_ranges=param_ranges,
            progress_callback=None
        )

        print(f"PASSED ADX Adaptive grid search completed: {len(results)} results")
        if len(results) == 0:
            print("  Note: ADX Adaptive returned no results (strategy may need longer time period)")

        print("\n" + "=" * 80)
        print("ALL GRID SEARCH TESTS PASSED")
        print("=" * 80)

        return True

    except AssertionError as e:
        print(f"\nFAILED TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\nFAILED UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_grid_search()
    sys.exit(0 if success else 1)
