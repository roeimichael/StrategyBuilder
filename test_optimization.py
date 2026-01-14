import requests
import json

BASE_URL = "http://localhost:8086"

def test_optimize_bollinger():
    print("Testing Bollinger Bands optimization...")
    response = requests.post(
        f"{BASE_URL}/optimize",
        json={
            "ticker": "BTC-USD",
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
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
        print(f"Success: {result['success']}")
        print(f"Total Combinations: {result['total_combinations']}")
        print(f"\nTop {len(result['top_results'])} Results:")
        for i, res in enumerate(result['top_results'], 1):
            print(f"\n{i}. Parameters: {res['parameters']}")
            print(f"   PnL: ${res['pnl']:.2f}")
            print(f"   Return: {res['return_pct']:.2f}%")
            print(f"   Sharpe: {res['sharpe_ratio']}")
    else:
        print(f"Error: {response.text}")

def test_optimize_williams():
    print("\n" + "="*60)
    print("Testing Williams R optimization...")
    response = requests.post(
        f"{BASE_URL}/optimize",
        json={
            "ticker": "ETH-USD",
            "strategy": "williams_r_strategy",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "interval": "1d",
            "cash": 10000.0,
            "optimization_params": {
                "period": [10, 14, 20],
                "oversold": [-90, -80, -70],
                "overbought": [-30, -20, -10]
            }
        }
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Total Combinations: {result['total_combinations']}")
        print(f"\nTop {len(result['top_results'])} Results:")
        for i, res in enumerate(result['top_results'], 1):
            print(f"\n{i}. Parameters: {res['parameters']}")
            print(f"   PnL: ${res['pnl']:.2f}")
            print(f"   Return: {res['return_pct']:.2f}%")
            print(f"   Sharpe: {res['sharpe_ratio']}")
    else:
        print(f"Error: {response.text}")

def test_get_strategy_with_params():
    print("\n" + "="*60)
    print("Testing strategy info endpoint with optimization params...")
    response = requests.get(f"{BASE_URL}/strategies/bollinger_bands_strategy")

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        strategy = result.get('strategy', {})
        print(f"Strategy: {strategy.get('class_name')}")
        print(f"\nOptimizable Parameters:")
        for param in strategy.get('optimizable_params', []):
            print(f"\n  {param['name']}:")
            print(f"    Type: {param['type']}")
            print(f"    Default: {param['default']}")
            print(f"    Range: [{param['min']} - {param['max']}]")
            print(f"    Step: {param['step']}")
            print(f"    Description: {param['description']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Make sure the API server is running on localhost:8086")
    print("="*60)

    try:
        test_optimize_bollinger()
        test_optimize_williams()
        test_get_strategy_with_params()
        print("\n" + "="*60)
        print("All tests completed!")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API server.")
        print("Please start the server with: python -m src.api.main")
