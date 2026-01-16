# Core Folder Structure

## Purpose
Core backtesting engine providing strategy execution, data management, optimization, and chart data extraction capabilities.

## Components

### Strategy Execution (strategy_skeleton.py, run_strategy.py)

**Strategy_skeleton:**
Base class for all backtrader strategies with trade tracking and order management.

**Classes:**
- Strategy_skeleton: extends bt.Strategy with trade recording

**Key Methods:**
- notify_order: processes order lifecycle events
- _record_trade_from_orders: calculates and stores completed trade metrics
- log: stub for strategy logging
- start: initializes broker state
- next: strategy tick handler (override in subclasses)

**Run_strategy:**
Orchestrates strategy execution with data fetching, analyzer integration, and result compilation.

**Classes:**
- Run_strategy: strategy runner with cerebro wrapper

**Key Methods:**
- runstrat: execute complete backtest workflow
- add_analyzers: attach performance analyzers to cerebro
- _fetch_and_add_data: retrieve and configure data feed
- _execute_backtest: run cerebro and capture results
- _build_equity_curve_list: construct time-series portfolio values
- _calculate_metrics_with_analyzer: compute advanced performance metrics

### Data Management (data_manager.py)

**Purpose:** Market data caching layer with SQLite persistence and yfinance integration.

**Classes:**
- DataManager: manages OHLCV data retrieval and caching

**Key Methods:**
- get_data: retrieve data with cache-first strategy
- bulk_download: batch ticker data fetching
- get_cache_stats: cache metadata and statistics
- clear_cache: selective or full cache invalidation
- get_sp500_tickers: static S&P 500 ticker list fallback

**Database Schema:**
- ohlcv_data: ticker, date, OHLC, volume, interval
- data_metadata: ticker, interval, update timestamps

### Optimization (optimizer.py, strategy_optimization_config.py)

**optimizer.py:**
Grid search optimizer for strategy parameter tuning.

**Classes:**
- StrategyOptimizer: parameter combination testing framework

**Key Methods:**
- run_optimization: execute grid search over parameter ranges
- Returns: top 5 results sorted by PNL

**strategy_optimization_config.py:**
Parameter definitions for all strategies with bounds and metadata.

**Classes:**
- ParameterConfig: parameter specification with type, bounds, step, description

**Functions:**
- get_strategy_parameters: retrieve optimizable parameters for strategy
- get_default_parameters: get default parameter set for strategy

**Strategies Configured:**
bollinger_bands_strategy, williams_r_strategy, rsi_stochastic_strategy, mfi_strategy, keltner_channel_strategy, cci_atr_strategy, momentum_multi_strategy, adx_strategy, tema_macd_strategy, tema_crossover_strategy, alligator_strategy, cmf_atr_macd_strategy

### Chart Data Extraction (extractors/)

**Purpose:** Extract structured data from backtrader strategies for visualization and analysis.

**Module Structure:**
- __init__.py: exports all extractor classes
- ohlc_extractor.py: OHLCV time-series extraction
- indicator_extractor.py: technical indicator value extraction
- trade_marker_extractor.py: trade entry/exit point extraction
- chart_data_extractor.py: unified timeline orchestrator

**OHLCExtractor:**
Extracts OHLCV bars from PandasData feed.

**IndicatorExtractor:**
Strategy pattern for extracting indicator values from multiple indicator types.

**Extractors:**
- ArrayBasedExtractor: handles direct array access indicators
- SingleLineIndicatorExtractor: single-line backtrader indicators
- MultiLineIndicatorExtractor: multi-line backtrader indicators

**TradeMarkerExtractor:**
Converts trade history to entry/exit markers with date, price, type, action.

**ChartDataExtractor:**
Combines OHLC, indicators, and trade markers into unified timeline.

## Data Flow
1. DataManager fetches/caches market data
2. Run_strategy loads data into cerebro
3. Strategy executes with attached analyzers
4. ChartDataExtractor processes results
5. PerformanceAnalyzer calculates advanced metrics
6. Results returned with trades, equity curve, chart data

## External Dependencies
- backtrader: backtesting framework
- yfinance: market data source
- pandas: data manipulation
- sqlite3: caching layer
- src.utils.performance_analyzer: advanced metrics calculation
- src.config.backtest_config: default configuration values

## Configuration
DataManager database path: data/market_data.db
StrategyOptimizer max combinations: 1000
Default interval: from BacktestConfig.DEFAULT_INTERVAL
Default cash: from BacktestConfig.DEFAULT_CASH
