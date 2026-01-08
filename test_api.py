import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8086"

def test_market_data_btc():
    response = requests.post(
        f"{BASE_URL}/market-data",
        json={
            "ticker": "BTC-USD",
            "period": "6mo",
            "interval": "1d"
        }
    )
    return {
        "test_name": "Market Data - BTC 6 months",
        "endpoint": "/market-data",
        "body": {
            "ticker": "BTC-USD",
            "period": "6mo",
            "interval": "1d"
        },
        "status_code": response.status_code,
        "response": response.json() if response.status_code == 200 else response.text
    }

def test_market_data_eth():
    response = requests.post(
        f"{BASE_URL}/market-data",
        json={
            "ticker": "ETH-USD",
            "period": "1y",
            "interval": "1d"
        }
    )
    return {
        "test_name": "Market Data - ETH 1 year",
        "endpoint": "/market-data",
        "body": {
            "ticker": "ETH-USD",
            "period": "1y",
            "interval": "1d"
        },
        "status_code": response.status_code,
        "response": response.json() if response.status_code == 200 else response.text
    }

def test_backtest_williams_r():
    response = requests.post(
        f"{BASE_URL}/backtest",
        json={
            "ticker": "BTC-USD",
            "strategy": "williams_r_strategy",
            "start_date": "2024-01-01",
            "end_date": "2025-12-31",
            "interval": "1d",
            "cash": 10000.0,
            "parameters": {
                "period": 14,
                "lower_bound": -80,
                "upper_bound": -20
            }
        }
    )
    return {
        "test_name": "Backtest - Williams R Strategy",
        "endpoint": "/backtest",
        "body": {
            "ticker": "BTC-USD",
            "strategy": "williams_r_strategy",
            "start_date": "2024-01-01",
            "end_date": "2025-12-31",
            "interval": "1d",
            "cash": 10000.0,
            "parameters": {
                "period": 14,
                "lower_bound": -80,
                "upper_bound": -20
            }
        },
        "status_code": response.status_code,
        "response": response.json() if response.status_code == 200 else response.text
    }

def test_backtest_rsi_stochastic():
    response = requests.post(
        f"{BASE_URL}/backtest",
        json={
            "ticker": "ETH-USD",
            "strategy": "rsi_stochastic_strategy",
            "start_date": "2025-06-01",
            "end_date": "2025-12-31",
            "interval": "1d",
            "cash": 5000.0,
            "parameters": {}
        }
    )
    return {
        "test_name": "Backtest - RSI Stochastic Strategy",
        "endpoint": "/backtest",
        "body": {
            "ticker": "ETH-USD",
            "strategy": "rsi_stochastic_strategy",
            "start_date": "2025-06-01",
            "end_date": "2025-12-31",
            "interval": "1d",
            "cash": 5000.0,
            "parameters": {}
        },
        "status_code": response.status_code,
        "response": response.json() if response.status_code == 200 else response.text
    }

def test_backtest_bollinger_bands():
    response = requests.post(
        f"{BASE_URL}/backtest",
        json={
            "ticker": "BTC-USD",
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-06-01",
            "end_date": "2024-12-31",
            "interval": "1d",
            "cash": 20000.0,
            "parameters": {}
        }
    )
    return {
        "test_name": "Backtest - Bollinger Bands Strategy",
        "endpoint": "/backtest",
        "body": {
            "ticker": "BTC-USD",
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-06-01",
            "end_date": "2024-12-31",
            "interval": "1d",
            "cash": 20000.0,
            "parameters": {}
        },
        "status_code": response.status_code,
        "response": response.json() if response.status_code == 200 else response.text
    }

def run_all_tests():
    print("Starting API tests...")
    print(f"Target: {BASE_URL}")
    print("-" * 80)

    tests = [
        test_market_data_btc,
        test_market_data_eth,
        test_backtest_williams_r,
        test_backtest_rsi_stochastic,
        test_backtest_bollinger_bands
    ]

    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "tests": []
    }

    for i, test_func in enumerate(tests, 1):
        print(f"\nRunning test {i}/{len(tests)}: {test_func.__name__}...")
        try:
            result = test_func()
            results["tests"].append(result)
            print(f"Status: {result['status_code']}")
        except Exception as e:
            error_result = {
                "test_name": test_func.__name__,
                "error": str(e)
            }
            results["tests"].append(error_result)
            print(f"Error: {e}")

    output_file = "test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'-' * 80}")
    print(f"Tests complete. Results saved to {output_file}")
    print(f"Total tests: {len(tests)}")
    print(f"Successful: {sum(1 for t in results['tests'] if t.get('status_code') == 200)}")

if __name__ == "__main__":
    run_all_tests()
