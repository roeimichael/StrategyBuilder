"""Basic tests for backtest domain."""
import sys
import os
import requests
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

API_BASE = "http://localhost:8000"


def test_backtest_endpoint() -> Dict[str, Any]:
    """Test backtest endpoint with valid request."""
    request_data = {
        "ticker": "AAPL",
        "strategy": "bollinger_bands_strategy",
        "start_date": "2024-07-01",
        "end_date": "2024-12-31",
        "interval": "1d",
        "cash": 10000,
        "parameters": {"period": 20, "devfactor": 2.0}
    }

    try:
        response = requests.post(f"{API_BASE}/backtest", json=request_data, timeout=60)

        if response.status_code == 200:
            data = response.json()
            assert data['success'] == True, "Expected success=True"
            assert 'pnl' in data, "Missing PnL field"
            assert 'return_pct' in data, "Missing return_pct field"
            assert 'total_trades' in data, "Missing total_trades field"
            print(f"  [PASS] Backtest endpoint working")
            print(f"         PnL: {data['pnl']:.2f}, Return: {data['return_pct']:.2f}%")
            return {"passed": True, "name": "Backtest Endpoint", "error": None}
        else:
            error = f"HTTP {response.status_code}: {response.text}"
            print(f"  [FAIL] Backtest endpoint failed: {error}")
            return {"passed": False, "name": "Backtest Endpoint", "error": error}

    except Exception as e:
        print(f"  [FAIL] Backtest endpoint error: {str(e)}")
        return {"passed": False, "name": "Backtest Endpoint", "error": str(e)}


def test_backtest_validation() -> Dict[str, Any]:
    """Test backtest endpoint validation."""
    invalid_request = {
        "ticker": "INVALID!!!",  # Invalid ticker format
        "strategy": "bollinger_bands_strategy",
        "start_date": "invalid-date",  # Invalid date format
        "cash": -1000  # Negative cash
    }

    try:
        response = requests.post(f"{API_BASE}/backtest", json=invalid_request, timeout=10)

        # Should return 422 validation error
        if response.status_code == 422:
            print(f"  [PASS] Validation working (rejected invalid input)")
            return {"passed": True, "name": "Backtest Validation", "error": None}
        else:
            error = f"Expected 422 validation error, got {response.status_code}"
            print(f"  [FAIL] {error}")
            return {"passed": False, "name": "Backtest Validation", "error": error}

    except Exception as e:
        print(f"  [FAIL] Validation test error: {str(e)}")
        return {"passed": False, "name": "Backtest Validation", "error": str(e)}


def run_tests() -> list:
    """Run all backtest tests."""
    print("\n" + "=" * 80)
    print("BACKTEST DOMAIN TESTS")
    print("=" * 80)

    results = []
    results.append(test_backtest_endpoint())
    results.append(test_backtest_validation())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"\nBacktest Tests: {passed}/{total} passed")
    print("=" * 80)

    return results


if __name__ == "__main__":
    run_tests()
