# Tests Folder Structure

## Purpose
Comprehensive test suite validating backtesting platform functionality including API endpoints, strategy implementations, indicators, imports, and performance correctness across multiple scenarios.

## Test Organization

**Root Level Tests** (`/tests/`)
- API endpoint integration tests (backtest, optimization, presets, snapshot)
- Import validation and module structure tests
- Indicator accuracy verification tests
- Strategy loading and execution tests
- Master test runner orchestrating all suites

**Strategy Correctness Tests** (`/tests/strategies/`)
- Bollinger Bands strategy correctness validation
- Williams %R strategy correctness validation

**Test Data** (`/tests/data/`)
- Supporting data files for test scenarios

## Root Level Test Files

### test_backtest.py

**Purpose:** Integration tests for backtest API endpoint validation

**Test Class:** BacktestTester

**Test Methods:**
- test_basic_backtest(): Validates basic backtest execution with Bollinger Bands strategy on AAPL stock
- test_backtest_with_chart_data(): Tests backtest response including chart data in columnar format with Williams %R strategy on BTC-USD
- test_multiple_strategies(): Validates multiple strategy types (RSI Stochastic, MFI, Keltner Channel, TEMA MACD) execute correctly on ETH-USD
- test_invalid_inputs(): Error handling validation for invalid ticker, invalid strategy name, and invalid date range
- test_performance_metrics(): Validates presence of all required performance metrics (PnL, return%, Sharpe, max drawdown, trades, portfolio values)
- print_summary(): Test suite summary with pass/fail counts and error details

**Configuration:**
- API Base URL: http://localhost:8086
- Requires running FastAPI server
- Tests execute real HTTP requests against local API
- Validates response structure, status codes, and field presence

**Test Coverage:**
- 5 test scenarios covering happy path, chart data inclusion, multi-strategy execution, error handling, and metrics validation
- Validates HTTP 200 for success, 400 for validation errors, 404 for not found
- Tests both traditional stocks (AAPL) and cryptocurrencies (BTC-USD, ETH-USD)

### test_optimization.py

**Purpose:** Integration tests for strategy optimization endpoint

**Test Functions:**
- test_optimize_bollinger(): Tests Bollinger Bands parameter optimization with period=[15,20,25] and devfactor=[1.5,2.0,2.5] on BTC-USD
- test_optimize_williams(): Tests Williams %R parameter optimization with period, oversold, overbought ranges on ETH-USD
- test_get_strategy_with_params(): Validates strategy info endpoint returns optimizable parameters with type, default, min/max range, step, description

**Configuration:**
- API Base URL: http://localhost:8086
- Tests grid search optimization across parameter combinations
- Validates top results ranked by performance metrics

**Test Coverage:**
- Parameter grid optimization validation
- Strategy metadata retrieval
- Top results sorting and formatting

### test_presets.py

**Purpose:** Integration tests for strategy preset management API

**Test Class:** PresetTester

**Test Methods:**
- test_create_preset(): Creates new preset with RSI Stochastic strategy for AAPL with full parameter set
- test_create_duplicate_preset(): Validates duplicate preset rejection with HTTP 409 Conflict
- test_list_presets(): Lists all presets with pagination support
- test_list_presets_filtered(): Tests preset filtering by ticker and strategy name
- test_backtest_from_preset(): Executes backtest using saved preset configuration
- test_delete_preset(): Deletes preset by ID and validates removal
- test_invalid_strategy(): Validates HTTP 404 for nonexistent strategy reference
- print_summary(): Test suite summary with pass/fail counts

**Configuration:**
- API Base URL: http://localhost:8086
- Tests full CRUD lifecycle for presets
- Validates unique constraint enforcement on (name, strategy, ticker)

**Test Coverage:**
- 7 test scenarios covering creation, duplication prevention, listing, filtering, execution, deletion, validation
- Tests database persistence and retrieval
- Validates foreign key relationships and constraints

### test_snapshot.py

**Purpose:** Integration tests for live snapshot endpoint providing near-real-time strategy state

**Test Class:** SnapshotTester

**Test Methods:**
- test_api_health(): Validates API server connectivity before running tests
- test_basic_snapshot(): Tests basic snapshot request with Bollinger Bands on AAPL, validates required fields (success, ticker, strategy, last_bar, indicators, position_state, recent_trades, portfolio_value, cash, timestamp)
- test_snapshot_with_different_lookbacks(): Tests snapshot with varying lookback periods (50, 100, 200 bars) to validate historical data retrieval
- test_snapshot_invalid_inputs(): Error handling for invalid ticker and invalid strategy name
- test_snapshot_multiple_strategies(): Validates snapshot works across Bollinger Bands, RSI Stochastic, and MFI strategies
- test_snapshot_performance(): Measures snapshot response time and validates acceptable performance (< 10 seconds)
- print_summary(): Test suite summary with pass/fail counts

**Configuration:**
- API Base URL: http://localhost:8086
- Tests real-time strategy state retrieval
- Validates indicator values, position tracking, trade history

**Test Coverage:**
- 6 test scenarios covering basic functionality, lookback variations, error handling, multi-strategy support, and performance
- Validates indicator calculation and position state tracking
- Tests performance constraints for production readiness

### test_imports.py

**Purpose:** Module import validation ensuring all project components load correctly

**Test Class:** ImportTester

**Test Methods:**
- test_core_modules(): Imports core backtesting components (strategy_skeleton, data_manager, optimizer, strategy_optimization_config)
- test_api_modules(): Imports API layer (main, models, requests, responses)
- test_service_modules(): Imports service layer (strategy_service, backtest_service)
- test_indicator_modules(): Imports custom indicators (OBV, MFI, CMF)
- test_strategy_modules(): Dynamically imports all strategy files from src/strategies directory
- test_exception_modules(): Imports exception hierarchy (base, data_errors, strategy_errors)
- test_data_modules(): Imports data persistence layer (repositories)
- test_config_modules(): Imports configuration modules (constants, backtest_config)
- test_init_exports(): Validates __init__.py __all__ exports for src, src.api.models, src.exceptions
- test_circular_imports(): Tests simultaneous imports to detect circular dependencies
- print_summary(): Test suite summary

**Configuration:**
- Adds project root to sys.path for import resolution
- Uses importlib for dynamic module loading
- Tests both explicit imports and __all__ exports

**Test Coverage:**
- 10 test categories covering all project layers
- Dynamic strategy discovery and loading
- Circular dependency detection
- Export validation for public APIs

### test_indicators.py

**Purpose:** Custom indicator accuracy and calculation validation

**Test Class:** IndicatorTester

**Test Methods:**
- test_obv_indicator(): Tests On-Balance Volume (OBV) calculation on AAPL with 90 days data, validates value changes and accumulation logic
- test_mfi_indicator(): Tests Money Flow Index (MFI) calculation on BTC-USD, validates range [0, 100], checks for NaN/Inf values
- test_cmf_indicator(): Tests Chaikin Money Flow (CMF) calculation on ETH-USD, validates range [-1, 1], checks oscillation between positive/negative
- test_indicator_comparison(): Tests all three indicators simultaneously on same data to validate concurrent calculation
- print_summary(): Test suite summary

**Configuration:**
- Downloads live market data via yfinance
- Creates Backtrader cerebro instances for indicator testing
- Uses 60-90 day lookback periods for sufficient indicator warmup

**Indicator Testing Methodology:**
- OBV: Validates accumulation/distribution tracking via volume
- MFI: Validates 14-period money flow oscillator stays within bounds
- CMF: Validates 20-period Chaikin flow oscillates correctly

**Test Coverage:**
- 4 test scenarios covering individual indicators and combined execution
- Validates mathematical correctness and boundary conditions
- Tests real market data processing

### test_strategies.py

**Purpose:** Strategy loading, initialization, execution, and metadata validation

**Test Class:** StrategyTester

**Test Methods:**
- test_strategy_loading(): Loads all strategy classes from src/strategies directory dynamically
- test_strategy_initialization(): Initializes strategies with parameters using Backtrader cerebro
- test_strategy_execution(): Executes full backtests on AAPL with 400-day history for strategies requiring long indicators (EMA 200)
- test_strategy_parameters(): Validates strategy parameter definitions via Backtrader params attribute
- test_strategy_info_endpoint(): Retrieves strategy metadata including optimizable parameters with ranges
- test_short_position_support(): Detects which strategies support short selling by analyzing source code for self.position_type and self.sell() calls
- print_summary(): Test suite summary

**Configuration:**
- Uses yfinance for 400-day AAPL historical data
- Initializes StrategyService and DataManager
- Tests strategies: Bollinger Bands, Williams %R, RSI Stochastic, MFI, Keltner Channel, TEMA MACD, Alligator

**Strategy Analysis:**
- Dynamic discovery via glob pattern `src/strategies/*.py`
- Parameter introspection via Backtrader params
- Short position detection via source code analysis
- Optimizable parameter metadata extraction

**Test Coverage:**
- 6 test categories covering loading, initialization, execution, parameters, metadata, short support
- Tests both long-only and long/short strategies
- Validates strategy completeness and correctness

### test_everything.py

**Purpose:** Master test runner executing all test suites with comprehensive reporting

**Test Class:** TestRunner

**Supporting Classes:**
- Color: ANSI color codes for terminal output formatting

**Test Methods:**
- print_header(): Displays test suite header with timestamp
- run_test(test_name, test_file, needs_api): Executes individual test file as subprocess, captures output, determines pass/fail, tracks duration
- print_summary(): Displays final results table with per-test status, statistics, success rate

**Test Execution Features:**
- Subprocess isolation: Each test runs in separate process
- Timeout protection: 5-minute timeout per test prevents hanging
- Output capture: Captures both stdout and stderr
- Return code validation: Uses exit codes to determine pass/fail
- Duration tracking: Measures and reports execution time per test
- API dependency detection: Skips API-dependent tests if server not running

**Helper Functions:**
- check_api_server(): Validates API server availability on localhost:8086

**Test Suite Configuration:**
Currently Active Tests:
- Strategy Validation (test_strategies.py): Tests all strategy implementations
- Williams %R Correctness (strategies/test_williams_r_strategy.py): Controlled scenario testing
- Bollinger Bands Correctness (strategies/test_bollinger_bands_strategy.py): Controlled scenario testing

Commented Out (Previously Passed):
- Import Validation (test_imports.py): Module import verification
- Indicator Accuracy (test_indicators.py): Custom indicator testing
- Backtest Endpoint (test_backtest.py): API integration testing
- Optimization Endpoint (test_optimization.py): Parameter optimization testing
- Preset Management (test_presets.py): Preset CRUD testing
- Snapshot Endpoint (test_snapshot.py): Live data snapshot testing

**Reporting:**
- Individual test results with status and duration
- Aggregate statistics: total tests, passed count, failed count, total duration, average time
- Color-coded output: Green for passed, Red for failed, Yellow for warnings
- Success rate percentage calculation

**Test Coverage:**
- Orchestrates execution of 9 distinct test suites
- Handles API-dependent vs standalone tests differently
- Provides comprehensive final report

## Strategy Correctness Tests Subfolder

### strategies/test_bollinger_bands_strategy.py

**Purpose:** Strategy correctness validation using controlled, deterministic price data

**Test Class:** TestBollingerBandsStrategy

**Pattern Generators:**
- create_downward_spike_pattern(): Generates stable→drop→recovery→stable pattern to test lower band cross (long entry) and middle band cross (long exit)
- create_upward_spike_pattern(): Generates stable→spike→drop→stable pattern to test upper band cross (short entry) and middle band cross (short exit)
- create_v_shaped_pattern(): Generates drop then spike pattern to test both long and short cycles in single dataset
- create_stable_pattern(): Generates tight range data to validate no false signals

**Test Methods:**
- test_lower_band_cross_triggers_long(): Validates crossing below lower band triggers long entry, checks entry price in expected range (65-85)
- test_middle_band_cross_exits_long(): Validates crossing above middle band exits long position, verifies exit price > entry price for profitability
- test_upper_band_cross_triggers_short(): Validates crossing above upper band triggers short entry, checks entry price range (115-135)
- test_v_shaped_pattern(): Tests both long and short trade cycles in V-shaped price movement
- test_no_trades_in_stable_range(): Validates strategy avoids false signals when price stays within tight range, expects 0-1 trades
- print_summary(): Test results with pass/fail counts

**Strategy Configuration:**
- Bollinger Bands parameters: period=20, devfactor=2
- Position sizing: 95% of capital
- Initial cash: $10,000
- Uses Backtrader PercentSizer

**Test Methodology:**
- Deterministic price patterns with numpy random noise
- 50-60 bar datasets with clear signal zones
- Validates entry timing, exit timing, and position direction
- Checks price ranges rather than exact values (accounts for noise)

**Validation Approach:**
- Behavioral testing: Verifies strategy reacts correctly to price patterns
- No look-ahead bias: Ensures signals only trigger after complete bar
- Entry/exit logic: Validates both long and short position management
- False signal prevention: Tests stable periods produce minimal trades

**Test Coverage:**
- 5 test scenarios covering long entry, long exit, short entry, combined cycles, stable periods
- Validates strategy supports both long and short positions
- Tests mean reversion behavior at band extremes

### strategies/test_williams_r_strategy.py

**Purpose:** Williams %R strategy correctness validation with controlled price scenarios

**Test Class:** TestWilliamsRStrategy

**Pattern Generators:**
- create_oversold_overbought_cycle(): Generates 100→50→150→180→50 pattern creating oversold (long entry)→overbought (long exit/short entry)→oversold (short exit) cycle
- create_oscillating_pattern(): Generates sine wave pattern (40-160 range) testing multiple entry/exit cycles

**Test Methods:**
- test_oversold_triggers_long(): Validates oversold condition (Williams %R < -80) triggers long entry during drop to 50
- test_overbought_exits_long(): Validates overbought condition (Williams %R > -20) exits long position during rise to 150
- test_overbought_triggers_short(): Validates overbought condition triggers short entry during spike to 180
- test_no_premature_signals(): Validates no trades occur before 14-bar period completion (prevents look-ahead bias)
- test_oscillating_pattern(): Tests multiple trade cycles with continuous oscillation, validates both long and short trades
- print_summary(): Test results summary

**Strategy Configuration:**
- Williams %R parameters: period=14, oversold=-80, overbought=-20
- Position sizing: 95% of capital
- Initial cash: $10,000

**Test Methodology:**
- 50-60 bar deterministic datasets with clear oversold/overbought zones
- Validates indicator calculation period requirements
- Tests oscillator range behavior (-100 to 0)
- Verifies entry/exit signal timing

**Validation Approach:**
- Oversold/overbought detection: Validates threshold crossings trigger correct actions
- Period warmup: Ensures indicator waits for sufficient data before signaling
- Cycle testing: Validates strategy handles repeated entry/exit cycles
- Position direction: Verifies both long and short position support

**Test Coverage:**
- 5 test scenarios covering oversold entry, overbought exit, short entry, premature signal prevention, oscillation cycles
- Tests mean reversion behavior at extremes
- Validates Williams %R specific logic

## Common Test Patterns

**API Integration Tests:**
- Base URL configuration: http://localhost:8086
- Health check before execution
- HTTP request/response validation
- Status code verification (200, 400, 404, 409)
- JSON response structure validation
- Error message validation

**Strategy Tests:**
- Backtrader cerebro initialization
- PandasData feed creation from DataFrames
- Strategy class loading and parameter injection
- Broker configuration (cash, commission)
- Result extraction and validation
- Trade list analysis

**Indicator Tests:**
- yfinance data download
- Multi-level column handling
- Backtrader integration
- Value range validation
- NaN/Inf detection
- Concurrent indicator calculation

**Test Result Reporting:**
- Pass/fail counters
- Error message collection
- Summary statistics
- Print-based console output for visibility
- Exit codes (0 for success, 1 for failure)

## Test Execution

**Individual Test Execution:**
```bash
python tests/test_backtest.py
python tests/test_optimization.py
python tests/test_presets.py
python tests/test_snapshot.py
python tests/test_indicators.py
python tests/test_imports.py
python tests/test_strategies.py
python tests/strategies/test_bollinger_bands_strategy.py
python tests/strategies/test_williams_r_strategy.py
```

**Master Test Runner:**
```bash
python tests/test_everything.py
```

**Prerequisites:**
- API-dependent tests require: `python -m src.api.main` running on port 8086
- All tests require project root in Python path
- Market data tests require internet connectivity for yfinance

## Test Data Requirements

**Market Data:**
- yfinance: Real-time and historical stock/crypto data
- Tickers used: AAPL, BTC-USD, ETH-USD
- Date ranges: Typically 60-400 days for sufficient indicator history
- Intervals: Primarily 1d (daily), some tests use intraday

**Synthetic Data:**
- Deterministic price patterns for correctness testing
- Numpy-generated OHLC data with controlled noise
- Pandas DataFrames with datetime index
- Volume data (constant 1,000,000 for simplicity)

## Dependencies

**Core Testing Libraries:**
- requests: HTTP client for API integration tests
- backtrader: Backtesting framework for strategy execution
- yfinance: Market data provider
- pandas: Data manipulation and DataFrame handling
- numpy: Numerical operations and synthetic data generation

**Standard Library:**
- sys: Path manipulation for imports
- os: File system operations
- pathlib: Modern path handling
- datetime/timedelta: Date manipulation
- json: JSON parsing
- importlib: Dynamic module importing
- subprocess: Test execution in isolation
- time: Duration tracking

**Project Dependencies:**
- src.strategies.*: Strategy implementations
- src.services.*: Business logic services
- src.core.*: Core backtesting engine
- src.api.*: API layer and models
- src.indicators.*: Custom technical indicators
- src.data.*: Data persistence repositories
- src.config.*: Configuration management
- src.exceptions.*: Exception hierarchy

## Test Categories

**Unit Tests:**
- Import validation (test_imports.py)
- Indicator accuracy (test_indicators.py)

**Integration Tests:**
- API endpoint testing (test_backtest.py, test_optimization.py, test_presets.py, test_snapshot.py)
- Strategy loading and execution (test_strategies.py)

**Behavioral Tests:**
- Strategy correctness (strategies/test_bollinger_bands_strategy.py, strategies/test_williams_r_strategy.py)

**End-to-End Tests:**
- Master test runner (test_everything.py) orchestrating full suite

## Test Metrics

**Code Coverage Areas:**
- API endpoints: 100% of public endpoints tested
- Strategies: All strategies loaded, subset tested for execution and correctness
- Indicators: Custom indicators (OBV, MFI, CMF) validated
- Data layer: CRUD operations tested via presets
- Error handling: Invalid inputs validated across endpoints

**Performance Benchmarks:**
- Snapshot response time: < 10 seconds expected
- Individual test timeout: 5 minutes maximum
- Full suite execution: Variable based on market data download speed

## Notes

**Test Output:**
All tests use print statements for output rather than logging framework. This is intentional for test visibility and compatibility with test runners that capture stdout/stderr.

**Test Isolation:**
Master test runner executes each test suite in separate subprocess to prevent cross-contamination and state leakage.

**API Dependency Management:**
Tests requiring API server check connectivity and skip gracefully if server unavailable. This allows core tests (imports, indicators, strategy correctness) to run independently.

**Market Data Volatility:**
Tests using real market data may have variable results based on market conditions and data availability. Correctness tests use synthetic deterministic data to ensure reproducible results.

**Test Maintenance:**
Some passing tests commented out in master runner to focus on specific failing scenarios during development. Uncomment after fixes verified.
