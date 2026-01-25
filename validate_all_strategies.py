"""Comprehensive validation script for all strategies and configurations."""
import sys
import requests
import json
from typing import Dict, List, Any

API_BASE = "http://localhost:8000"

def test_all_strategies() -> Dict[str, Any]:
    """Test all 12 strategies with multiple parameter configurations."""
    strategies_response = requests.get(f"{API_BASE}/strategies")
    if strategies_response.status_code != 200:
        return {"error": "Failed to fetch strategies list"}

    strategies = strategies_response.json()["strategies"]
    results = {
        "total_strategies": len(strategies),
        "tested": 0,
        "passed": 0,
        "failed": 0,
        "failures": []
    }

    for strategy in strategies:
        strategy_name = strategy["module"]

        detail_response = requests.get(f"{API_BASE}/strategies/{strategy_name}")
        if detail_response.status_code != 200:
            results["failures"].append({
                "strategy": strategy_name,
                "error": "Failed to fetch strategy details"
            })
            results["failed"] += 1
            continue

        strategy_info = detail_response.json()["strategy"]
        default_params = strategy_info.get("parameters", {})

        test_params = [default_params]

        optimizable = strategy_info.get("optimizable_params", [])
        if optimizable and len(optimizable) > 0:
            alt_params = default_params.copy()
            for param_info in optimizable[:2]:
                param_name = param_info["name"]
                if param_info["type"] == "int":
                    alt_params[param_name] = int((param_info["min"] + param_info["max"]) / 2)
                else:
                    alt_params[param_name] = (param_info["min"] + param_info["max"]) / 2
            test_params.append(alt_params)

        for params in test_params:
            backtest_request = {
                "ticker": "AAPL",
                "strategy": strategy_name,
                "start_date": "2024-07-01",
                "end_date": "2024-12-31",
                "interval": "1d",
                "cash": 10000,
                "parameters": params
            }

            response = requests.post(f"{API_BASE}/backtest", json=backtest_request)
            results["tested"] += 1

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["failures"].append({
                        "strategy": strategy_name,
                        "params": params,
                        "error": "Backtest failed"
                    })
            else:
                results["failed"] += 1
                results["failures"].append({
                    "strategy": strategy_name,
                    "params": params,
                    "error": response.text
                })

    return results

def validate_config_dynamic_behavior() -> Dict[str, Any]:
    """Validate that configs don't override user input."""
    results = {"tests": [], "passed": 0, "failed": 0}

    test_cases = [
        {
            "name": "Custom cash value",
            "request": {
                "ticker": "AAPL",
                "strategy": "bollinger_bands_strategy",
                "start_date": "2024-12-01",
                "end_date": "2024-12-31",
                "interval": "1d",
                "cash": 50000,
                "parameters": {"period": 20, "devfactor": 2.0}
            },
            "expected_cash": 50000
        },
        {
            "name": "Custom interval",
            "request": {
                "ticker": "AAPL",
                "strategy": "bollinger_bands_strategy",
                "start_date": "2024-12-01",
                "end_date": "2024-12-31",
                "interval": "1d",
                "cash": 10000,
                "parameters": {"period": 20, "devfactor": 2.0}
            },
            "expected_interval": "1d"
        }
    ]

    for test_case in test_cases:
        response = requests.post(f"{API_BASE}/backtest", json=test_case["request"])
        if response.status_code == 200:
            data = response.json()
            if "expected_cash" in test_case:
                if abs(data.get("start_value", 0) - test_case["expected_cash"]) < 0.01:
                    results["passed"] += 1
                    results["tests"].append({"name": test_case["name"], "status": "PASS"})
                else:
                    results["failed"] += 1
                    results["tests"].append({
                        "name": test_case["name"],
                        "status": "FAIL",
                        "expected": test_case["expected_cash"],
                        "actual": data.get("start_value")
                    })
            elif "expected_interval" in test_case:
                if data.get("interval") == test_case["expected_interval"]:
                    results["passed"] += 1
                    results["tests"].append({"name": test_case["name"], "status": "PASS"})
                else:
                    results["failed"] += 1
                    results["tests"].append({
                        "name": test_case["name"],
                        "status": "FAIL",
                        "expected": test_case["expected_interval"],
                        "actual": data.get("interval")
                    })
        else:
            results["failed"] += 1
            results["tests"].append({
                "name": test_case["name"],
                "status": "FAIL",
                "error": response.text
            })

    return results

if __name__ == "__main__":
    print("Starting comprehensive validation...")
    print("\n" + "="*80)
    print("TESTING ALL STRATEGIES WITH MULTIPLE CONFIGURATIONS")
    print("="*80)

    strategy_results = test_all_strategies()
    print(f"\nTotal Strategies: {strategy_results['total_strategies']}")
    print(f"Total Tests: {strategy_results['tested']}")
    print(f"Passed: {strategy_results['passed']}")
    print(f"Failed: {strategy_results['failed']}")

    if strategy_results['failures']:
        print("\nFailures:")
        for failure in strategy_results['failures'][:5]:
            print(f"  - {failure['strategy']}: {failure.get('error', 'Unknown error')}")

    print("\n" + "="*80)
    print("VALIDATING CONFIG DYNAMIC BEHAVIOR")
    print("="*80)

    config_results = validate_config_dynamic_behavior()
    print(f"\nPassed: {config_results['passed']}")
    print(f"Failed: {config_results['failed']}")

    for test in config_results['tests']:
        status_symbol = "PASS" if test['status'] == "PASS" else "FAIL"
        print(f"  [{status_symbol}] {test['name']}")

    print("\n" + "="*80)

    if strategy_results['failed'] == 0 and config_results['failed'] == 0:
        print("ALL VALIDATIONS PASSED")
        sys.exit(0)
    else:
        print("SOME VALIDATIONS FAILED")
        sys.exit(1)
