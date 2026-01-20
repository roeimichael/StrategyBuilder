"""
Test script for strategy presets functionality
Tests preset creation, listing, deletion, and backtest execution
"""
import requests
import json

BASE_URL = "http://localhost:8086"

class PresetTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.created_preset_id = None

    def test_create_preset(self):
        """Test creating a new preset"""
        print("\n" + "="*60)
        print("TEST 1: Create Preset")
        print("="*60)

        try:
            response = requests.post(
                f"{BASE_URL}/presets",
                json={
                    "name": "Aggressive RSI Strategy",
                    "strategy": "rsi_stochastic_strategy",
                    "parameters": {
                        "rsi_period": 14,
                        "rsi_oversold": 30,
                        "rsi_overbought": 70,
                        "stoch_period": 14,
                        "stoch_oversold": 20,
                        "stoch_overbought": 80
                    },
                    "notes": "Aggressive mean reversion strategy for volatile markets"
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Status Code: {response.status_code}")
                print(f"  Preset ID: {result['id']}")
                print(f"  Name: {result['name']}")
                print(f"  Strategy: {result['strategy']}")
                print(f"  Parameters: {result['parameters']}")
                print(f"  Notes: {result.get('notes', 'None')}")

                self.created_preset_id = result['id']
                self.passed += 1
                return True
            else:
                print(f"[FAIL] Failed with status code: {response.status_code}")
                print(f"  Error: {response.text}")
                self.failed += 1
                self.errors.append(f"Test 1 failed: {response.text}")
                return False

        except Exception as e:
            print(f"[FAIL] Exception occurred: {str(e)}")
            self.failed += 1
            self.errors.append(f"Test 1 exception: {str(e)}")
            return False

    def test_create_duplicate_preset(self):
        """Test that duplicate presets are rejected"""
        print("\n" + "="*60)
        print("TEST 2: Create Duplicate Preset (Should Fail)")
        print("="*60)

        try:
            response = requests.post(
                f"{BASE_URL}/presets",
                json={
                    "name": "Aggressive RSI Strategy",
                    "strategy": "rsi_stochastic_strategy",
                    "parameters": {"rsi_period": 14}
                }
            )

            if response.status_code == 409:
                print(f"[OK] Correctly rejected duplicate preset with 409 Conflict")
                self.passed += 1
                return True
            else:
                print(f"[FAIL] Expected 409, got {response.status_code}")
                self.failed += 1
                return False

        except Exception as e:
            print(f"[FAIL] Exception occurred: {str(e)}")
            self.failed += 1
            return False

    def test_list_presets(self):
        """Test listing presets"""
        print("\n" + "="*60)
        print("TEST 3: List Presets")
        print("="*60)

        try:
            response = requests.get(f"{BASE_URL}/presets")

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Status Code: {response.status_code}")
                print(f"  Success: {result['success']}")
                print(f"  Total Count: {result['total_count']}")
                print(f"  Returned: {result['count']} presets")

                if result['count'] > 0:
                    print(f"\n  First preset:")
                    first = result['presets'][0]
                    print(f"    ID: {first['id']}")
                    print(f"    Name: {first['name']}")
                    print(f"    Strategy: {first['strategy']}")
                    print(f"    Parameters: {first['parameters']}")

                self.passed += 1
                return True
            else:
                print(f"[FAIL] Failed with status code: {response.status_code}")
                self.failed += 1
                return False

        except Exception as e:
            print(f"[FAIL] Exception occurred: {str(e)}")
            self.failed += 1
            return False

    def test_list_presets_filtered(self):
        """Test listing presets with filters"""
        print("\n" + "="*60)
        print("TEST 4: List Presets with Filters")
        print("="*60)

        try:
            response = requests.get(
                f"{BASE_URL}/presets",
                params={"strategy": "rsi_stochastic_strategy"}
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Filtered by strategy=rsi_stochastic_strategy")
                print(f"  Found {result['count']} matching presets")

                self.passed += 1
                return True
            else:
                print(f"[FAIL] Failed with status code: {response.status_code}")
                self.failed += 1
                return False

        except Exception as e:
            print(f"[FAIL] Exception occurred: {str(e)}")
            self.failed += 1
            return False

    def test_backtest_from_preset(self):
        """Test running backtest from a preset"""
        print("\n" + "="*60)
        print("TEST 5: Run Backtest from Preset")
        print("="*60)

        if not self.created_preset_id:
            print("[WARN] Skipping: No preset ID available")
            return False

        try:
            response = requests.post(
                f"{BASE_URL}/presets/{self.created_preset_id}/backtest",
                params={
                    "ticker": "AAPL",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30",
                    "interval": "1d",
                    "cash": 10000.0
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Status Code: {response.status_code}")
                print(f"  Ticker: {result['ticker']}")
                print(f"  Strategy: {result['strategy']}")
                print(f"  PnL: ${result['pnl']:.2f}")
                print(f"  Return: {result['return_pct']:.2f}%")
                print(f"  Total Trades: {result['total_trades']}")

                self.passed += 1
                return True
            else:
                print(f"[FAIL] Failed with status code: {response.status_code}")
                print(f"  Error: {response.text}")
                self.failed += 1
                return False

        except Exception as e:
            print(f"[FAIL] Exception occurred: {str(e)}")
            self.failed += 1
            return False

    def test_delete_preset(self):
        """Test deleting a preset"""
        print("\n" + "="*60)
        print("TEST 6: Delete Preset")
        print("="*60)

        if not self.created_preset_id:
            print("[WARN] Skipping: No preset ID available")
            return False

        try:
            response = requests.delete(
                f"{BASE_URL}/presets/{self.created_preset_id}"
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Status Code: {response.status_code}")
                print(f"  Success: {result['success']}")
                print(f"  Message: {result['message']}")

                self.passed += 1
                return True
            else:
                print(f"[FAIL] Failed with status code: {response.status_code}")
                self.failed += 1
                return False

        except Exception as e:
            print(f"[FAIL] Exception occurred: {str(e)}")
            self.failed += 1
            return False

    def test_invalid_strategy(self):
        """Test creating preset with invalid strategy"""
        print("\n" + "="*60)
        print("TEST 7: Create Preset with Invalid Strategy")
        print("="*60)

        try:
            response = requests.post(
                f"{BASE_URL}/presets",
                json={
                    "name": "Invalid Strategy Test",
                    "strategy": "nonexistent_strategy",
                    "parameters": {}
                }
            )

            if response.status_code == 404:
                print(f"[OK] Correctly rejected invalid strategy with 404")
                self.passed += 1
                return True
            else:
                print(f"[FAIL] Expected 404, got {response.status_code}")
                self.failed += 1
                return False

        except Exception as e:
            print(f"[FAIL] Exception occurred: {str(e)}")
            self.failed += 1
            return False

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
            return True
        else:
            print(f"\n[FAIL] {self.failed} test(s) failed")
            return False

def main():
    print("="*60)
    print("STRATEGY PRESETS TEST SUITE")
    print("="*60)
    print("Make sure the API server is running on localhost:8086")
    print("Start server with: python -m src.api.main")
    print("="*60)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("[OK] API server is running\n")
        else:
            print("[FAIL] API server returned unexpected response")
            return False
    except requests.exceptions.RequestException:
        print("[FAIL] Could not connect to API server")
        print("Please start the server first!")
        return False

    # Run tests
    tester = PresetTester()

    tester.test_create_preset()
    tester.test_create_duplicate_preset()
    tester.test_list_presets()
    tester.test_list_presets_filtered()
    tester.test_backtest_from_preset()
    tester.test_delete_preset()
    tester.test_invalid_strategy()

    return tester.print_summary()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
