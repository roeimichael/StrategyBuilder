"""Master test runner for all domain endpoint tests."""
import sys
import os
from datetime import datetime

project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)

test_modules = []

try:
    from tests.domains.strategies import test_strategies
    test_modules.append(('Strategies', test_strategies))
except ImportError as e:
    print(f"Warning: Could not import test_strategies: {e}")

try:
    from tests.domains.run_history import test_run_history
    test_modules.append(('Run History', test_run_history))
except ImportError as e:
    print(f"Warning: Could not import test_run_history: {e}")

try:
    from tests.domains.market_scans import test_market_scans
    test_modules.append(('Market Scans', test_market_scans))
except ImportError as e:
    print(f"Warning: Could not import test_market_scans: {e}")

try:
    from tests.domains.presets import test_presets
    test_modules.append(('Presets', test_presets))
except ImportError as e:
    print(f"Warning: Could not import test_presets: {e}")

try:
    from tests.domains.backtests import test_backtests
    test_modules.append(('Backtests', test_backtests))
except ImportError as e:
    print(f"Warning: Could not import test_backtests: {e}")

try:
    from tests.domains.optimizations import test_optimizations
    test_modules.append(('Optimizations', test_optimizations))
except ImportError as e:
    print(f"Warning: Could not import test_optimizations: {e}")

try:
    from tests.domains.portfolios import test_portfolios
    test_modules.append(('Portfolios', test_portfolios))
except ImportError as e:
    print(f"Warning: Could not import test_portfolios: {e}")

try:
    from tests.domains.watchlists import test_watchlists
    test_modules.append(('Watchlists', test_watchlists))
except ImportError as e:
    print(f"Warning: Could not import test_watchlists: {e}")

try:
    from tests.domains.market_data import test_market_data
    test_modules.append(('Market Data', test_market_data))
except ImportError as e:
    print(f"Warning: Could not import test_market_data: {e}")

def print_header() -> None:
    print("\n" + "=" * 80)
    print(" " * 20 + "STRATEGYBUILDER COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test modules: {len(test_modules)}")
    print("=" * 80 + "\n")

def print_footer(results: list) -> bool:
    print("\n" + "=" * 80)
    print(" " * 30 + "FINAL RESULTS")
    print("=" * 80)
    total_domains = len(results)
    passed_domains = sum(1 for r in results if r['passed'])
    failed_domains = total_domains - passed_domains
    print(f"\nDomains tested: {total_domains}")
    print(f"Domains passed: {passed_domains}")
    print(f"Domains failed: {failed_domains}\n")
    for result in results:
        status = "PASS" if result['passed'] else "FAIL"
        print(f"  [{status}]  {result['name']}")
    print("\n" + "=" * 80)
    if failed_domains == 0:
        print("ALL TESTS PASSED - System is ready!")
    else:
        print(f"{failed_domains} domain(s) failed - Please review errors above")
    print("=" * 80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    return failed_domains == 0

def run_all_tests() -> bool:
    print_header()
    results = []
    for domain_name, test_module in test_modules:
        print("\n" + "-" * 80)
        print(f"Running {domain_name} Tests...")
        print("-" * 80 + "\n")
        try:
            test_results = test_module.run_tests()
            # Handle both list of results and boolean return values
            if isinstance(test_results, list):
                # If it's a list, check if all tests passed
                passed = all(r.get('passed', False) for r in test_results)
            else:
                # If it's a boolean, use it directly
                passed = bool(test_results)
            results.append({'name': domain_name, 'passed': passed})
        except Exception as e:
            print(f"ERROR running {domain_name} tests: {e}")
            import traceback
            traceback.print_exc()
            results.append({'name': domain_name, 'passed': False})
    all_passed = print_footer(results)
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
