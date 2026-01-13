# Persistent Run Storage Implementation Summary

## Overview

This implementation adds persistent storage for backtest runs, allowing users to save, query, and replay strategy backtests.

## Task 1.1: Run Storage Schema and Repository

### Files Created

1. **`src/data/run_repository.py`** - Repository pattern for managing strategy runs
   - `RunRepository` class with methods:
     - `save_run(run_record)` - Save a backtest run
     - `get_run_by_id(run_id)` - Retrieve a specific run
     - `list_runs(ticker, strategy, limit, offset)` - List runs with filters
     - `get_run_count(ticker, strategy)` - Count runs matching filters
     - `delete_run(run_id)` - Delete a run

2. **`src/data/__init__.py`** - Package initialization for data module

### Database Schema

Table: `strategy_runs`
```sql
CREATE TABLE strategy_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    strategy TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    interval TEXT NOT NULL,
    cash REAL NOT NULL,
    pnl REAL,
    return_pct REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    created_at TEXT NOT NULL
);
```

Indexes:
- `idx_ticker` - Index on ticker column
- `idx_strategy` - Index on strategy column
- `idx_created_at` - Index on created_at column (DESC)

Database Location: `data/strategy_runs.db`

### Files Modified

1. **`src/config/constants.py`** - Added table name constants:
   - `TABLE_STRATEGY_RUNS = 'strategy_runs'`
   - `TABLE_OHLCV_DATA = 'ohlcv_data'`
   - `TABLE_DATA_METADATA = 'data_metadata'`

2. **`src/services/backtest_service.py`** - Integrated RunRepository:
   - Added `__init__(self)` method to initialize RunRepository
   - Modified `run_backtest()` to accept `save_run` parameter (default: True)
   - Added `_save_run()` private method to persist run records
   - Added `run_backtest_from_saved_run()` method for replaying saved runs with overrides

## Task 1.2: Saved Runs API Endpoints

### New Pydantic Models

1. **`src/api/models/requests.py`**:
   - `ReplayRunRequest` - Optional overrides for replaying runs
     - Fields: start_date, end_date, interval, cash, parameters (all optional)

2. **`src/api/models/responses.py`**:
   - `SavedRunSummaryResponse` - Summary for list view
     - Fields: id, ticker, strategy, interval, pnl, return_pct, created_at
   - `SavedRunDetailResponse` - Full details for single run view
     - Fields: id, ticker, strategy, parameters, start_date, end_date, interval, cash, pnl, return_pct, sharpe_ratio, max_drawdown, total_trades, winning_trades, losing_trades, created_at

3. **`src/api/models/__init__.py`** - Updated exports to include new models

### New API Endpoints

1. **GET `/runs`** - List saved runs with filters
   - Query parameters:
     - `ticker` (optional) - Filter by ticker
     - `strategy` (optional) - Filter by strategy
     - `limit` (default: 100, max: 1000) - Max results
     - `offset` (default: 0) - Pagination offset
   - Response: List of `SavedRunSummaryResponse` with pagination info

2. **GET `/runs/{run_id}`** - Get detailed run information
   - Path parameter: `run_id` - The run ID
   - Response: `SavedRunDetailResponse` with full run details
   - Returns 404 if run not found

3. **POST `/runs/{run_id}/replay`** - Replay a saved run with optional overrides
   - Path parameter: `run_id` - The run ID to replay
   - Body: `ReplayRunRequest` - Optional parameter overrides
   - Response: `BacktestResponse` - Full backtest results (same as `/backtest`)
   - Returns 404 if run not found

### Files Modified

1. **`src/api/main.py`**:
   - Added imports for new models and RunRepository
   - Initialized `run_repository` instance
   - Updated root endpoint to list new endpoints
   - Added three new endpoint handlers with error handling

## Key Features

### Automatic Run Persistence

- Every backtest via `/backtest` endpoint is automatically saved
- No API changes required for existing clients
- Can be disabled per request with `save_run=False` parameter (internal only)

### Run Querying

- Filter by ticker and/or strategy
- Pagination support with limit and offset
- Count total matching runs
- Created timestamp for sorting by recency

### Run Replay

- Load saved run configuration by ID
- Override any parameters (dates, cash, strategy parameters)
- Creates a new run record for the replay
- Useful for:
  - Re-running with updated date ranges
  - Testing with different capital amounts
  - Comparing parameter variations

## Implementation Details

### Repository Pattern

- Clean separation between data access and business logic
- Context manager for safe database connections
- Parameterized queries to prevent SQL injection
- Row factory for dict-like access to results

### Data Integrity

- Required fields enforced at database level
- JSON serialization for flexible parameters storage
- Timestamps in ISO 8601 format
- Null-safe handling for optional metrics

### Error Handling

- Proper HTTP status codes (404, 400, 500)
- Detailed error messages
- Exception handling at API layer
- Validation via Pydantic models

## Testing

All code passed syntax validation:
- ✓ `src/data/run_repository.py`
- ✓ `src/api/models/requests.py`
- ✓ `src/api/models/responses.py`
- ✓ `src/services/backtest_service.py`
- ✓ `src/api/main.py`

## Usage Examples

### List All Saved Runs
```bash
curl http://localhost:8086/runs
```

### List Runs for Specific Ticker
```bash
curl "http://localhost:8086/runs?ticker=AAPL&limit=10"
```

### Get Run Details
```bash
curl http://localhost:8086/runs/1
```

### Replay Run with New Dates
```bash
curl -X POST http://localhost:8086/runs/1/replay \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-06-01",
    "end_date": "2024-12-31"
  }'
```

### Replay Run with Different Cash
```bash
curl -X POST http://localhost:8086/runs/1/replay \
  -H "Content-Type: application/json" \
  -d '{
    "cash": 50000.0
  }'
```

## Database Storage

- Database file: `data/strategy_runs.db`
- Automatically created on first use
- Separate from market data cache (`data/market_data.db`)
- Can be backed up independently
- SQLite format for portability and simplicity

## API Documentation

All new endpoints are automatically documented in:
- FastAPI Swagger UI: `http://localhost:8086/docs`
- ReDoc: `http://localhost:8086/redoc`

## Next Steps for Frontend

1. Create "Saved Runs" page/tab
   - Table displaying runs from GET `/runs`
   - Columns: ID, Ticker, Strategy, Interval, PnL, Return %, Created Date
   - Add filters for ticker and strategy
   - Add pagination controls

2. Add "View Details" button
   - Calls GET `/runs/{run_id}`
   - Shows full run configuration and metrics
   - Display parameters used

3. Add "Replay" button
   - Modal/form to override parameters
   - Calls POST `/runs/{run_id}/replay`
   - Shows new backtest results

4. Add "Compare" feature (future enhancement)
   - Select multiple runs
   - Side-by-side comparison
   - Visualize differences

## Architecture Notes

- No breaking changes to existing `/backtest` endpoint
- Runs are saved internally, transparent to existing clients
- New endpoints follow existing patterns and conventions
- Follows repository pattern for data access
- Consistent error handling and validation
- Scalable: can add more fields or features without schema changes (JSON parameters)

## Files Changed

### New Files (6)
1. `src/data/__init__.py`
2. `src/data/run_repository.py`
3. `test_run_storage.py`
4. `IMPLEMENTATION_SUMMARY.md`

### Modified Files (6)
1. `src/config/constants.py`
2. `src/services/backtest_service.py`
3. `src/api/models/requests.py`
4. `src/api/models/responses.py`
5. `src/api/models/__init__.py`
6. `src/api/main.py`

**Total Changes: 10 files (6 new, 6 modified)**
