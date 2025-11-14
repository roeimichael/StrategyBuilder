"""Master test runner - Execute all test suites"""
import sys
import subprocess
import time


def run_test_suite(test_name, test_file):
    """Run a single test suite and return success status"""
    print("\n" + "=" * 100)
    print(f"RUNNING: {test_name}")
    print("=" * 100)

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            check=False
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"\nPASSED {test_name} ({elapsed:.1f}s)")
            return True
        else:
            print(f"\nFAILED {test_name} ({elapsed:.1f}s)")
            return False

    except Exception as e:
        print(f"\nERROR {test_name}: {str(e)}")
        return False


def main():
    """Run all test suites"""
    print("=" * 100)
    print("STRATEGYBUILDER PRO - COMPREHENSIVE TEST SUITE")
    print("=" * 100)
    print("\nThis will run all test suites:")
    print("  1. Database Operations")
    print("  2. Grid Search Optimizer")
    print("  3. All Strategies (12 strategies × 5 configs × 5 stocks = 300 tests)")
    print("\nEstimated time: 10-20 minutes depending on system performance")
    print("=" * 100)

    input("\nPress Enter to begin testing...")

    test_suites = [
        ("Database Operations", "tests/test_database.py"),
        ("Grid Search Optimizer", "tests/test_grid_search.py"),
        ("Comprehensive Strategy Testing", "tests/test_all_strategies.py"),
    ]

    results = {}
    overall_start = time.time()

    for test_name, test_file in test_suites:
        results[test_name] = run_test_suite(test_name, test_file)

    overall_elapsed = time.time() - overall_start

    print("\n" + "=" * 100)
    print("FINAL TEST SUMMARY")
    print("=" * 100)

    total_tests = len(test_suites)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests

    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name:50} {status}")

    print("\n" + "-" * 100)
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    print(f"Total Time: {overall_elapsed/60:.1f} minutes")
    print("=" * 100)

    if failed_tests == 0:
        print("\nALL TESTS PASSED! System is ready for beta release.")
        return 0
    else:
        print(f"\n{failed_tests} test suite(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
