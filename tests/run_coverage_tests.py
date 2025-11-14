"""Run all tests with coverage measurement"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_tests_with_coverage():
    """Run all unit tests and measure code coverage"""
    try:
        import coverage
    except ImportError:
        print("Coverage module not installed. Install with: pip install coverage")
        print("Running tests without coverage...")
        run_tests_without_coverage()
        return

    cov = coverage.Coverage(source=['src/core', 'src/utils'])
    cov.start()

    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()

    print("\n" + "="*70)
    print("COVERAGE REPORT")
    print("="*70)
    cov.report()

    print("\n" + "="*70)
    print("DETAILED COVERAGE BY FILE")
    print("="*70)

    cov_data = cov.get_data()
    total_statements = 0
    total_executed = 0

    for filename in cov_data.measured_files():
        if 'test_' not in filename:
            analysis = cov.analysis2(filename)
            statements = len(analysis[1])
            executed = len(analysis[1]) - len(analysis[3])

            total_statements += statements
            total_executed += executed

            coverage_pct = (executed / statements * 100) if statements > 0 else 0

            print(f"{os.path.basename(filename)}: {coverage_pct:.1f}% ({executed}/{statements} statements)")

    overall_coverage = (total_executed / total_statements * 100) if total_statements > 0 else 0

    print("="*70)
    print(f"OVERALL COVERAGE: {overall_coverage:.1f}% ({total_executed}/{total_statements} statements)")
    print("="*70)

    if overall_coverage >= 80:
        print("\nSUCCESS: Coverage requirement met (80%+)")
    else:
        print(f"\nWARNING: Coverage below 80% target (current: {overall_coverage:.1f}%)")

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\nALL TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")

    return result.wasSuccessful() and overall_coverage >= 80


def run_tests_without_coverage():
    """Run tests without coverage measurement"""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\nALL TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests_with_coverage()
    sys.exit(0 if success else 1)
