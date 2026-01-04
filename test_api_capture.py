import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import time


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results: List[Dict[str, Any]] = []

    def capture_request(self, name: str, method: str, endpoint: str,
                       payload: Dict = None, params: Dict = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, json=payload)
            else:
                raise ValueError(f"Unsupported method: {method}")

            elapsed_time = time.time() - start_time

            result = {
                "test_name": name,
                "timestamp": datetime.now().isoformat(),
                "request": {
                    "method": method,
                    "endpoint": endpoint,
                    "url": url,
                    "payload": payload,
                    "params": params
                },
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                },
                "performance": {
                    "elapsed_seconds": round(elapsed_time, 3)
                },
                "success": response.status_code in [200, 201]
            }

            self.test_results.append(result)
            return result

        except Exception as e:
            error_result = {
                "test_name": name,
                "timestamp": datetime.now().isoformat(),
                "request": {
                    "method": method,
                    "endpoint": endpoint,
                    "url": url,
                    "payload": payload,
                    "params": params
                },
                "error": str(e),
                "success": False
            }
            self.test_results.append(error_result)
            return error_result

    def test_root(self):
        print("\n1. Testing Root Endpoint...")
        return self.capture_request(
            name="Get API Root Information",
            method="GET",
            endpoint="/"
        )

    def test_health(self):
        print("2. Testing Health Check...")
        return self.capture_request(
            name="Health Check",
            method="GET",
            endpoint="/health"
        )

    def test_list_strategies(self):
        print("3. Testing List All Strategies...")
        return self.capture_request(
            name="List All Available Strategies",
            method="GET",
            endpoint="/strategies"
        )

    def test_get_strategy_info(self, strategy_name: str = "bollinger_bands_strategy"):
        print(f"4. Testing Get Strategy Info ({strategy_name})...")
        return self.capture_request(
            name=f"Get Strategy Information - {strategy_name}",
            method="GET",
            endpoint=f"/strategies/{strategy_name}"
        )

    def test_get_default_parameters(self):
        print("5. Testing Get Default Parameters...")
        return self.capture_request(
            name="Get Default Strategy Parameters",
            method="GET",
            endpoint="/parameters/default"
        )

    def test_backtest_simple(self):
        print("6. Testing Simple Backtest (Bollinger Bands)...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        payload = {
            "ticker": "AAPL",
            "strategy": "bollinger_bands_strategy",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "interval": "1d",
            "cash": 10000.0
        }

        return self.capture_request(
            name="Run Backtest - Bollinger Bands Strategy",
            method="POST",
            endpoint="/backtest",
            payload=payload
        )

    def test_backtest_with_custom_params(self):
        print("7. Testing Backtest with Custom Parameters...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)

        payload = {
            "ticker": "MSFT",
            "strategy": "rsi_stochastic_strategy",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "interval": "1d",
            "cash": 25000.0,
            "parameters": {
                "position_size_pct": 80,
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70
            }
        }

        return self.capture_request(
            name="Run Backtest - RSI with Custom Parameters",
            method="POST",
            endpoint="/backtest",
            payload=payload
        )

    def test_backtest_different_interval(self):
        print("8. Testing Backtest with Different Interval (1h)...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        payload = {
            "ticker": "TSLA",
            "strategy": "williams_r_strategy",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "interval": "1h",
            "cash": 15000.0
        }

        return self.capture_request(
            name="Run Backtest - Williams R with 1h Interval",
            method="POST",
            endpoint="/backtest",
            payload=payload
        )

    def test_market_data(self):
        print("9. Testing Market Data Retrieval...")
        payload = {
            "ticker": "AAPL",
            "period": "1mo",
            "interval": "1d"
        }

        return self.capture_request(
            name="Get Market Data - AAPL 1 Month Daily",
            method="POST",
            endpoint="/market-data",
            payload=payload
        )

    def test_market_data_intraday(self):
        print("10. Testing Intraday Market Data...")
        payload = {
            "ticker": "GOOGL",
            "period": "5d",
            "interval": "1h"
        }

        return self.capture_request(
            name="Get Market Data - GOOGL 5 Days Hourly",
            method="POST",
            endpoint="/market-data",
            payload=payload
        )

    def run_all_tests(self):
        print("=" * 80)
        print("STRATEGYBUILDER API TEST SUITE")
        print("=" * 80)

        # Run all tests
        self.test_root()
        self.test_health()
        self.test_list_strategies()
        self.test_get_strategy_info("bollinger_bands_strategy")
        self.test_get_strategy_info("adx_strategy")
        self.test_get_default_parameters()
        self.test_backtest_simple()
        self.test_backtest_with_custom_params()
        self.test_backtest_different_interval()
        self.test_market_data()
        self.test_market_data_intraday()

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        successful = sum(1 for r in self.test_results if r.get('success', False))
        total = len(self.test_results)
        print(f"Total Tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")

        # Save results
        self.save_results()

    def save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_results_{timestamp}.json"

        output = {
            "test_run_info": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_tests": len(self.test_results),
                "successful_tests": sum(1 for r in self.test_results if r.get('success', False))
            },
            "tests": self.test_results
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✓ Results saved to: {filename}")

        # Also create a simplified examples file
        self.create_examples_file()

    def create_examples_file(self):
        examples = {
            "api_base_url": self.base_url,
            "endpoints": {}
        }

        for result in self.test_results:
            if result.get('success'):
                endpoint = result['request']['endpoint']
                if endpoint not in examples["endpoints"]:
                    examples["endpoints"][endpoint] = []

                example = {
                    "description": result['test_name'],
                    "method": result['request']['method'],
                    "request": {
                        "payload": result['request'].get('payload'),
                        "params": result['request'].get('params')
                    },
                    "response_sample": result['response']['body'],
                    "typical_response_time_seconds": result['performance']['elapsed_seconds']
                }
                examples["endpoints"][endpoint].append(example)

        with open("api_examples.json", 'w') as f:
            json.dump(examples, f, indent=2)

        print("✓ Examples saved to: api_examples.json")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("IMPORTANT: Make sure the API server is running on http://localhost:8000")
    print("Run: python run_api.py")
    print("=" * 80)

    input("\nPress Enter to start testing (or Ctrl+C to cancel)...")

    tester = APITester()
    tester.run_all_tests()

    print("\n" + "=" * 80)
    print("Testing complete! Check the generated JSON files for details.")
    print("=" * 80)
