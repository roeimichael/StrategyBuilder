"""Basic tests for market data domain."""
import sys
import os
import requests
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

API_BASE = "http://localhost:8000"


def test_fetch_market_data() -> Dict[str, Any]:
    """Test fetching market data."""
    request_data = {
        "ticker": "AAPL",
        "period": "1mo",
        "interval": "1d"
    }

    try:
        response = requests.post(f"{API_BASE}/market-data", json=request_data, timeout=30)

        if response.status_code == 200:
            data = response.json()
            assert 'success' in data, "Missing success field"
            assert 'data' in data, "Missing data field"
            print(f"  [PASS] Market data endpoint working")
            return {"passed": True, "name": "Fetch Market Data", "error": None}
        else:
            error = f"HTTP {response.status_code}: {response.text}"
            print(f"  [FAIL] Market data fetch failed: {error}")
            return {"passed": False, "name": "Fetch Market Data", "error": error}

    except Exception as e:
        print(f"  [FAIL] Market data fetch error: {str(e)}")
        return {"passed": False, "name": "Fetch Market Data", "error": str(e)}


def test_market_data_validation() -> Dict[str, Any]:
    """Test market data endpoint validation."""
    invalid_request = {
        "ticker": "!!!INVALID!!!",  # Invalid ticker
        "period": "invalid_period",
        "interval": "invalid_interval"
    }

    try:
        response = requests.post(f"{API_BASE}/market-data", json=invalid_request, timeout=10)

        # Should return 422 validation error
        if response.status_code == 422:
            print(f"  [PASS] Market data validation working")
            return {"passed": True, "name": "Market Data Validation", "error": None}
        else:
            error = f"Expected 422 validation error, got {response.status_code}"
            print(f"  [FAIL] {error}")
            return {"passed": False, "name": "Market Data Validation", "error": error}

    except Exception as e:
        print(f"  [FAIL] Validation test error: {str(e)}")
        return {"passed": False, "name": "Market Data Validation", "error": str(e)}


def run_tests() -> list:
    """Run all market data tests."""
    print("\n" + "=" * 80)
    print("MARKET DATA DOMAIN TESTS")
    print("=" * 80)

    results = []
    results.append(test_fetch_market_data())
    results.append(test_market_data_validation())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"\nMarket Data Tests: {passed}/{total} passed")
    print("=" * 80)

    return results


if __name__ == "__main__":
    run_tests()
