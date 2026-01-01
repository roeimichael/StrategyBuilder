import requests
import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
        self.session = requests.Session()

    def log_result(self, endpoint: str, method: str, status_code: int, success: bool, response_time: float, error: str = None) -> None:
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        self.results.append(result)
        status = "✓" if success else "✗"
        print(f"{status} {method} {endpoint} - {status_code} ({result['response_time_ms']}ms)")
        if error:
            print(f"  Error: {error}")

    def test_root(self) -> None:
        endpoint = "/"
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            response_time = time.time() - start
            data = response.json()
            success = response.status_code == 200 and "name" in data and "version" in data and "endpoints" in data
            self.log_result(endpoint, "GET", response.status_code, success, response_time)
            if success:
                print(f"  API: {data['name']} v{data['version']}")
        except Exception as e:
            self.log_result(endpoint, "GET", 0, False, time.time() - start, str(e))

    def test_health(self) -> None:
        endpoint = "/health"
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            response_time = time.time() - start
            data = response.json()
            success = response.status_code == 200 and data.get("status") == "healthy" and "timestamp" in data
            self.log_result(endpoint, "GET", response.status_code, success, response_time)
        except Exception as e:
            self.log_result(endpoint, "GET", 0, False, time.time() - start, str(e))

    def test_get_strategies(self) -> List[str]:
        endpoint = "/strategies"
        start = time.time()
        strategy_modules = []
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            response_time = time.time() - start
            data = response.json()
            success = (response.status_code == 200 and
                      data.get("success") == True and
                      "strategies" in data and
                      "count" in data)
            self.log_result(endpoint, "GET", response.status_code, success, response_time)
            if success:
                print(f"  Found {data['count']} strategies")
                strategy_modules = [s.get("module") for s in data.get("strategies", [])]
        except Exception as e:
            self.log_result(endpoint, "GET", 0, False, time.time() - start, str(e))
        return strategy_modules

    def test_get_strategy_info(self, strategy_name: str) -> None:
        endpoint = f"/strategies/{strategy_name}"
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            response_time = time.time() - start
            data = response.json()
            success = (response.status_code == 200 and
                      data.get("success") == True and
                      "strategy" in data)
            self.log_result(endpoint, "GET", response.status_code, success, response_time)
            if success:
                strategy = data["strategy"]
                print(f"  Class: {strategy.get('class_name')}, Params: {len(strategy.get('parameters', {}))}")
        except Exception as e:
            self.log_result(endpoint, "GET", 0, False, time.time() - start, str(e))

    def test_get_default_parameters(self) -> None:
        endpoint = "/parameters/default"
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            response_time = time.time() - start
            data = response.json()
            success = (response.status_code == 200 and
                      data.get("success") == True and
                      "parameters" in data)
            self.log_result(endpoint, "GET", response.status_code, success, response_time)
            if success:
                params = data["parameters"]
                print(f"  Default cash: ${params.get('cash')}")
        except Exception as e:
            self.log_result(endpoint, "GET", 0, False, time.time() - start, str(e))

    def test_backtest(self, strategy: str = "bollinger_bands_strategy") -> None:
        endpoint = "/backtest"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        payload = {
            "ticker": "AAPL",
            "strategy": strategy,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "interval": "1d",
            "cash": 10000.0
        }

        start = time.time()
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
            response_time = time.time() - start
            data = response.json()
            success = (response.status_code == 200 and
                      data.get("success") == True and
                      "ticker" in data and
                      "return_pct" in data)
            self.log_result(endpoint, "POST", response.status_code, success, response_time)
            if success:
                print(f"  {data['ticker']}: ROI {data['return_pct']}%, Trades: {data['total_trades']}")
                if data.get('sharpe_ratio'):
                    print(f"  Sharpe: {data['sharpe_ratio']}, Max DD: {data.get('max_drawdown')}%")
        except Exception as e:
            self.log_result(endpoint, "POST", 0, False, time.time() - start, str(e))

    def test_market_data(self) -> None:
        endpoint = "/market-data"
        payload = {
            "ticker": "MSFT",
            "period": "5d",
            "interval": "1d"
        }

        start = time.time()
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
            response_time = time.time() - start
            data = response.json()
            success = (response.status_code == 200 and
                      data.get("success") == True and
                      "data" in data and
                      "statistics" in data)
            self.log_result(endpoint, "POST", response.status_code, success, response_time)
            if success:
                print(f"  {data['ticker']}: {data['data_points']} data points")
                stats = data.get("statistics", {})
                if stats.get("mean"):
                    print(f"  Mean: ${stats['mean']:.2f}, Range: ${stats['min']:.2f}-${stats['max']:.2f}")
        except Exception as e:
            self.log_result(endpoint, "POST", 0, False, time.time() - start, str(e))

    def test_invalid_strategy(self) -> None:
        endpoint = "/backtest"
        payload = {
            "ticker": "AAPL",
            "strategy": "nonexistent_strategy",
            "interval": "1d",
            "cash": 10000.0
        }

        start = time.time()
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
            response_time = time.time() - start
            success = response.status_code == 400 or response.status_code == 404
            self.log_result(f"{endpoint} (invalid)", "POST", response.status_code, success, response_time)
        except Exception as e:
            self.log_result(f"{endpoint} (invalid)", "POST", 0, False, time.time() - start, str(e))

    def test_invalid_ticker(self) -> None:
        endpoint = "/market-data"
        payload = {
            "ticker": "INVALIDticker123",
            "period": "5d",
            "interval": "1d"
        }

        start = time.time()
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
            response_time = time.time() - start
            success = response.status_code >= 400
            self.log_result(f"{endpoint} (invalid ticker)", "POST", response.status_code, success, response_time)
        except Exception as e:
            self.log_result(f"{endpoint} (invalid ticker)", "POST", 0, False, time.time() - start, str(e))

    def print_summary(self) -> None:
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")

        avg_time = sum(r["response_time_ms"] for r in self.results) / total if total > 0 else 0
        print(f"Average Response Time: {avg_time:.2f}ms")

        if failed > 0:
            print("\nFailed Tests:")
            for r in self.results:
                if not r["success"]:
                    print(f"  - {r['method']} {r['endpoint']} ({r['status_code']}): {r.get('error', 'Unknown error')}")

        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("\nDetailed results saved to: test_results.json")

    def run_all_tests(self) -> None:
        print("="*60)
        print("STRATEGYBUILDER API TEST SUITE")
        print("="*60)
        print(f"Target: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        print("1. Testing Root Endpoint...")
        self.test_root()

        print("\n2. Testing Health Check...")
        self.test_health()

        print("\n3. Testing Get Strategies...")
        strategies = self.test_get_strategies()

        print("\n4. Testing Get Strategy Info...")
        if strategies:
            self.test_get_strategy_info(strategies[0])

        print("\n5. Testing Default Parameters...")
        self.test_get_default_parameters()

        print("\n6. Testing Market Data...")
        self.test_market_data()

        print("\n7. Testing Backtest...")
        if strategies:
            self.test_backtest(strategies[0])

        print("\n8. Testing Error Handling (Invalid Strategy)...")
        self.test_invalid_strategy()

        print("\n9. Testing Error Handling (Invalid Ticker)...")
        self.test_invalid_ticker()

        self.print_summary()

if __name__ == "__main__":
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL

    tester = APITester(base_url)

    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        tester.print_summary()
