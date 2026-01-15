"""
Test script for backtest endpoint validation
Tests various strategies with different parameters and validates results
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8086"

class BacktestTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_basic_backtest(self):
        """Test basic backtest with Bollinger Bands"""
        print("\n" + "="*60)
        print("TEST 1: Basic Backtest - Bollinger Bands")
        print("="*60)

        try:
            response = requests.post(
                f"{BASE_URL}/backtest",
                json={
                    "ticker": "AAPL",
                    "strategy": "bollinger_bands_strategy",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30",
                    "interval": "1d",
                    "cash": 10000.0,
                    "parameters": {
                        "period": 20,
                        "devfactor": 2.0
                    },
                    "include_chart_data": False
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Success: {result['success']}")
                print(f"  Ticker: {result['ticker']}")
                print(f"  Strategy: {result['strategy']}")
                print(f"  PnL: ${result['pnl']:.2f}")
                print(f"  Return: {result['return_pct']:.2f}%")
                print(f"  Sharpe Ratio: {result.get('sharpe_ratio', 'N/A')}")
                print(f"  Total Trades: {result['total_trades']}")

                # Validate response structure
                assert result['success'] == True
                assert 'pnl' in result
                assert 'return_pct' in result
                assert 'total_trades' in result

                self.passed += 1
                return True
            else:
                print(f"✗ Failed with status code: {response.status_code}")
                print(f"  Error: {response.text}")
                self.failed += 1
                self.errors.append(f"Test 1 failed: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Exception occurred: {str(e)}")
            self.failed += 1
            self.errors.append(f"Test 1 exception: {str(e)}")
            return False

    def test_backtest_with_chart_data(self):
        """Test backtest with chart data included"""
        print("\n" + "="*60)
        print("TEST 2: Backtest with Chart Data")
        print("="*60)

        try:
            response = requests.post(
                f"{BASE_URL}/backtest",
                json={
                    "ticker": "BTC-USD",
                    "strategy": "williams_r_strategy",
                    "start_date": "2024-03-01",
                    "end_date": "2024-05-31",
                    "interval": "1d",
                    "cash": 10000.0,
                    "parameters": {
                        "period": 14,
                        "oversold": -80,
                        "overbought": -20
                    },
                    "include_chart_data": True,
                    "columnar_format": True
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✓ Status Code: {response.status_code}")
                print(f"✓ Chart data included: {result['chart_data'] is not None}")

                if result['chart_data']:
                    # Check if columnar format
                    if isinstance(result['chart_data'], dict):
                        print(f"✓ Columnar format verified")
                        print(f"  Data points: {len(result['chart_data'].get('timestamp', []))}")
                    else:
                        print(f"  Chart data format: list of {len(result['chart_data'])} points")

                print(f"  PnL: ${result['pnl']:.2f}")
                print(f"  Return: {result['return_pct']:.2f}%")

                self.passed += 1
                return True
            else:
                print(f"✗ Failed with status code: {response.status_code}")
                self.failed += 1
                self.errors.append(f"Test 2 failed: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Exception occurred: {str(e)}")
            self.failed += 1
            self.errors.append(f"Test 2 exception: {str(e)}")
            return False

    def test_multiple_strategies(self):
        """Test multiple strategies to ensure they all work"""
        print("\n" + "="*60)
        print("TEST 3: Multiple Strategy Validation")
        print("="*60)

        strategies = [
            ("rsi_stochastic_strategy", {"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70,
                                          "stoch_period": 14, "stoch_oversold": 20, "stoch_overbought": 80}),
            ("mfi_strategy", {"period": 14, "oversold": 20, "overbought": 80}),
            ("keltner_channel_strategy", {"ema_period": 20, "atr_period": 10, "atr_multiplier": 2.0}),
            ("tema_macd_strategy", {"macd1": 12, "macd2": 26, "macdsig": 9, "tema_period": 12})
        ]

        for strategy_name, params in strategies:
            try:
                print(f"\n  Testing {strategy_name}...")
                response = requests.post(
                    f"{BASE_URL}/backtest",
                    json={
                        "ticker": "ETH-USD",
                        "strategy": strategy_name,
                        "start_date": "2024-04-01",
                        "end_date": "2024-05-31",
                        "interval": "1d",
                        "cash": 10000.0,
                        "parameters": params,
                        "include_chart_data": False
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✓ {strategy_name}: PnL=${result['pnl']:.2f}, Trades={result['total_trades']}")
                    self.passed += 1
                else:
                    print(f"  ✗ {strategy_name} failed: {response.status_code}")
                    self.failed += 1
                    self.errors.append(f"{strategy_name} failed: {response.text}")

            except Exception as e:
                print(f"  ✗ {strategy_name} exception: {str(e)}")
                self.failed += 1
                self.errors.append(f"{strategy_name} exception: {str(e)}")

    def test_invalid_inputs(self):
        """Test error handling with invalid inputs"""
        print("\n" + "="*60)
        print("TEST 4: Invalid Input Handling")
        print("="*60)

        test_cases = [
            {
                "name": "Invalid ticker",
                "data": {
                    "ticker": "INVALID_TICKER_12345",
                    "strategy": "bollinger_bands_strategy",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30"
                },
                "expected_status": [400, 500]
            },
            {
                "name": "Invalid strategy",
                "data": {
                    "ticker": "AAPL",
                    "strategy": "nonexistent_strategy",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30"
                },
                "expected_status": [400, 404]
            },
            {
                "name": "Invalid date range",
                "data": {
                    "ticker": "AAPL",
                    "strategy": "bollinger_bands_strategy",
                    "start_date": "2024-06-30",
                    "end_date": "2024-01-01"
                },
                "expected_status": [400, 500]
            }
        ]

        for test_case in test_cases:
            try:
                print(f"\n  Testing {test_case['name']}...")
                response = requests.post(f"{BASE_URL}/backtest", json=test_case['data'])

                if response.status_code in test_case['expected_status']:
                    print(f"  ✓ Correctly returned error status: {response.status_code}")
                    self.passed += 1
                else:
                    print(f"  ✗ Unexpected status code: {response.status_code}")
                    self.failed += 1

            except Exception as e:
                print(f"  ✗ Exception: {str(e)}")
                self.failed += 1

    def test_performance_metrics(self):
        """Test that all performance metrics are calculated"""
        print("\n" + "="*60)
        print("TEST 5: Performance Metrics Validation")
        print("="*60)

        try:
            response = requests.post(
                f"{BASE_URL}/backtest",
                json={
                    "ticker": "AAPL",
                    "strategy": "alligator_strategy",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30",
                    "interval": "1d",
                    "cash": 10000.0,
                    "parameters": {
                        "lips_period": 5,
                        "teeth_period": 8,
                        "jaws_period": 13,
                        "ema_period": 200
                    }
                }
            )

            if response.status_code == 200:
                result = response.json()
                required_fields = ['pnl', 'return_pct', 'sharpe_ratio', 'max_drawdown',
                                  'total_trades', 'start_value', 'end_value']

                print(f"✓ Checking required metrics...")
                missing_fields = []
                for field in required_fields:
                    if field in result:
                        print(f"  ✓ {field}: {result[field]}")
                    else:
                        print(f"  ✗ Missing: {field}")
                        missing_fields.append(field)

                if not missing_fields:
                    print(f"\n✓ All required metrics present")
                    self.passed += 1
                else:
                    print(f"\n✗ Missing metrics: {missing_fields}")
                    self.failed += 1
                    self.errors.append(f"Missing metrics: {missing_fields}")

            else:
                print(f"✗ Request failed: {response.status_code}")
                self.failed += 1

        except Exception as e:
            print(f"✗ Exception: {str(e)}")
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
            print("\n✓ All tests passed!")
            return True
        else:
            print(f"\n✗ {self.failed} test(s) failed")
            return False

def main():
    print("="*60)
    print("BACKTEST ENDPOINT TEST SUITE")
    print("="*60)
    print("Make sure the API server is running on localhost:8086")
    print("Start server with: python -m src.api.main")
    print("="*60)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ API server is running\n")
        else:
            print("✗ API server returned unexpected response")
            return False
    except requests.exceptions.RequestException:
        print("✗ Could not connect to API server")
        print("Please start the server first!")
        return False

    # Run tests
    tester = BacktestTester()

    tester.test_basic_backtest()
    tester.test_backtest_with_chart_data()
    tester.test_multiple_strategies()
    tester.test_invalid_inputs()
    tester.test_performance_metrics()

    return tester.print_summary()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
