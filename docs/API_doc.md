# API Folder Structure

## Purpose
FastAPI REST endpoint layer providing HTTP interface for backtesting platform operations.

## Components

### Main Application (main.py)
FastAPI application instance with middleware stack and route handlers.

**Dependencies:**
- StrategyService: strategy loading and information retrieval
- BacktestService: backtest execution and snapshot generation
- DataManager: market data retrieval
- StrategyOptimizer: parameter optimization
- RunRepository: saved run persistence
- PresetRepository: configuration preset management
- WatchlistRepository: monitoring entry management

**Middleware:**
- CORSMiddleware: cross-origin request handling
- GZipMiddleware: response compression

**Utility Functions:**
- convert_to_columnar: transforms chart data from row to column format

### Models Package (models/)

#### Request Models (models/requests.py)
Input validation schemas for API endpoints.

**Types:**
- BacktestRequest: backtest execution parameters
- OptimizationRequest: parameter grid search configuration
- MarketDataRequest: historical data retrieval
- ReplayRunRequest: saved run replay with overrides
- CreatePresetRequest: configuration preset creation
- SnapshotRequest: real-time strategy state query
- CreateWatchlistRequest: monitoring entry creation

#### Response Models (models/responses.py)
Output data structures returned by API endpoints.

**Types:**
- BacktestResponse: backtest results and metrics
- OptimizationResponse: optimization results with ranked parameter sets
- OptimizationResult: single parameter set performance
- ParameterInfo: strategy parameter metadata
- StrategyInfo: strategy class information
- StrategyParameters: default parameter set
- SavedRunSummaryResponse: abbreviated run information
- SavedRunDetailResponse: complete run information
- PresetResponse: configuration preset data
- SnapshotPositionState: current position status
- SnapshotResponse: real-time strategy state
- WatchlistEntryResponse: monitoring entry data

#### Package Exports (models/__init__.py)
Unified import namespace for all model types.

## Endpoint Groups

### Strategy Management
- GET /strategies: list available strategies
- GET /strategies/{name}: retrieve strategy metadata

### Backtesting
- POST /backtest: execute backtest with parameters
- POST /optimize: run parameter optimization grid search

### Data Access
- POST /market-data: retrieve historical price data
- GET /parameters/default: get default parameter sets

### Run Persistence
- GET /runs: list saved backtest runs with filtering
- GET /runs/{id}: retrieve complete run details
- POST /runs/{id}/replay: re-execute run with modifications

### Configuration Presets
- POST /presets: create reusable configuration
- GET /presets: list presets with filtering
- DELETE /presets/{id}: remove preset
- POST /presets/{id}/backtest: execute backtest from preset

### Real-Time Monitoring
- POST /snapshot: get current strategy state without full backtest

### Watchlist Management
- POST /watchlist: create monitoring entry
- GET /watchlist: list monitoring entries
- GET /watchlist/{id}: retrieve entry details
- PATCH /watchlist/{id}: update entry state
- DELETE /watchlist/{id}: remove entry

### System
- GET /: API information and endpoint directory
- GET /health: system health check

## Data Flow
1. HTTP request validation via Pydantic request models
2. Service layer invocation with validated parameters
3. Business logic execution in service/core layers
4. Result transformation to response models
5. Automatic JSON serialization and HTTP response

## Error Handling
HTTPException raised with appropriate status codes:
- 400: invalid input or insufficient data
- 404: resource not found
- 409: conflict (duplicate resource)
- 500: server error

## Configuration Dependencies
- Config: API_TITLE, API_VERSION, API_HOST, API_PORT
- BacktestConfig: DEFAULT_INTERVAL, DEFAULT_CASH
- CORS settings: origins, credentials, methods, headers

## External Service Dependencies
- src.services.strategy_service
- src.services.backtest_service
- src.core.data_manager
- src.core.optimizer
- src.data.run_repository
- src.data.preset_repository
- src.data.watchlist_repository
- src.utils.api_logger
- src.exceptions
