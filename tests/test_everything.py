"""
Master test runner - executes all test suites
Runs tests in sequence and provides comprehensive summary
"""
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

class Color:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TestRunner:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None

    def print_header(self):
        """Print test suite header"""
        print("\n" + "="*70)
        print(f"{Color.BOLD}{Color.CYAN}STRATEGYBUILDER COMPREHENSIVE TEST SUITE{Color.END}")
        print("="*70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

    def run_test(self, test_name, test_file, needs_api=False):
        """Run a single test file"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}Running: {test_name}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}\n")

        if needs_api:
            print(f"{Color.YELLOW}[WARN] This test requires API server running on localhost:8086{Color.END}")
            print(f"{Color.YELLOW}  Start server with: python -m src.api.main{Color.END}\n")

        start = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            duration = time.time() - start

            # Print test output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{Color.YELLOW}Warnings/Errors:{Color.END}")
                print(result.stderr)

            # Determine if test passed
            passed = result.returncode == 0

            self.results.append({
                'name': test_name,
                'file': test_file,
                'passed': passed,
                'duration': duration,
                'returncode': result.returncode
            })

            if passed:
                print(f"\n{Color.GREEN}[OK] {test_name} PASSED{Color.END} (took {duration:.2f}s)")
            else:
                print(f"\n{Color.RED}[FAIL] {test_name} FAILED{Color.END} (exit code: {result.returncode})")

            return passed

        except subprocess.TimeoutExpired:
            duration = time.time() - start
            print(f"\n{Color.RED}[FAIL] {test_name} TIMEOUT{Color.END} (exceeded {duration:.2f}s)")
            self.results.append({
                'name': test_name,
                'file': test_file,
                'passed': False,
                'duration': duration,
                'returncode': -1
            })
            return False

        except Exception as e:
            duration = time.time() - start
            print(f"\n{Color.RED}[FAIL] {test_name} ERROR: {str(e)}{Color.END}")
            self.results.append({
                'name': test_name,
                'file': test_file,
                'passed': False,
                'duration': duration,
                'returncode': -2
            })
            return False

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n\n" + "="*70)
        print(f"{Color.BOLD}{Color.CYAN}FINAL TEST SUMMARY{Color.END}")
        print("="*70 + "\n")

        total_duration = sum(r['duration'] for r in self.results)
        passed_count = sum(1 for r in self.results if r['passed'])
        failed_count = len(self.results) - passed_count

        # Print individual results
        print(f"{Color.BOLD}Test Results:{Color.END}\n")
        for i, result in enumerate(self.results, 1):
            status = f"{Color.GREEN}[OK] PASSED{Color.END}" if result['passed'] else f"{Color.RED}[FAIL] FAILED{Color.END}"
            print(f"  {i}. {result['name']:<40} {status} ({result['duration']:.2f}s)")

        # Print statistics
        print(f"\n{Color.BOLD}Statistics:{Color.END}\n")
        print(f"  Total Tests:     {len(self.results)}")
        print(f"  {Color.GREEN}Passed:          {passed_count}{Color.END}")
        print(f"  {Color.RED}Failed:          {failed_count}{Color.END}")
        print(f"  Total Duration:  {total_duration:.2f}s")
        print(f"  Average Time:    {total_duration/len(self.results):.2f}s per test")

        # Print overall result
        print("\n" + "="*70)
        if failed_count == 0:
            print(f"{Color.BOLD}{Color.GREEN}[OK] ALL TESTS PASSED!{Color.END}")
            success_rate = 100.0
        else:
            success_rate = (passed_count / len(self.results)) * 100
            print(f"{Color.BOLD}{Color.YELLOW}[WARN] SOME TESTS FAILED{Color.END}")

        print(f"{Color.BOLD}Success Rate: {success_rate:.1f}%{Color.END}")
        print("="*70 + "\n")

        return failed_count == 0

def check_api_server():
    """Check if API server is running"""
    import requests
    try:
        response = requests.get("http://localhost:8086/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    runner = TestRunner()
    runner.start_time = time.time()

    runner.print_header()

    # Define all tests in order
    tests = [
        {
            'name': 'Import Validation',
            'file': Path('tests/test_imports.py'),
            'needs_api': False,
            'description': 'Validates all module imports and __init__ files'
        },
        {
            'name': 'Indicator Accuracy',
            'file': Path('tests/test_indicators.py'),
            'needs_api': False,
            'description': 'Tests custom indicators (OBV, MFI, CMF)'
        },
        {
            'name': 'Strategy Validation',
            'file': Path('tests/test_strategies.py'),
            'needs_api': False,
            'description': 'Validates all strategy implementations'
        },
        {
            'name': 'Backtest Endpoint',
            'file': Path('tests/test_backtest.py'),
            'needs_api': True,
            'description': 'Tests backtest API endpoint functionality'
        },
        {
            'name': 'Optimization Endpoint',
            'file': Path('tests/test_optimization.py'),
            'needs_api': True,
            'description': 'Tests optimization API endpoint functionality'
        },
        {
            'name': 'Preset Management',
            'file': Path('tests/test_presets.py'),
            'needs_api': True,
            'description': 'Tests strategy preset creation and execution'
        },
        {
            'name': 'Snapshot (Live Data)',
            'file': Path('tests/test_snapshot.py'),
            'needs_api': True,
            'description': 'Tests near-real-time snapshot endpoint for live monitoring'
        }
    ]

    # Check if API-dependent tests should be skipped
    api_running = check_api_server()
    if not api_running:
        print(f"{Color.YELLOW}[WARN] API server is not running{Color.END}")
        print(f"{Color.YELLOW}  API-dependent tests will be skipped{Color.END}")
        print(f"{Color.YELLOW}  Start server with: python -m src.api.main{Color.END}\n")

    # Run all tests
    for test in tests:
        if test['needs_api'] and not api_running:
            print(f"\n{Color.YELLOW}Skipping {test['name']} (API server not running){Color.END}")
            runner.results.append({
                'name': test['name'],
                'file': test['file'],
                'passed': None,
                'duration': 0,
                'returncode': -3
            })
            continue

        if not test['file'].exists():
            print(f"\n{Color.RED}[FAIL] Test file not found: {test['file']}{Color.END}")
            runner.results.append({
                'name': test['name'],
                'file': test['file'],
                'passed': False,
                'duration': 0,
                'returncode': -4
            })
            continue

        runner.run_test(test['name'], test['file'], test['needs_api'])

        # Brief pause between tests
        time.sleep(1)

    runner.end_time = time.time()

    # Print summary
    success = runner.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
