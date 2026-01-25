"""Comprehensive endpoint validation including optimization vs backtest consistency."""
import sys
import requests
import json
from typing import Dict, List, Any

API_BASE = "http://localhost:8000"

def test_optimize_endpoint() -> Dict[str, Any]:
    """Test the optimize endpoint."""
    print("\n" + "="*80)
    print("TESTING OPTIMIZE ENDPOINT")
    print("="*80)

    test_request = {
        "ticker": "AAPL",
        "strategy": "bollinger_bands_strategy",
        "start_date": "2024-07-01",
        "end_date": "2024-12-31",
        "interval": "1d",
        "cash": 10000,
        "param_ranges": {
            "period": [15, 20, 25],
            "devfactor": [1.5, 2.0, 2.5]
        }
    }

    response = requests.post(f"{API_BASE}/optimize", json=test_request)

    if response.status_code == 200:
        data = response.json()
        print(f"  [PASS] Optimize endpoint working")
        print(f"  Total combinations tested: {data['total_combinations']}")
        print(f"  Top 3 results:")
        for i, result in enumerate(data['top_results'][:3], 1):
            print(f"    {i}. {result['parameters']} -> {result['return_pct']:.4f}% return")
        return {"status": "PASS", "data": data}
    else:
        print(f"  [FAIL] Optimize endpoint failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return {"status": "FAIL", "error": response.text}

def test_market_scan_endpoint() -> Dict[str, Any]:
    """Test the market-scan endpoint."""
    print("\n" + "="*80)
    print("TESTING MARKET-SCAN ENDPOINT")
    print("="*80)

    test_request = {
        "tickers": ["AAPL", "MSFT", "GOOGL"],
        "strategy": "bollinger_bands_strategy",
        "start_date": "2024-07-01",
        "end_date": "2024-12-31",
        "interval": "1d",
        "cash": 10000,
        "parameters": {"period": 20, "devfactor": 2.0}
    }

    response = requests.post(f"{API_BASE}/market-scan", json=test_request)

    if response.status_code == 200:
        data = response.json()
        print(f"  [PASS] Market-scan endpoint working")
        print(f"  Tickers scanned: {data['total_tickers']}")
        print(f"  Successful scans: {data['successful_scans']}")
        print(f"  Failed scans: {data['failed_scans']}")
        print(f"  Top performers:")
        for result in data['top_performers'][:3]:
            print(f"    {result['ticker']}: {result['return_pct']:.2f}% ({result['total_trades']} trades)")
        return {"status": "PASS", "data": data}
    else:
        print(f"  [FAIL] Market-scan endpoint failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return {"status": "FAIL", "error": response.text}

def test_optimization_vs_backtest_consistency() -> Dict[str, Any]:
    """
    Critical test: Validate that optimization results match individual backtests.

    This tests that the optimization logic doesn't introduce any changes to the
    backtest calculations. We run an optimization with 2 parameter sets, then
    run 2 individual backtests with those same parameters, and verify the results
    are identical.
    """
    print("\n" + "="*80)
    print("TESTING OPTIMIZATION VS BACKTEST CONSISTENCY")
    print("="*80)
    print("This validates that optimization doesn't alter backtest logic")

    results = {"tests": [], "passed": 0, "failed": 0}

    # Step 1: Run optimization with 2 parameter combinations
    optimize_request = {
        "ticker": "AAPL",
        "strategy": "bollinger_bands_strategy",
        "start_date": "2024-07-01",
        "end_date": "2024-12-31",
        "interval": "1d",
        "cash": 10000,
        "param_ranges": {
            "period": [20, 25],
            "devfactor": [2.0]
        }
    }

    print("\n  Running optimization with 2 parameter combinations...")
    opt_response = requests.post(f"{API_BASE}/optimize", json=optimize_request)

    if opt_response.status_code != 200:
        results["failed"] += 1
        results["tests"].append({
            "name": "Optimization request",
            "status": "FAIL",
            "error": opt_response.text
        })
        return results

    opt_data = opt_response.json()
    print(f"  Optimization returned {opt_data['total_combinations']} results")

    # Step 2: For each optimization result, run a separate backtest with same params
    for i, opt_result in enumerate(opt_data['top_results'], 1):
        params = opt_result['parameters']
        opt_pnl = opt_result['pnl']
        opt_return = opt_result['return_pct']
        opt_trades = opt_result.get('total_trades', 0)

        print(f"\n  Test {i}: Params {params}")
        print(f"    Optimization result: PnL={opt_pnl:.6f}, Return={opt_return:.6f}%")

        # Run individual backtest with same parameters
        backtest_request = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-07-01",
            "end_date": "2024-12-31",
            "interval": "1d",
            "cash": 10000,
            "parameters": params
        }

        bt_response = requests.post(f"{API_BASE}/backtest", json=backtest_request)

        if bt_response.status_code != 200:
            results["failed"] += 1
            results["tests"].append({
                "name": f"Backtest with params {params}",
                "status": "FAIL",
                "error": bt_response.text
            })
            continue

        bt_data = bt_response.json()
        bt_pnl = bt_data['pnl']
        bt_return = bt_data['return_pct']
        bt_trades = bt_data['total_trades']

        print(f"    Backtest result:     PnL={bt_pnl:.6f}, Return={bt_return:.6f}%")

        # Compare results - they should be identical
        pnl_match = abs(opt_pnl - bt_pnl) < 0.01
        return_match = abs(opt_return - bt_return) < 0.01

        if pnl_match and return_match:
            print(f"    [PASS] Results match perfectly!")
            results["passed"] += 1
            results["tests"].append({
                "name": f"Consistency check {params}",
                "status": "PASS",
                "opt_pnl": opt_pnl,
                "bt_pnl": bt_pnl,
                "opt_return": opt_return,
                "bt_return": bt_return
            })
        else:
            print(f"    [FAIL] Results DO NOT match!")
            print(f"      PnL difference: {abs(opt_pnl - bt_pnl):.6f}")
            print(f"      Return difference: {abs(opt_return - bt_return):.6f}%")
            results["failed"] += 1
            results["tests"].append({
                "name": f"Consistency check {params}",
                "status": "FAIL",
                "opt_pnl": opt_pnl,
                "bt_pnl": bt_pnl,
                "opt_return": opt_return,
                "bt_return": bt_return,
                "pnl_diff": abs(opt_pnl - bt_pnl),
                "return_diff": abs(opt_return - bt_return)
            })

    return results

if __name__ == "__main__":
    print("\nStarting comprehensive endpoint validation...")

    all_passed = True

    # Test 1: Optimize endpoint
    opt_result = test_optimize_endpoint()
    if opt_result["status"] != "PASS":
        all_passed = False

    # Test 2: Market-scan endpoint
    scan_result = test_market_scan_endpoint()
    if scan_result["status"] != "PASS":
        all_passed = False

    # Test 3: Critical consistency test
    consistency_result = test_optimization_vs_backtest_consistency()
    if consistency_result["failed"] > 0:
        all_passed = False

    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Optimize endpoint: {opt_result['status']}")
    print(f"Market-scan endpoint: {scan_result['status']}")
    print(f"Consistency tests: {consistency_result['passed']} passed, {consistency_result['failed']} failed")

    if all_passed and consistency_result['failed'] == 0:
        print("\n[PASS] ALL ENDPOINT VALIDATIONS PASSED")
        print("Optimization and backtest logic are consistent!")
        sys.exit(0)
    else:
        print("\n[FAIL] SOME VALIDATIONS FAILED")
        sys.exit(1)
