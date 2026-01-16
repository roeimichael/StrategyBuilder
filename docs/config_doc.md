# Config Folder Structure

## Purpose
Centralized configuration management providing API settings, backtesting defaults, and system-wide constants.

## Components

### Main Configuration (__init__.py)

**Config Class:**
Unified configuration class inheriting from ApiConfig and BacktestConfig.

**Exports:**
- Config: combined configuration class
- ApiConfig: API-specific settings
- BacktestConfig: backtest-specific settings
- All constants via wildcard import

### API Configuration (api_config.py)

**Purpose:** FastAPI application configuration and CORS settings.

**ApiConfig Class Attributes:**
- API_TITLE: application title string
- API_VERSION: semantic version string
- API_HOST: server host address
- API_PORT: server port number
- CORS_ORIGINS: allowed CORS origins list
- CORS_CREDENTIALS: CORS credentials flag
- CORS_METHODS: allowed HTTP methods list
- CORS_HEADERS: allowed HTTP headers list

### Backtest Configuration (backtest_config.py)

**Purpose:** Default parameters for backtesting engine and strategy execution.

**BacktestConfig Class Attributes:**
- DEFAULT_CASH: initial portfolio cash
- DEFAULT_COMMISSION: broker commission rate
- DEFAULT_POSITION_SIZE_PCT: position sizing percentage
- DEFAULT_MACD_FAST: MACD fast period
- DEFAULT_MACD_SLOW: MACD slow period
- DEFAULT_MACD_SIGNAL: MACD signal period
- DEFAULT_ATR_PERIOD: ATR calculation period
- DEFAULT_ATR_DISTANCE: ATR-based stop distance
- DEFAULT_ORDER_PCT: order size percentage
- DEFAULT_BACKTEST_PERIOD_YEARS: default historical period
- DEFAULT_INTERVAL: default data interval

**Methods:**
- get_default_parameters(): returns dictionary of default strategy parameters

### Constants (constants.py)

**Purpose:** System-wide constant definitions for trades, orders, and database schema.

**Time Constants:**
- DAYS_PER_YEAR: days per year for annualization

**Trade Type Constants:**
- TRADE_TYPE_LONG: long position identifier
- TRADE_TYPE_SHORT: short position identifier

**Trade Action Constants:**
- TRADE_ACTION_OPEN: position opening identifier
- TRADE_ACTION_CLOSE: position closing identifier

**Order Type Constants:**
- ORDER_TYPE_BUY: buy order identifier
- ORDER_TYPE_SELL: sell order identifier

**Database Table Names:**
- TABLE_STRATEGY_RUNS: strategy runs table name
- TABLE_STRATEGY_PRESETS: strategy presets table name
- TABLE_OHLCV_DATA: market data table name
- TABLE_DATA_METADATA: data metadata table name

## Usage Pattern
Config class is imported throughout the application to access API and backtest settings. Constants are available via wildcard import for use in data models, repositories, and business logic.

## Import Paths
- from src.config import Config
- from src.config import ApiConfig, BacktestConfig
- from src.config.constants import TRADE_TYPE_LONG, TABLE_STRATEGY_RUNS

## Dependencies
None - configuration layer has no external dependencies.
