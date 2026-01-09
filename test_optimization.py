import requests
import json

BASE_URL = "http://localhost:8086"

def test_optimize_bollinger():
    response = requests.post(
        f"{BASE_URL}/optimize",
        json={
            "ticker": "BTC-USD",
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-06-01",
            "end_date": "2024-12-31",
            "interval": "1d",
            "cash": 10000.0,
            "optimization_params": {
                "period": [15, 20, 25],
                "devfactor": [1.5, 2.0, 2.5]
            }
        }
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")

def test_optimize_williams():
    response = requests.post(
        f"{BASE_URL}/optimize",
        json={
            "ticker": "ETH-USD",
            "strategy": "williams_r_strategy",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "interval": "1d",
            "cash": 5000.0,
            "optimization_params": {
                "period": [10, 14, 20],
                "lower_bound": [-90, -80, -70],
                "upper_bound": [-30, -20, -10]
            }
        }
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("=" * 80)
    print("Test 1: Bollinger Bands Optimization (9 combinations)")
    print("=" * 80)
    test_optimize_bollinger()
    print("\n" + "=" * 80)
    print("Test 2: Williams R Optimization (27 combinations)")
    print("=" * 80)
    test_optimize_williams()
