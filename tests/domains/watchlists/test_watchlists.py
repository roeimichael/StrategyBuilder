"""Basic tests for watchlist domain."""
import sys
import os
import requests
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

API_BASE = "http://localhost:8000"


def test_create_watchlist() -> Dict[str, Any]:
    """Test creating a watchlist."""
    request_data = {
        "name": "Test Watchlist",
        "description": "Watchlist for testing",
        "tickers": ["AAPL", "MSFT", "GOOGL"]
    }

    try:
        response = requests.post(f"{API_BASE}/watchlists", json=request_data, timeout=10)

        if response.status_code == 201:
            data = response.json()
            assert 'id' in data, "Missing watchlist ID"
            assert data['name'] == "Test Watchlist", "Name mismatch"
            print(f"  [PASS] Watchlist creation working (ID: {data['id']})")
            return {"passed": True, "name": "Create Watchlist", "error": None, "watchlist_id": data['id']}
        else:
            error = f"HTTP {response.status_code}: {response.text}"
            print(f"  [FAIL] Watchlist creation failed: {error}")
            return {"passed": False, "name": "Create Watchlist", "error": error}

    except Exception as e:
        print(f"  [FAIL] Watchlist creation error: {str(e)}")
        return {"passed": False, "name": "Create Watchlist", "error": str(e)}


def test_list_watchlists() -> Dict[str, Any]:
    """Test listing watchlists."""
    try:
        response = requests.get(f"{API_BASE}/watchlists", timeout=10)

        if response.status_code == 200:
            data = response.json()
            assert 'success' in data, "Missing success field"
            assert 'watchlists' in data, "Missing watchlists field"
            print(f"  [PASS] Watchlist list endpoint working ({data.get('count', 0)} watchlists)")
            return {"passed": True, "name": "List Watchlists", "error": None}
        else:
            error = f"HTTP {response.status_code}: {response.text}"
            print(f"  [FAIL] Watchlist list failed: {error}")
            return {"passed": False, "name": "List Watchlists", "error": error}

    except Exception as e:
        print(f"  [FAIL] Watchlist list error: {str(e)}")
        return {"passed": False, "name": "List Watchlists", "error": str(e)}


def run_tests() -> list:
    """Run all watchlist tests."""
    print("\n" + "=" * 80)
    print("WATCHLIST DOMAIN TESTS")
    print("=" * 80)

    results = []
    results.append(test_list_watchlists())
    results.append(test_create_watchlist())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"\nWatchlist Tests: {passed}/{total} passed")
    print("=" * 80)

    return results


if __name__ == "__main__":
    run_tests()
