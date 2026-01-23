#!/usr/bin/env python3
"""
Master Test Runner - test_everything.py

Runs all domain endpoint tests sequentially and provides a comprehensive report.
Located in shared/utils as requested to centralize testing utilities.

Usage:
    python src/shared/utils/test_everything.py

    # Or from project root
    python -m src.shared.utils.test_everything
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)

# Import all test modules
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

# TODO: Add imports for remaining test modules as they are created
# from tests.domains.backtests import test_backtests
# from tests.domains.optimizations import test_optimizations
# from tests.domains.watchlists import test_watchlists
# from tests.domains.portfolios import test_portfolios
# from tests.domains.live_monitor import test_live_monitor
# from tests.domains.market_data import test_market_data
# from tests.domains.system import test_system


def print_header():
    """Print test suite header."""
    print("\n" + "=" * 80)
    print(" " * 20 + "STRATEGYBUILDER COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test modules: {len(test_modules)}")
    print("=" * 80 + "\n")


def print_footer(results):
    """Print test suite footer with summary."""
    print("\n" + "=" * 80)
    print(" " * 30 + "FINAL RESULTS")
    print("=" * 80)

    total_domains = len(results)
    passed_domains = sum(1 for r in results if r['passed'])
    failed_domains = total_domains - passed_domains

    print(f"\nDomains tested: {total_domains}")
    print(f"Domains passed: {passed_domains}")
    print(f"Domains failed: {failed_domains}")
    print()

    # Show details for each domain
    for result in results:
        status = "✓ PASS" if result['passed'] else "✗ FAIL"
        print(f"  {status}  {result['name']}")

    print("\n" + "=" * 80)

    if failed_domains == 0:
        print("✓ ALL TESTS PASSED - System is ready!")
    else:
        print(f"✗ {failed_domains} domain(s) failed - Please review errors above")

    print("=" * 80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return failed_domains == 0


def run_all_tests():
    """Run all domain tests sequentially."""
    print_header()

    if not test_modules:
        print("✗ ERROR: No test modules were successfully imported!")
        print("  Please ensure test files are properly created in tests/domains/")
        return False

    results = []

    for domain_name, test_module in test_modules:
        print(f"\n{'─' * 80}")
        print(f"Running {domain_name} Tests...")
        print(f"{'─' * 80}")

        try:
            # Each test module has a run_tests() function that returns True/False
            passed = test_module.run_tests()
            results.append({
                'name': domain_name,
                'passed': passed
            })
        except Exception as e:
            print(f"\n✗ CRITICAL ERROR in {domain_name} tests: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'name': domain_name,
                'passed': False
            })

    # Print final summary
    all_passed = print_footer(results)
    return all_passed


def main():
    """Main entry point."""
    try:
        all_passed = run_all_tests()
        return 0 if all_passed else 1
    except KeyboardInterrupt:
        print("\n\n✗ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n✗ Unexpected error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
