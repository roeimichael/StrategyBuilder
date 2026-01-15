import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import time

BASE_URL = "http://localhost:8086"


class SnapshotTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_api_health(self):
        """Test that API is running"""
        print("\n" + "="*60)
        print("SNAPSHOT ENDPOINT TEST SUITE")
        print("="*60)
        print("Make sure the API server is running on localhost:8086")
        print("Start server with: python -m src.api.main")
        print("="*60)

        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("[OK] API server is running\n")
                return True
            else:
                print("[FAIL] API server returned non-200 status")
                return False
        except requests.exceptions.ConnectionError:
            print("[FAIL] Cannot connect to API server")
            print("Please start the server first: python -m src.api.main")
            return False

    def test_basic_snapshot(self):
        """Test basic snapshot request"""
        print("\n" + "="*60)
        print("TEST 1: Basic Snapshot - Bollinger Bands")
        print("="*60)

        try:
            response = requests.post(
                f"{BASE_URL}/snapshot",
                json={
                    "ticker": "AAPL",
                    "strategy": "bollinger_bands_strategy",
                    "parameters": {
                        "period": 20,
                        "devfactor": 2.0
                    },
                    "interval": "1d",
                    "lookback_bars": 200,
                    "cash": 10000.0
                }
            )

            if response.status_code == 200:
                print(f"[OK] Status Code: {response.status_code}")
                result = response.json()

                # Check required fields
                required_fields = ['success', 'ticker', 'strategy', 'last_bar', 'indicators',
                                 'position_state', 'recent_trades', 'portfolio_value', 'cash', 'timestamp']

                all_present = True
                for field in required_fields:
                    if field in result:
                        print(f"  [OK] {field}: present")
                    else:
                        print(f"  [FAIL] {field}: missing")
                        all_present = False

                if all_present:
                    print(f"\n  Ticker: {result.get('ticker')}")
                    print(f"  Strategy: {result.get('strategy')}")
                    print(f"  Lookback Bars: {result.get('lookback_bars')}")

                    # Check last_bar
                    last_bar = result.get('last_bar', {})
                    if last_bar:
                        print(f"\n  Last Bar:")
                        print(f"    Date: {last_bar.get('date')}")
                        print(f"    Close: ${last_bar.get('close', 0):.2f}")

                    # Check indicators
                    indicators = result.get('indicators', {})
                    print(f"\n  Indicators: {len(indicators)} found")
                    for key in list(indicators.keys())[:5]:  # Show first 5
                        print(f"    {key}: {indicators[key]}")

                    # Check position state
                    position = result.get('position_state', {})
                    print(f"\n  Position State:")
                    print(f"    In Position: {position.get('in_position')}")
                    if position.get('in_position'):
                        print(f"    Type: {position.get('position_type')}")
                        print(f"    Entry Price: ${position.get('entry_price', 0):.2f}")

                    # Check recent trades
                    trades = result.get('recent_trades', [])
                    print(f"\n  Recent Trades: {len(trades)}")

                    print(f"\n[OK] Snapshot completed successfully")
                    self.passed += 1
                else:
                    print(f"\n[FAIL] Missing required fields")
                    self.failed += 1
                    self.errors.append("Basic snapshot missing fields")
            else:
                print(f"[FAIL] Status Code: {response.status_code}")
                print(f"  Error: {response.text}")
                self.failed += 1
                self.errors.append(f"Basic snapshot returned {response.status_code}")

        except Exception as e:
            print(f"[FAIL] Exception: {str(e)}")
            self.failed += 1
            self.errors.append(f"Basic snapshot exception: {str(e)}")

    def test_snapshot_with_different_lookbacks(self):
        """Test snapshot with different lookback periods"""
        print("\n" + "="*60)
        print("TEST 2: Different Lookback Periods")
        print("="*60)

        lookback_values = [50, 100, 200]

        for lookback in lookback_values:
            try:
                print(f"\n  Testing lookback={lookback}...")
                response = requests.post(
                    f"{BASE_URL}/snapshot",
                    json={
                        "ticker": "AAPL",
                        "strategy": "rsi_stochastic_strategy",
                        "parameters": {
                            "rsi_period": 14,
                            "rsi_oversold": 30,
                            "rsi_overbought": 70
                        },
                        "interval": "1d",
                        "lookback_bars": lookback
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('lookback_bars') == lookback:
                        print(f"  [OK] lookback={lookback}: Success")
                    else:
                        print(f"  [FAIL] lookback mismatch")
                        self.failed += 1
                        return
                else:
                    print(f"  [FAIL] lookback={lookback}: {response.status_code}")
                    self.failed += 1
                    return

            except Exception as e:
                print(f"  [FAIL] Exception with lookback={lookback}: {str(e)}")
                self.failed += 1
                return

        print(f"\n[OK] All lookback periods tested successfully")
        self.passed += 1

    def test_snapshot_invalid_inputs(self):
        """Test snapshot with invalid inputs"""
        print("\n" + "="*60)
        print("TEST 3: Invalid Input Handling")
        print("="*60)

        test_cases = [
            {
                "name": "Invalid ticker",
                "data": {
                    "ticker": "INVALID_TICKER_12345",
                    "strategy": "bollinger_bands_strategy",
                    "interval": "1d",
                    "lookback_bars": 200
                },
                "expected_status": [400]
            },
            {
                "name": "Invalid strategy",
                "data": {
                    "ticker": "AAPL",
                    "strategy": "nonexistent_strategy",
                    "interval": "1d",
                    "lookback_bars": 200
                },
                "expected_status": [404]
            }
        ]

        for test_case in test_cases:
            try:
                print(f"\n  Testing {test_case['name']}...")
                response = requests.post(f"{BASE_URL}/snapshot", json=test_case['data'])

                if response.status_code in test_case['expected_status']:
                    print(f"  [OK] Correctly returned error status: {response.status_code}")
                else:
                    print(f"  [FAIL] Unexpected status code: {response.status_code}")
                    self.failed += 1
                    return

            except Exception as e:
                print(f"  [FAIL] Exception: {str(e)}")
                self.failed += 1
                return

        print(f"\n[OK] All invalid input tests passed")
        self.passed += 1

    def test_snapshot_multiple_strategies(self):
        """Test snapshot with multiple different strategies"""
        print("\n" + "="*60)
        print("TEST 4: Multiple Strategy Validation")
        print("="*60)

        strategies = [
            ("bollinger_bands_strategy", {"period": 20, "devfactor": 2.0}),
            ("rsi_stochastic_strategy", {"rsi_period": 14}),
            ("mfi_strategy", {"mfi_period": 14}),
        ]

        for strategy_name, params in strategies:
            try:
                print(f"\n  Testing {strategy_name}...")
                response = requests.post(
                    f"{BASE_URL}/snapshot",
                    json={
                        "ticker": "AAPL",
                        "strategy": strategy_name,
                        "parameters": params,
                        "interval": "1d",
                        "lookback_bars": 200
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    indicators = result.get('indicators', {})
                    print(f"  [OK] {strategy_name}: {len(indicators)} indicators")
                else:
                    print(f"  [FAIL] {strategy_name}: {response.status_code}")
                    self.failed += 1
                    return

            except Exception as e:
                print(f"  [FAIL] Exception with {strategy_name}: {str(e)}")
                self.failed += 1
                return

        print(f"\n[OK] All strategies tested successfully")
        self.passed += 1

    def test_snapshot_performance(self):
        """Test snapshot response time"""
        print("\n" + "="*60)
        print("TEST 5: Performance Check")
        print("="*60)

        try:
            start_time = time.time()

            response = requests.post(
                f"{BASE_URL}/snapshot",
                json={
                    "ticker": "AAPL",
                    "strategy": "bollinger_bands_strategy",
                    "parameters": {"period": 20, "devfactor": 2.0},
                    "interval": "1d",
                    "lookback_bars": 200
                }
            )

            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                print(f"[OK] Response Time: {elapsed_time:.2f} seconds")

                if elapsed_time < 10:
                    print(f"[OK] Performance acceptable (< 10s)")
                    self.passed += 1
                else:
                    print(f"[WARN] Slow response (> 10s)")
                    self.passed += 1  # Still pass, just slow
            else:
                print(f"[FAIL] Request failed: {response.status_code}")
                self.failed += 1

        except Exception as e:
            print(f"[FAIL] Exception: {str(e)}")
            self.failed += 1

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.failed == 0:
            print("\n[OK] All tests passed!")
            return 0
        else:
            print(f"\n[FAIL] {self.failed} test(s) failed")
            return 1


def main():
    tester = SnapshotTester()

    if not tester.test_api_health():
        return 1

    tester.test_basic_snapshot()
    tester.test_snapshot_with_different_lookbacks()
    tester.test_snapshot_invalid_inputs()
    tester.test_snapshot_multiple_strategies()
    tester.test_snapshot_performance()

    return tester.print_summary()


if __name__ == "__main__":
    exit(main())
