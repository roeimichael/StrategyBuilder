# Logging Guidelines

## Overview

This document defines logging standards and conventions for the StrategyBuilder project. Consistent logging helps with debugging, monitoring, and maintaining code quality.

## Logging Levels

Use appropriate logging levels for different scenarios:

### INFO
- Normal application flow
- Successful operations
- Configuration information
- Startup/shutdown messages

**Example:**
```python
logger.info(f"Strategy module '{strategy_name}' loaded successfully")
logger.info("API server started on port 8086")
```

### WARNING
- Recoverable errors
- Deprecated features
- Missing optional data
- Unusual but not critical conditions

**Example:**
```python
logger.warning(f"No valid strategy class found in {strategy_name}")
logger.warning("Using default parameters as none were provided")
```

### ERROR
- Failed operations that need attention
- Unexpected exceptions
- Data validation failures

**Example:**
```python
logger.error(f"Error loading strategy: {str(e)}")
logger.error("Database connection failed")
```

### DEBUG
- Detailed diagnostic information
- Variable values during execution
- Internal state changes

**Example:**
```python
logger.debug(f"Processing request with parameters: {params}")
logger.debug(f"Retrieved {len(results)} results from database")
```

## Where to Use Logging

### DO Use Logging

1. **Service Layer** (`src/services/`)
   - Strategy loading
   - Backtest execution
   - Data fetching

2. **Data Layer** (`src/data/`)
   - Database operations
   - Cache hits/misses
   - Repository operations

3. **API Layer** (`src/api/`)
   - Request/response logging (via `@log_errors`)
   - Validation errors
   - Authentication events

4. **Core Business Logic** (`src/core/`)
   - Optimization progress
   - Data manager operations
   - Critical calculations

### DO NOT Use Logging

1. **Strategy `next()` Methods**
   - Use `self.log()` for debugging (disabled by default)
   - Avoid logger calls in hot path

2. **Indicators** (`src/indicators/`)
   - No logging in calculation methods
   - Performance-critical code

3. **Models** (`src/api/models/`)
   - Pydantic models should not log
   - Keep models pure data structures

## Setup Logging in Modules

### Standard Module-Level Logger

```python
import logging

logger = logging.getLogger(__name__)

class MyService:
    def my_method(self):
        logger.info("Operation started")
        try:
            # ... do work ...
            logger.info("Operation completed successfully")
        except Exception as e:
            logger.error(f"Operation failed: {str(e)}")
            raise
```

### API Error Logging

API endpoints use `@log_errors` decorator which:
- Logs 400-499 errors at INFO level (expected validation errors)
- Logs 500+ errors at ERROR level with full stack trace
- Suppresses yfinance errors (too noisy)

```python
from src.utils.api_logger import log_errors

@app.post("/endpoint")
@log_errors
def my_endpoint():
    # Errors are automatically logged
    pass
```

## What NOT to Log

### Avoid Print Statements

**NEVER use `print()` in `src/` directory:**

```python
# BAD
print(f"Strategy loaded: {name}")

# GOOD
logger.info(f"Strategy loaded: {name}")
```

### No Emojis

Keep logs machine-readable and professional:

```python
# BAD
logger.info("Success! 🎉")

# GOOD
logger.info("Operation completed successfully")
```

### No Sensitive Data

Never log:
- API keys
- Passwords
- User credentials
- Personal information
- Financial account numbers

### Avoid Excessive Logging

Don't log in tight loops or high-frequency operations:

```python
# BAD - Logs thousands of times
for i in range(10000):
    logger.info(f"Processing item {i}")

# GOOD - Log summary
logger.info(f"Processing {len(items)} items")
# ... process items ...
logger.info("Processing complete")
```

## Test File Logging

Test files (`tests/`) may use print statements for output, but should:
- Use clear prefixes: `[OK]`, `[FAIL]`, `[WARN]`
- No Unicode characters (for Windows compatibility)
- Keep output concise and actionable

```python
# Test files only
print("[OK] Test passed")
print("[FAIL] Test failed: {error}")
```

## Strategy Debugging

Strategies inherit `self.log()` from `Strategy_skeleton`:

```python
class MyStrategy(Strategy_skeleton):
    def next(self):
        # This is a no-op by default (pass)
        # Can be enabled for debugging
        self.log(f'Close: {self.data.close[0]}')
```

The `log()` method is disabled by default for performance. Override it only when debugging specific strategies.

## Log Output Configuration

Logging is configured in `src/utils/api_logger.py`:

- **Level**: INFO
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Handlers**:
  - File: `logs/api_errors.log`
  - Console: stdout
- **Suppressions**:
  - yfinance errors (set to CRITICAL)

## Best Practices Summary

1. ✅ Use module-level `logger = logging.getLogger(__name__)`
2. ✅ Choose appropriate log levels (INFO, WARNING, ERROR, DEBUG)
3. ✅ Include context in log messages
4. ✅ Log exceptions with traceback
5. ❌ Never use `print()` in `src/`
6. ❌ No emojis in logs
7. ❌ Don't log in performance-critical paths
8. ❌ Don't log sensitive data

## Examples

### Good Logging

```python
import logging

logger = logging.getLogger(__name__)

class BacktestService:
    def run_backtest(self, request):
        logger.info(f"Starting backtest for {request.ticker} with {request.strategy}")

        try:
            results = self._execute(request)
            logger.info(f"Backtest completed: PnL=${results.pnl:.2f}")
            return results
        except ValueError as e:
            logger.warning(f"Invalid input: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Backtest failed: {str(e)}", exc_info=True)
            raise
```

### Bad Logging

```python
# DON'T DO THIS
import logging

logger = logging.getLogger(__name__)

class BacktestService:
    def run_backtest(self, request):
        print("Starting backtest 🚀")  # BAD: print + emoji

        logger.debug(request)  # BAD: logs entire object

        for i in range(1000):
            logger.info(f"Bar {i}")  # BAD: excessive logging

        logger.info(f"User API key: {secret_key}")  # BAD: sensitive data
```

## Migration Checklist

When updating existing code:

- [ ] Replace all `print()` with `logger.*()` in `src/`
- [ ] Add `import logging` and module logger
- [ ] Remove emojis from log messages
- [ ] Choose appropriate log level
- [ ] Add context to log messages
- [ ] Test that logs appear correctly
- [ ] Verify no performance impact

## References

- Python Logging: https://docs.python.org/3/library/logging.html
- API Logger: `src/utils/api_logger.py`
- Strategy Skeleton: `src/core/strategy_skeleton.py`
