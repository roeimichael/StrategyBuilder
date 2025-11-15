# StrategyBuilder Pro - Testing Guide

## Quick Start

To run the comprehensive test suite and generate a beta release report:

```bash
python run_all_tests.py
```

This will:
1. Check your environment and dependencies
2. Run all 221 tests across all modules
3. Generate detailed reports (console, text file, JSON)
4. Provide a beta release checklist
5. Exit with status 0 if all tests pass, 1 if any fail

## Output Files

After running, you'll find:
- `test_report.txt` - Detailed text report
- `test_report.json` - Machine-readable JSON report

## Test Coverage

### Core Functionality (120+ tests)
- **Config Loader** (9 tests): Configuration loading and validation
- **Data Manager** (18 tests): Market data fetching, caching, cleaning
- **Performance Analyzer** (17 tests): Metrics calculation (Sharpe, Sortino, etc.)
- **Walk-Forward Optimizer** (21 tests): Time-series cross-validation
- **Strategy Ensemble** (10 tests): Multi-strategy voting and aggregation
- **Performance Regression** (9 tests): Vectorization speedup validation

### Risk Management (63 tests)
- **Risk Manager** (28 tests): Drawdown limits, portfolio heat, position sizing
- **Monte Carlo Simulator** (35 tests): Bootstrapping, stress testing, statistics

### Deployment & UI (56 tests)
- **Deployment Validation** (24 tests): Docker, reporting, notifications, charts
- **UI/UX** (32 tests): Tooltips, progress bars, status indicators

### API Integration (18 tests)
- **FastAPI Tests** (18 tests): REST API endpoints (skipped if FastAPI not installed)

## Test Status Categories

- ✅ **PASSED**: Test executed successfully
- ❌ **FAILED**: Assertion failed - needs fixing
- 💥 **ERROR**: Exception raised - needs debugging
- ⏭️ **SKIPPED**: Optional dependency not installed

## Understanding the Report

### Overall Statistics
```
Total Tests Run:     221
✅ Passed:           220 (99.5%)
❌ Failed:           0
💥 Errors:           0
⏭️  Skipped:          1
⏱️  Execution Time:   6.44s
```

### Module Breakdown
Shows results organized by test module (e.g., test_risk_manager, test_monte_carlo)

### Detailed Failures
If any tests fail, you'll see:
- Test name
- Full traceback
- Error message

### Beta Release Checklist
Automated checks for:
- All critical tests passing
- No import errors
- Environment validated
- Test coverage threshold met
- Documentation present
- Configuration files present

## Running Specific Tests

### Single Module
```bash
python -m unittest tests.test_risk_manager
```

### Single Test Class
```bash
python -m unittest tests.test_risk_manager.TestDrawdownLimits
```

### Single Test Method
```bash
python -m unittest tests.test_risk_manager.TestDrawdownLimits.test_max_drawdown_stops_trading
```

### With Verbose Output
```bash
python -m unittest tests.test_risk_manager -v
```

## Common Issues

### Skipped Tests

**FastAPI Tests (18 skipped)**
```bash
# Install FastAPI to run API tests
pip install -r requirements_api.txt
```

**PDF Report Tests (1 skipped)**
```bash
# Install reportlab for PDF generation
pip install reportlab
```

### Network Errors

Some tests download real market data. If you see SSL errors:
```
SSLError: TLS connect error
```

This is usually transient. The tests will still pass as they use cached data as fallback.

## Test Performance

Expected execution times:
- **Fast tests** (< 0.1s): Unit tests, calculations
- **Medium tests** (0.1-1s): Data operations, small backtests
- **Slow tests** (1-5s): Full backtests, parallel operations
- **Total runtime**: ~6-10 seconds

## Debugging Failed Tests

1. **Read the traceback** - Shows exactly where the failure occurred
2. **Check the assertion** - What was expected vs actual
3. **Run in isolation** - Single test with verbose output
4. **Add print statements** - See intermediate values
5. **Check dependencies** - Ensure all packages installed

## Coverage Analysis

To run with coverage reporting:
```bash
python -m coverage run run_all_tests.py
python -m coverage report
python -m coverage html
```

## Beta Release Criteria

For a successful beta release, ensure:
- ✅ All critical tests passing (0 failures, 0 errors)
- ✅ Pass rate > 95%
- ✅ All skipped tests are for optional dependencies only
- ✅ Execution time < 15 seconds
- ✅ No import errors
- ✅ All documentation present

## CI/CD Integration

The test runner returns appropriate exit codes:
- `0` - All tests passed
- `1` - Tests failed or errored

Use in CI/CD pipelines:
```yaml
# GitHub Actions example
- name: Run Tests
  run: python run_all_tests.py
```

## Questions?

If tests fail unexpectedly:
1. Check the detailed failure output
2. Review recent code changes
3. Verify dependencies are installed
4. Check Python version (requires 3.8+)
5. Ensure config files are present

---

**Last Updated**: 2025-11-15
**Test Suite Version**: 1.0.0
**Total Tests**: 221
