# Utils Folder Structure

## Purpose
Utility layer providing logging infrastructure and performance analysis capabilities for backtesting operations.

## Components

### Package Exports (__init__.py)

**Exported Classes and Functions:**
- PerformanceAnalyzer: trading performance metrics calculator
- log_errors: decorator for comprehensive error logging
- logger: configured logger instance for application-wide use

### API Logger (api_logger.py)

**Purpose:** Centralized logging infrastructure with error tracking decorator for API endpoints and application components.

**Configuration:**

*Log Directory:* `{project_root}/logs/`

*Log File:* `api_errors.log`

*Log Level:* INFO

*Format:* `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

*Handlers:*
- FileHandler: Persists logs to api_errors.log
- StreamHandler: Outputs logs to console

*Logger Instance:* `StrategyBuilder.API`

*External Logger Suppression:* yfinance logger set to CRITICAL level to reduce noise from invalid ticker queries

**Exported Functions:**

*log_errors(func: Callable) -> Callable*
Decorator providing comprehensive error logging for both synchronous and asynchronous functions. Automatically detects function type using asyncio.iscoroutinefunction and returns appropriate wrapper.

**Async Wrapper Behavior:**
- HTTPException with 400-499 status codes: Logs at INFO level with compact format (function name, status code, detail message) - considered expected validation errors
- HTTPException with 500+ status codes: Logs at ERROR level with full structured format including timestamp, function metadata, arguments, keyword arguments, and full traceback - considered unexpected server errors
- Generic Exception: Logs at ERROR level with full structured format including error type, message, function context, and complete traceback
- All exceptions re-raised after logging for upstream handling

**Sync Wrapper Behavior:**
Identical error handling and logging strategy to async wrapper but wraps synchronous functions.

**Error Log Format (ERROR level):**
```
================================================================================
ERROR TIMESTAMP: {ISO 8601 timestamp}
FUNCTION: {function name}
MODULE: {module path}
ERROR TYPE: {exception class name or HTTPException status code}
ERROR MESSAGE: {error detail or string representation}

ARGUMENTS:
{positional arguments tuple}

KEYWORD ARGUMENTS:
{keyword arguments dictionary}

FULL TRACEBACK:
{complete stack trace}
================================================================================
```

**Usage Pattern:**
Applied as decorator to FastAPI endpoint functions and business logic methods requiring error visibility. Supports both sync and async functions transparently.

*logger: logging.Logger*
Pre-configured logger instance for direct use throughout application. Useful for informational logging, warnings, and debug messages outside error handling decorator.

**Dependencies:**
- logging: standard library logging framework
- traceback: stack trace extraction
- functools: wrapper preservation with @wraps
- asyncio: coroutine function detection
- datetime: timestamp generation
- typing: type hints (Callable, Any)
- pathlib: cross-platform path handling
- fastapi: HTTPException type

### Performance Analyzer (performance_analyzer.py)

**Purpose:** Calculates comprehensive trading performance metrics from backtest execution results.

**PerformanceAnalyzer Class:**

**Constructor Parameters:**
- trades: List[Dict[str, Any]] - Trade records with pnl, entry_date, exit_date
- start_value: float - Initial portfolio value
- end_value: float - Final portfolio value
- equity_curve: Optional[pd.Series] - Time series of portfolio values (nullable)

**Instance Attributes:**
- self.trades: trade history list
- self.start_value: initial capital
- self.end_value: final capital
- self.equity_curve: equity time series (may be None)

**Public Methods:**

*calculate_all_metrics() -> Dict[str, Any]*
Computes all available performance metrics in single call. Returns dictionary with keys: win_rate, profit_factor, payoff_ratio, calmar_ratio, sortino_ratio, max_consecutive_wins, max_consecutive_losses, avg_win, avg_loss, largest_win, largest_loss, avg_trade_duration, recovery_periods, expectancy. Returns empty metrics dictionary if no trades.

*calculate_win_rate() -> float*
Percentage of profitable trades. Returns 0.0 if no trades. Formula: (winning_trades / total_trades) * 100.

*calculate_profit_factor() -> Optional[float]*
Ratio of gross profit to gross loss. Returns None if no trades, zero gross loss, or zero gross profit. Formula: gross_profit / gross_loss.

*calculate_payoff_ratio() -> Optional[float]*
Ratio of average win to average loss. Returns None if either value is zero. Formula: avg_win / avg_loss.

*calculate_calmar_ratio() -> Optional[float]*
Risk-adjusted return metric comparing annualized return to maximum drawdown. Returns None if no trades, no equity curve, or zero max drawdown. Formula: annual_return / abs(max_drawdown).

*calculate_sortino_ratio(risk_free_rate: float = 0.0) -> Optional[float]*
Downside risk-adjusted return metric. Uses downside deviation instead of standard deviation. Returns None if no equity curve or no downside returns. Formula: mean(excess_returns) / downside_deviation. Downside deviation computed from returns below zero.

*calculate_max_consecutive_wins() -> int*
Longest streak of consecutive profitable trades. Returns 0 if no trades.

*calculate_max_consecutive_losses() -> int*
Longest streak of consecutive losing trades. Returns 0 if no trades.

*calculate_avg_win() -> float*
Average profit per winning trade. Returns 0.0 if no winning trades.

*calculate_avg_loss() -> float*
Average loss per losing trade (negative value). Returns 0.0 if no losing trades.

*calculate_largest_win() -> float*
Maximum single trade profit. Returns 0.0 if no winning trades.

*calculate_largest_loss() -> float*
Maximum single trade loss (negative value). Returns 0.0 if no losing trades.

*calculate_avg_trade_duration() -> Optional[float]*
Average holding period in days. Returns None if no trades with valid dates. Parses string dates in '%Y-%m-%d' format if necessary.

*calculate_recovery_periods() -> List[Dict[str, Any]]*
Identifies all drawdown recovery cycles. Returns list of dictionaries with keys: drawdown_start_idx, recovery_idx, recovery_days, drawdown_pct. Returns empty list if no equity curve. Tracks peak equity and records recovery when new peak reached.

*calculate_expectancy() -> float*
Expected profit per trade. Returns 0.0 if no trades. Formula: (win_rate * avg_win) - ((1 - win_rate) * avg_loss). Positive expectancy indicates profitable strategy over long term.

**Private Methods:**

*_calculate_annual_return() -> float*
Computes annualized return percentage using compound annual growth rate formula. Extracts date range from first and last trades. Returns 0.0 if insufficient data. Formula: ((1 + total_return) ** (1 / years) - 1) * 100. Uses 365.25 days per year for leap year adjustment.

*_calculate_max_drawdown() -> float*
Maximum peak-to-trough decline percentage in equity curve. Tracks running peak and computes drawdown at each point. Returns 0.0 if no equity curve. Formula: ((peak - value) / peak) * 100.

*_get_empty_metrics() -> Dict[str, Any]*
Returns metrics dictionary with default values for zero-trade scenarios. Numeric fields default to 0.0 or 0, optional metrics default to None, lists default to empty.

**Static Methods:**

*create_equity_curve(trades: List[Dict[str, Any]], start_value: float) -> pd.Series*
Constructs equity curve time series from trade history. Accumulates PnL sequentially starting from initial value. Returns Series with single start_value element if no trades. Used to generate equity_curve parameter for analyzer instantiation.

**Trade Dictionary Schema:**
Expected keys in trade dictionaries:
- pnl: float - Profit and loss for trade
- entry_date: str or datetime.date - Trade entry date (string format: '%Y-%m-%d')
- exit_date: str or datetime.date - Trade exit date (string format: '%Y-%m-%d')

**Metric Return Types:**
- Percentages: Returned as raw percentage values (e.g., 65.5 for 65.5%)
- Ratios: Returned as float values (e.g., 2.5 for 2.5:1 ratio)
- Counts: Returned as integers
- Durations: Returned as float days
- Optional metrics: Return None when calculation impossible (division by zero, insufficient data)

**Dependencies:**
- pandas: Series and DataFrame operations for equity curve analysis
- numpy: Statistical calculations (mean, sqrt) and power operations
- typing: Type hints (List, Dict, Any, Optional)
- datetime: Date parsing and manipulation

**Usage Pattern:**
Instantiated after backtest execution with trade history and portfolio values. Called from core backtesting engine to generate comprehensive performance report. Equity curve typically generated via static method create_equity_curve before analyzer instantiation.

## Common Patterns

**Decorator Application:**
log_errors decorator applied to FastAPI endpoints via @ syntax. Supports both sync and async endpoints without modification. Preserves function metadata via functools.wraps.

**Error Handling Strategy:**
- Client errors (400-499): Expected validation failures, logged at INFO level for request tracking
- Server errors (500+): Unexpected failures, logged at ERROR level with full context for debugging
- Generic exceptions: Unexpected failures, logged at ERROR level with complete traceback

**Performance Calculation Flow:**
1. Execute backtest, collect trade records
2. Generate equity curve via PerformanceAnalyzer.create_equity_curve
3. Instantiate PerformanceAnalyzer with trades, values, equity curve
4. Call calculate_all_metrics for comprehensive report
5. Individual metrics available via dedicated methods for selective calculation

**None Handling:**
Performance metrics return None when calculation impossible rather than raising exceptions. Allows partial metric reporting when data insufficient for specific calculations.

**Date Parsing:**
Trade dates accepted as either string ('%Y-%m-%d' format) or datetime.date objects. Automatic type detection and conversion in duration calculations.

## Import Paths

- from src.utils import PerformanceAnalyzer, log_errors, logger
- from src.utils.api_logger import log_errors, logger
- from src.utils.performance_analyzer import PerformanceAnalyzer

## Integration Points

**API Layer (src/api/main.py):**
- log_errors decorator applied to all endpoint functions
- logger used for informational logging and debugging

**Core Layer (src/core/run_strategy.py):**
- PerformanceAnalyzer instantiated after backtest completion
- Metrics calculated and included in backtest results

**Logging Guidelines (LOGGING_GUIDELINES.md):**
- References api_logger usage patterns and best practices

## Notes

**Logging Configuration:**
Logging configured at module import time. Single shared logger instance throughout application. Log directory created automatically if missing. Both file and console output enabled for development visibility.

**Performance Metric Accuracy:**
Metrics require accurate trade records with valid dates and PnL values. Missing or malformed data results in None returns for affected metrics. Equity curve essential for drawdown-based metrics (Calmar ratio, Sortino ratio, recovery periods).

**Thread Safety:**
Logger instance thread-safe via logging module's internal locking. PerformanceAnalyzer instances not thread-safe - create separate instances per thread if parallel processing required.

**Memory Considerations:**
Equity curve stored as pandas Series. For extremely long backtests (millions of data points), consider downsampling equity curve or calculating metrics on sliding windows to reduce memory footprint.

**Error Propagation:**
log_errors decorator logs but always re-raises exceptions. Ensures errors visible in logs while maintaining normal exception handling flow. Calling code must still handle exceptions appropriately.
