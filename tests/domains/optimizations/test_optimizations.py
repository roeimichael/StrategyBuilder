"""Basic tests for optimization domain."""
import sys
import os
import requests
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

API_BASE = "http://localhost:8000"


def test_optimize_endpoint() -> Dict[str, Any]:
    """Test optimize endpoint with valid request."""
    request_data = {
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

    try:
        response = requests.post(f"{API_BASE}/optimize", json=request_data, timeout=120)

        if response.status_code == 200:
            data = response.json()
            assert data['success'] == True, "Expected success=True"
            assert 'top_results' in data, "Missing top_results field"
            assert len(data['top_results']) > 0, "Expected at least one result"
            print(f"  [PASS] Optimization endpoint working")
            print(f"         Tested {data.get('total_combinations', 0)} combinations")
            return {"passed": True, "name": "Optimization Endpoint", "error": None}
        else:
            error = f"HTTP {response.status_code}: {response.text}"
            print(f"  [FAIL] Optimization endpoint failed: {error}")
            return {"passed": False, "name": "Optimization Endpoint", "error": error}

    except Exception as e:
        print(f"  [FAIL] Optimization endpoint error: {str(e)}")
        return {"passed": False, "name": "Optimization Endpoint", "error": str(e)}


def test_optimize_validation() -> Dict[str, Any]:
    """Test optimize endpoint validation."""
    invalid_request = {
        "ticker": "AAPL",
        "strategy": "bollinger_bands_strategy",
        "start_date": "2024-12-31",  # Start after end
        "end_date": "2024-01-01",
        "param_ranges": {}  # Empty param_ranges
    }

    try:
        response = requests.post(f"{API_BASE}/optimize", json=invalid_request, timeout=10)

        # Should return 422 validation error or 400 bad request
        if response.status_code in [400, 422]:
            print(f"  [PASS] Validation working (rejected invalid input)")
            return {"passed": True, "name": "Optimization Validation", "error": None}
        else:
            error = f"Expected 400/422 error, got {response.status_code}"
            print(f"  [FAIL] {error}")
            return {"passed": False, "name": "Optimization Validation", "error": error}

    except Exception as e:
        print(f"  [FAIL] Validation test error: {str(e)}")
        return {"passed": False, "name": "Optimization Validation", "error": str(e)}


def run_tests() -> list:
    """Run all optimization tests."""
    print("\n" + "=" * 80)
    print("OPTIMIZATION DOMAIN TESTS")
    print("=" * 80)

    results = []
    results.append(test_optimize_endpoint())
    results.append(test_optimize_validation())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"\nOptimization Tests: {passed}/{total} passed")
    print("=" * 80)

    return results


if __name__ == "__main__":
    run_tests()
