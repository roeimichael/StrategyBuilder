"""Basic tests for portfolio domain."""
import sys
import os
import requests
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

API_BASE = "http://localhost:8000"


def test_create_portfolio() -> Dict[str, Any]:
    """Test creating a portfolio."""
    request_data = {
        "name": "Test Portfolio",
        "description": "Portfolio for testing",
        "holdings": [
            {"ticker": "AAPL", "weight": 50},
            {"ticker": "MSFT", "weight": 50}
        ]
    }

    try:
        response = requests.post(f"{API_BASE}/portfolios", json=request_data, timeout=10)

        if response.status_code == 201:
            data = response.json()
            assert 'id' in data, "Missing portfolio ID"
            assert data['name'] == "Test Portfolio", "Name mismatch"
            print(f"  [PASS] Portfolio creation working (ID: {data['id']})")
            return {"passed": True, "name": "Create Portfolio", "error": None, "portfolio_id": data['id']}
        else:
            error = f"HTTP {response.status_code}: {response.text}"
            print(f"  [FAIL] Portfolio creation failed: {error}")
            return {"passed": False, "name": "Create Portfolio", "error": error}

    except Exception as e:
        print(f"  [FAIL] Portfolio creation error: {str(e)}")
        return {"passed": False, "name": "Create Portfolio", "error": str(e)}


def test_list_portfolios() -> Dict[str, Any]:
    """Test listing portfolios."""
    try:
        response = requests.get(f"{API_BASE}/portfolios", timeout=10)

        if response.status_code == 200:
            data = response.json()
            assert 'success' in data, "Missing success field"
            assert 'portfolios' in data, "Missing portfolios field"
            print(f"  [PASS] Portfolio list endpoint working ({data.get('count', 0)} portfolios)")
            return {"passed": True, "name": "List Portfolios", "error": None}
        else:
            error = f"HTTP {response.status_code}: {response.text}"
            print(f"  [FAIL] Portfolio list failed: {error}")
            return {"passed": False, "name": "List Portfolios", "error": error}

    except Exception as e:
        print(f"  [FAIL] Portfolio list error: {str(e)}")
        return {"passed": False, "name": "List Portfolios", "error": str(e)}


def run_tests() -> list:
    """Run all portfolio tests."""
    print("\n" + "=" * 80)
    print("PORTFOLIO DOMAIN TESTS")
    print("=" * 80)

    results = []
    results.append(test_list_portfolios())
    results.append(test_create_portfolio())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"\nPortfolio Tests: {passed}/{total} passed")
    print("=" * 80)

    return results


if __name__ == "__main__":
    run_tests()
