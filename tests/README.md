# StrategyBuilder Test Suite

Comprehensive testing suite for validating the StrategyBuilder backtesting platform.

## Test Structure

```
tests/
├── test_everything.py      # Master test runner - runs all tests
├── test_imports.py          # Import validation and module structure
├── test_indicators.py       # Custom indicator accuracy tests
├── test_strategies.py       # Strategy implementation validation
├── test_backtest.py         # Backtest API endpoint tests
├── test_optimization.py     # Optimization API endpoint tests
└── README.md               # This file
```

## Quick Start

### Run All Tests

```bash
# From project root
python tests/test_everything.py
```

This will run all test suites in sequence and provide a comprehensive summary.

### Run Individual Tests

```bash
# Import validation
python tests/test_imports.py

# Indicator accuracy
python tests/test_indicators.py

# Strategy validation
python tests/test_strategies.py

# Backtest endpoint (requires API server)
python tests/test_backtest.py

# Optimization endpoint (requires API server)
python tests/test_optimization.py
```

## Test Descriptions

### 1. test_imports.py - Import Validation
**Purpose:** Validates all module imports and __init__ files

**Tests:**
- Core module imports (strategy_skeleton, data_manager, optimizer)
- API module imports (main, models, requests, responses)
- Service module imports (strategy_service, backtest_service)
- Indicator module imports (OBV, MFI, CMF)
- Strategy module imports (all 12 strategies)
- Exception module imports
- Data module imports
- Config module imports
- __init__ exports validation
- Circular import detection

**Requirements:** None

**Expected Output:**
```
Total Tests: 50+
All imports validated successfully
```

### 2. test_indicators.py - Indicator Accuracy
**Purpose:** Tests custom indicator implementations for mathematical correctness

**Tests:**
- **OBV (On-Balance Volume)**
  - Calculation accuracy
  - Value range validation
  - Change detection
- **MFI (Money Flow Index)**
  - Valid range [0, 100]
  - No NaN/Inf values
  - Division by zero handling
- **CMF (Chaikin Money Flow)**
  - Valid range [-1, 1]
  - Oscillation validation
  - Edge case handling
- **Multi-Indicator Comparison**
  - All three indicators on same data

**Requirements:**
- Internet connection (downloads market data via yfinance)

**Expected Output:**
```
Total Tests: 4
All indicator tests passed
```

### 3. test_strategies.py - Strategy Validation
**Purpose:** Validates all strategy implementations can load and execute

**Tests:**
- **Strategy Loading**
  - All 12 strategies can be imported
- **Strategy Initialization**
  - Strategies initialize with parameters correctly
- **Strategy Execution**
  - Strategies can complete backtests
  - PnL calculations work
- **Parameter Definitions**
  - All strategies have proper params
- **Strategy Info Endpoint**
  - get_strategy_info() returns metadata
  - Optimizable parameters included
- **Short Position Support**
  - Detects which strategies support shorts
  - Calculates coverage percentage

**Requirements:**
- Internet connection (downloads market data via yfinance)

**Expected Output:**
```
Total Tests: 40+
All strategy tests passed
Short position coverage: 83%
```

### 4. test_backtest.py - Backtest Endpoint
**Purpose:** Tests the /backtest API endpoint functionality

**Tests:**
- **Basic Backtest**
  - Simple backtest with Bollinger Bands
  - Response structure validation
- **Chart Data Inclusion**
  - Backtest with chart data
  - Columnar format validation
- **Multiple Strategies**
  - Tests 4 different strategies
  - Validates all execute successfully
- **Invalid Input Handling**
  - Invalid ticker
  - Invalid strategy
  - Invalid date range
- **Performance Metrics**
  - All required metrics present
  - PnL, return_pct, sharpe_ratio, etc.

**Requirements:**
- API server running on localhost:8086
- Internet connection

**Expected Output:**
```
Total Tests: 15+
All tests passed
```

**Start API Server:**
```bash
python -m src.api.main
```

### 5. test_optimization.py - Optimization Endpoint
**Purpose:** Tests the /optimize API endpoint functionality

**Tests:**
- **Bollinger Bands Optimization**
  - Grid search over period and devfactor
  - Top 5 results validation
- **Williams R Optimization**
  - Grid search over period, oversold, overbought
  - 27 combinations tested
- **Strategy Info with Params**
  - get_strategy_info returns optimization metadata
  - Parameter definitions validated

**Requirements:**
- API server running on localhost:8086
- Internet connection

**Expected Output:**
```
Total Tests: 3
All tests completed
Top 5 results returned for each optimization
```

## Test Features

### Color-Coded Output
Tests use ANSI color codes for easy identification:
- 🟢 Green: Passed tests
- 🔴 Red: Failed tests
- 🟡 Yellow: Warnings

### Detailed Reporting
Each test provides:
- Individual test results
- Success/failure indicators
- Error messages for failures
- Performance metrics
- Summary statistics

### Exit Codes
All tests return proper exit codes:
- `0`: All tests passed
- `1`: One or more tests failed

## Common Issues

### API Server Not Running
**Error:** `Could not connect to API server`

**Solution:**
```bash
python -m src.api.main
```

### Import Errors
**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Make sure you're in project root
cd /path/to/StrategyBuilder

# Verify Python path
python -c "import sys; print(sys.path)"
```

### No Market Data
**Error:** `No data found for ticker`

**Solution:**
- Check internet connection
- Try a different ticker symbol
- Check if market is open (for real-time data)

## Performance Benchmarks

Expected test durations on typical hardware:

| Test | Duration | Notes |
|------|----------|-------|
| test_imports.py | ~5s | Fast, no network |
| test_indicators.py | ~30s | Downloads market data |
| test_strategies.py | ~60s | Multiple backtests |
| test_backtest.py | ~45s | API calls + backtests |
| test_optimization.py | ~90s | Grid search computations |
| **Total** | **~4 min** | Full suite |

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests without API server (subset)
python tests/test_imports.py && \
python tests/test_indicators.py && \
python tests/test_strategies.py

# Run full suite with API
python -m src.api.main &
API_PID=$!
sleep 5
python tests/test_everything.py
kill $API_PID
```

## Adding New Tests

To add a new test file:

1. Create `tests/test_newfeature.py`
2. Follow the tester class pattern:
   ```python
   class NewFeatureTester:
       def __init__(self):
           self.passed = 0
           self.failed = 0
           self.errors = []
   ```
3. Add test methods
4. Add to `test_everything.py` tests list
5. Update this README

## Code Coverage

To check code coverage:

```bash
pip install coverage
coverage run -m pytest tests/
coverage report
coverage html  # Generate HTML report
```

## Test Data

- Market data downloaded via yfinance
- Test tickers: AAPL, BTC-USD, ETH-USD
- Typical date range: Last 90 days
- All tests use standardized data to ensure consistency

## Support

If tests fail unexpectedly:

1. Check all dependencies installed: `pip install -r requirements.txt`
2. Verify Python version: `python --version` (3.8+)
3. Clear cache: `rm -rf __pycache__ src/__pycache__`
4. Check logs for detailed error messages
5. Run individual tests to isolate issues

## License

Same as main project.
