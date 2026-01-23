# StrategyBuilder Test Suite

Comprehensive test suite organized by domain/endpoint.

## Structure

```
tests/
├── domains/
│   ├── strategies/
│   │   └── test_strategies.py       # GET /strategies, GET /strategies/{name}
│   ├── backtests/
│   │   └── test_backtests.py        # POST /backtest
│   ├── optimizations/
│   │   └── test_optimizations.py    # POST /optimize
│   ├── market_scans/
│   │   └── test_market_scans.py     # POST /market-scan
│   ├── run_history/
│   │   └── test_run_history.py      # GET /runs, GET /runs/{id}, POST /runs/{id}/replay
│   ├── presets/
│   │   └── test_presets.py          # /presets/* endpoints
│   ├── watchlists/
│   │   └── test_watchlists.py       # /watchlists/* endpoints
│   ├── portfolios/
│   │   └── test_portfolios.py       # /portfolios/* endpoints
│   ├── live_monitor/
│   │   └── test_live_monitor.py     # POST /live-monitor
│   ├── market_data/
│   │   └── test_market_data.py      # POST /market-data
│   └── system/
│       └── test_system.py           # GET /, GET /health
└── README.md
```

## Running Tests

### Run All Tests

Use the master test runner located in `src/shared/utils/`:

```bash
python src/shared/utils/test_everything.py
```

This will:
1. Run all domain tests sequentially
2. Provide comprehensive progress output
3. Generate a final summary report
4. Return exit code 0 if all pass, 1 if any fail

### Run Individual Domain Tests

Each domain test can be run independently:

```bash
# Test strategies endpoints
python tests/domains/strategies/test_strategies.py

# Test run history endpoints
python tests/domains/run_history/test_run_history.py

# Test market scans endpoint
python tests/domains/market_scans/test_market_scans.py

# Test presets endpoints
python tests/domains/presets/test_presets.py
```

## Test Structure

Each test file follows the same pattern:

```python
def test_imports():
    """Test that components can be imported."""
    pass

def test_config_loading():
    """Test that domain config loads correctly."""
    pass

def test_domain_specific():
    """Test domain-specific functionality."""
    pass

def run_tests():
    """Run all tests for this domain."""
    # Returns True if all tests pass, False otherwise
    pass

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
```

## Adding New Tests

To add tests for a new domain:

1. Create test file: `tests/domains/your_domain/test_your_domain.py`
2. Follow the pattern from existing test files
3. Add import to `src/shared/utils/test_everything.py`:
   ```python
   from tests.domains.your_domain import test_your_domain
   test_modules.append(('Your Domain', test_your_domain))
   ```

## Test Types

### Unit Tests
- Test individual functions and classes
- Use temporary databases for repository tests
- Mock external dependencies

### Integration Tests
- Test endpoint functionality
- Test database operations
- Test service layer integration

### Config Tests
- Verify all configs load correctly
- Verify config values are used properly

## CI/CD Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions
- name: Run tests
  run: python src/shared/utils/test_everything.py
```

Exit codes:
- `0`: All tests passed
- `1`: One or more tests failed
- `130`: Tests interrupted by user

## Dependencies

Tests require all project dependencies to be installed:
- backtrader
- pydantic
- fastapi
- pandas
- yfinance
- etc.

Install with:
```bash
pip install -r requirements.txt
```
