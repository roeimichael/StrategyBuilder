"""
Backtest vs Optimization Comparison Test

This script runs the same strategy parameters through both:
1. The normal backtest endpoint
2. The optimization endpoint

It compares the results to identify discrepancies in the logic.

Key Differences Being Investigated:
- Position sizing (backtest uses 95% PercentSizer, optimizer uses no sizer)
- Commission settings (optimizer explicitly sets 0.1%, backtest uses default)
- Parameter passing method
- Analyzer configurations
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8086"

def test_backtest_vs_optimization():
    """
    Compare backtest and optimization results for the same parameters
    """
    print("="*80)
    print("BACKTEST VS OPTIMIZATION COMPARISON TEST")
    print("="*80)
    print(f"Testing: Bollinger Bands Strategy on AAPL")
    print(f"Parameter: devfactor = 2.0")
    print(f"Date Range: 2024-01-01 to 2024-12-31")
    print("="*80)

    # Test parameters
    ticker = "AAPL"
    strategy = "bollinger_bands_strategy"
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    interval = "1d"
    cash = 10000.0

    # Parameter we're testing
    test_devfactor = 2.0

    # ============================================================================
    # STEP 1: Run normal backtest with devfactor=2.0
    # ============================================================================
    print("\n" + "="*80)
    print("STEP 1: Running BACKTEST with devfactor=2.0")
    print("="*80)

    backtest_payload = {
        "ticker": ticker,
        "strategy": strategy,
        "start_date": start_date,
        "end_date": end_date,
        "interval": interval,
        "cash": cash,
        "parameters": {
            "period": 20,
            "devfactor": test_devfactor
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/backtest",
            json=backtest_payload,
            timeout=30
        )

        if response.status_code == 200:
            backtest_result = response.json()
            print(f"✓ Backtest completed successfully")
            print(f"\nBacktest Results:")
            print(f"  Start Value:  ${backtest_result['start_value']:,.2f}")
            print(f"  End Value:    ${backtest_result['end_value']:,.2f}")
            print(f"  PnL:          ${backtest_result['pnl']:,.2f}")
            print(f"  Return:       {backtest_result['return_pct']:.2f}%")
            print(f"  Total Trades: {backtest_result['total_trades']}")
            print(f"  Sharpe Ratio: {backtest_result['sharpe_ratio']}")
            print(f"  Max Drawdown: {backtest_result['max_drawdown']}%")

            if backtest_result.get('advanced_metrics'):
                adv = backtest_result['advanced_metrics']
                print(f"\n  Advanced Metrics:")
                print(f"    Winning Trades: {adv.get('winning_trades', 'N/A')}")
                print(f"    Losing Trades:  {adv.get('losing_trades', 'N/A')}")
                print(f"    Win Rate:       {adv.get('win_rate', 'N/A')}%")
        else:
            print(f"✗ Backtest failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Backtest error: {str(e)}")
        return False

    # ============================================================================
    # STEP 2: Run optimization with devfactor=[2.0, 3.0, 4.0]
    # ============================================================================
    print("\n" + "="*80)
    print("STEP 2: Running OPTIMIZATION with devfactor=[2.0, 3.0, 4.0]")
    print("="*80)

    optimization_payload = {
        "ticker": ticker,
        "strategy": strategy,
        "start_date": start_date,
        "end_date": end_date,
        "interval": interval,
        "cash": cash,
        "optimization_params": {
            "period": [20],  # Keep period fixed
            "devfactor": [2.0, 3.0, 4.0]
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/optimize",
            json=optimization_payload,
            timeout=60
        )

        if response.status_code == 200:
            optimization_result = response.json()
            print(f"✓ Optimization completed successfully")
            print(f"\nOptimization Results:")
            print(f"  Total Combinations: {optimization_result['total_combinations']}")
            print(f"  Top {len(optimization_result['top_results'])} Results:")

            # Find the result with devfactor=2.0
            devfactor_2_result = None
            for idx, result in enumerate(optimization_result['top_results'], 1):
                params = result['parameters']
                devfactor_value = params.get('devfactor', 'N/A')
                print(f"\n  {idx}. devfactor={devfactor_value}")
                print(f"     Start Value:  ${result['start_value']:,.2f}")
                print(f"     End Value:    ${result['end_value']:,.2f}")
                print(f"     PnL:          ${result['pnl']:,.2f}")
                print(f"     Return:       {result['return_pct']:.2f}%")
                print(f"     Sharpe Ratio: {result['sharpe_ratio']}")

                if devfactor_value == test_devfactor:
                    devfactor_2_result = result

        else:
            print(f"✗ Optimization failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Optimization error: {str(e)}")
        return False

    # ============================================================================
    # STEP 3: Compare results for devfactor=2.0
    # ============================================================================
    print("\n" + "="*80)
    print("STEP 3: COMPARISON ANALYSIS")
    print("="*80)

    if devfactor_2_result is None:
        print("\n⚠️  WARNING: Could not find devfactor=2.0 in optimization results")
        print("This might indicate the optimization result is not sorted correctly")
        return False

    print(f"\nComparing results for devfactor=2.0:\n")

    # Create comparison table
    comparison = {
        'Start Value': {
            'Backtest': backtest_result['start_value'],
            'Optimization': devfactor_2_result['start_value']
        },
        'End Value': {
            'Backtest': backtest_result['end_value'],
            'Optimization': devfactor_2_result['end_value']
        },
        'PnL': {
            'Backtest': backtest_result['pnl'],
            'Optimization': devfactor_2_result['pnl']
        },
        'Return %': {
            'Backtest': backtest_result['return_pct'],
            'Optimization': devfactor_2_result['return_pct']
        },
        'Sharpe Ratio': {
            'Backtest': backtest_result['sharpe_ratio'],
            'Optimization': devfactor_2_result['sharpe_ratio']
        },
        'Max Drawdown': {
            'Backtest': backtest_result.get('max_drawdown'),
            'Optimization': 'N/A'  # Optimizer doesn't return this
        },
        'Total Trades': {
            'Backtest': backtest_result['total_trades'],
            'Optimization': 'N/A'  # Optimizer doesn't return this
        }
    }

    print(f"{'Metric':<20} {'Backtest':<20} {'Optimization':<20} {'Difference':<20}")
    print("-" * 80)

    issues_found = []

    for metric, values in comparison.items():
        backtest_val = values['Backtest']
        optimize_val = values['Optimization']

        if backtest_val == 'N/A' or optimize_val == 'N/A':
            diff_str = 'N/A'
        else:
            diff = optimize_val - backtest_val
            diff_pct = (diff / backtest_val * 100) if backtest_val != 0 else 0

            # Format difference
            if abs(diff) < 0.01:
                diff_str = '✓ Match'
            elif abs(diff_pct) < 1.0:
                diff_str = f'~{diff:+.2f} (~{diff_pct:+.1f}%)'
            else:
                diff_str = f'⚠️  {diff:+.2f} ({diff_pct:+.1f}%)'
                issues_found.append({
                    'metric': metric,
                    'backtest': backtest_val,
                    'optimization': optimize_val,
                    'difference': diff,
                    'difference_pct': diff_pct
                })

        print(f"{metric:<20} {str(backtest_val):<20} {str(optimize_val):<20} {diff_str:<20}")

    # ============================================================================
    # STEP 4: Analyze discrepancies
    # ============================================================================
    print("\n" + "="*80)
    print("STEP 4: DISCREPANCY ANALYSIS")
    print("="*80)

    if not issues_found:
        print("\n✓ PASS: Results match between backtest and optimization!")
        print("The logic is consistent.")
        return True
    else:
        print(f"\n⚠️  FAIL: Found {len(issues_found)} significant discrepancies:")

        for issue in issues_found:
            print(f"\n  {issue['metric']}:")
            print(f"    Backtest:     {issue['backtest']:.2f}")
            print(f"    Optimization: {issue['optimization']:.2f}")
            print(f"    Difference:   {issue['difference']:+.2f} ({issue['difference_pct']:+.1f}%)")

        print("\n" + "="*80)
        print("POTENTIAL CAUSES OF DISCREPANCIES:")
        print("="*80)

        print("\n1. POSITION SIZING:")
        print("   - Backtest: Uses PercentSizer(95%) - trades with 95% of available cash")
        print("   - Optimizer: No sizer configured - might use different default")
        print("   Impact: Different position sizes → different PnL")

        print("\n2. COMMISSION:")
        print("   - Backtest: Uses default commission (likely 0%)")
        print("   - Optimizer: Explicitly sets commission=0.001 (0.1%)")
        print("   Impact: Optimizer pays commission, backtest doesn't → lower PnL")

        print("\n3. PARAMETER PASSING:")
        print("   - Backtest: cerebro.addstrategy(strategy, args=params)")
        print("   - Optimizer: cerebro.addstrategy(strategy, args=params, **params)")
        print("   Impact: Parameters might be passed differently to strategy")

        print("\n4. ANALYZERS:")
        print("   - Backtest: Uses multiple analyzers (TradeAnalyzer, DrawDown, etc.)")
        print("   - Optimizer: Uses only SharpeRatio and Returns")
        print("   Impact: Different metrics calculated")

        print("\n" + "="*80)
        print("RECOMMENDED FIXES:")
        print("="*80)

        print("\nTo make optimization match backtest logic:")
        print("1. Add PercentSizer(95%) to optimizer.py")
        print("2. Make commission consistent (either both 0% or both 0.1%)")
        print("3. Use same parameter passing method")
        print("4. Add same analyzers to both")

        print("\n" + "="*80)

        return False


def test_commission_impact():
    """
    Test to isolate commission impact on results
    """
    print("\n" + "="*80)
    print("BONUS TEST: Commission Impact Analysis")
    print("="*80)
    print("Running two backtests to see commission impact:")
    print("1. With 0% commission (default)")
    print("2. Calculate what 0.1% commission would cost")
    print("="*80)

    # This is informational only - we'd need to modify the code to test this properly
    print("\nNote: This would require code modifications to test properly.")
    print("The backtest endpoint doesn't expose commission settings.")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("BACKTEST VS OPTIMIZATION DEBUGGING SUITE")
    print("="*80)
    print("This test will help identify why optimization results")
    print("don't match backtest results for the same parameters.")
    print("\nMake sure the API server is running on localhost:8086")
    print("="*80)

    input("\nPress Enter to start the comparison test...")

    success = test_backtest_vs_optimization()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    if success:
        print("✓ PASS: Backtest and optimization logic are consistent")
    else:
        print("✗ FAIL: Discrepancies found between backtest and optimization")
        print("\nReview the analysis above to understand the differences.")
        print("The most likely causes are:")
        print("  1. Position sizing differences (95% vs no sizer)")
        print("  2. Commission settings (0% vs 0.1%)")
        print("  3. Parameter passing method")

    print("="*80)

    # Try commission impact test
    test_commission_impact()
