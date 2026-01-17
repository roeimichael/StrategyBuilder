# Data Folder Structure

## Purpose
Data persistence layer implementing repository pattern for strategy execution history, configuration presets, and automated monitoring entries using SQLite database.

## Components

### Package Exports (__init__.py)

**Exported Classes:**
- RunRepository: strategy execution history repository
- PresetRepository: configuration template repository
- WatchlistRepository: automated monitoring repository

### Run Repository (run_repository.py)

**Purpose:** Manages strategy backtest execution records and performance metrics.

**Database Table:** strategy_runs

**Schema:**
- id: primary key (autoincrement)
- ticker: stock symbol
- strategy: strategy class name
- parameters_json: JSON-serialized strategy parameters
- start_date: backtest start date (ISO format)
- end_date: backtest end date (ISO format)
- interval: data interval (e.g., '1d', '1h')
- cash: initial capital
- pnl: profit and loss
- return_pct: percentage return
- sharpe_ratio: risk-adjusted return metric
- max_drawdown: maximum drawdown percentage
- total_trades: total number of trades executed
- winning_trades: count of profitable trades
- losing_trades: count of losing trades
- created_at: timestamp (ISO format)

**Indexes:**
- idx_ticker: on ticker column
- idx_strategy: on strategy column
- idx_created_at: on created_at (descending)

**RunRepository Methods:**

*save_run(run_record: Dict[str, Any]) -> int*
Persists backtest execution results and returns record ID. Accepts dictionary containing ticker, strategy, parameters, date range, cash, and performance metrics. Automatically serializes parameters to JSON and timestamps creation.

*get_run_by_id(run_id: int) -> Optional[Dict[str, Any]]*
Retrieves single run record by ID. Returns dictionary with all fields and deserialized parameters, or None if not found.

*list_runs(ticker: Optional[str], strategy: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]*
Lists run records with optional filtering by ticker and strategy. Supports pagination via limit (default 100) and offset (default 0). Returns records ordered by created_at descending. Deserializes parameters JSON for each record.

*get_run_count(ticker: Optional[str], strategy: Optional[str]) -> int*
Returns total count of runs matching optional ticker and strategy filters. Used for pagination calculations.

*delete_run(run_id: int) -> bool*
Deletes run record by ID. Returns True if deleted, False if not found.

*_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]*
Internal helper converting database row to dictionary with deserialized parameters. Removes parameters_json key after parsing.

### Preset Repository (preset_repository.py)

**Purpose:** Manages reusable strategy configuration templates for quick backtest execution.

**Database Table:** strategy_presets

**Schema:**
- id: primary key (autoincrement)
- name: preset display name
- ticker: target stock symbol
- strategy: strategy class name
- parameters_json: JSON-serialized strategy parameters
- interval: data interval
- notes: optional description text
- created_at: timestamp (ISO format)
- UNIQUE constraint: (name, strategy, ticker) combination

**Indexes:**
- idx_preset_ticker: on ticker column
- idx_preset_strategy: on strategy column
- idx_preset_name: on name column

**PresetRepository Methods:**

*create_preset(preset_data: Dict[str, Any]) -> int*
Creates new preset configuration. Accepts dictionary with name, ticker, strategy, parameters, interval, and optional notes. Automatically serializes parameters to JSON and timestamps creation. Enforces unique constraint on (name, strategy, ticker). Returns created preset ID.

*get_preset(preset_id: int) -> Optional[Dict[str, Any]]*
Retrieves single preset by ID. Returns dictionary with all fields and deserialized parameters, or None if not found.

*list_presets(ticker: Optional[str], strategy: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]*
Lists presets with optional filtering by ticker and strategy. Supports pagination via limit (default 100) and offset (default 0). Returns records ordered by created_at descending. Deserializes parameters JSON for each record.

*delete_preset(preset_id: int) -> bool*
Deletes preset by ID. Returns True if deleted, False if not found. Note: Check watchlist foreign keys before deletion.

*get_preset_count(ticker: Optional[str], strategy: Optional[str]) -> int*
Returns total count of presets matching optional ticker and strategy filters. Used for pagination calculations.

*preset_exists(name: str, strategy: str, ticker: str) -> bool*
Checks if preset with exact (name, strategy, ticker) combination already exists. Used for duplicate prevention before creation.

*_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]*
Internal helper converting database row to dictionary with deserialized parameters. Removes parameters_json key after parsing.

### Watchlist Repository (watchlist_repository.py)

**Purpose:** Manages automated monitoring entries for scheduled strategy execution and surveillance.

**Database Table:** watchlist_entries

**Schema:**
- id: primary key (autoincrement)
- name: entry display name
- preset_id: foreign key to strategy_presets (nullable)
- run_id: foreign key to strategy_runs (nullable)
- frequency: execution frequency (e.g., 'daily', 'intraday_15m')
- enabled: active status (integer: 1=enabled, 0=disabled)
- created_at: timestamp (ISO format)
- last_run_at: last execution timestamp (nullable, ISO format)
- FOREIGN KEY: preset_id references strategy_presets(id)
- FOREIGN KEY: run_id references strategy_runs(id)
- CHECK constraint: preset_id IS NOT NULL OR run_id IS NOT NULL

**Indexes:**
- idx_watchlist_preset: on preset_id column
- idx_watchlist_run: on run_id column
- idx_watchlist_enabled: on enabled column
- idx_watchlist_frequency: on frequency column

**WatchlistRepository Methods:**

*create_entry(entry_data: Dict[str, Any]) -> int*
Creates new watchlist monitoring entry. Requires name, frequency, and either preset_id or run_id (not both required but at least one). Optional enabled boolean (defaults True). Converts enabled boolean to integer (1/0) for SQLite storage. Raises ValueError if neither preset_id nor run_id provided. Returns created entry ID.

*get_entry(entry_id: int) -> Optional[Dict[str, Any]]*
Retrieves single watchlist entry by ID. Returns dictionary with all fields and enabled converted to boolean, or None if not found.

*list_entries(enabled_only: bool) -> List[Dict[str, Any]]*
Lists all watchlist entries, optionally filtered to enabled only. Returns records ordered by created_at descending. Converts enabled integer to boolean for each record.

*update_entry(entry_id: int, updates: Dict[str, Any]) -> bool*
Updates watchlist entry fields. Allowed fields: name, enabled, frequency, last_run_at. Filters out disallowed fields. Converts enabled boolean to integer if present. Returns True if updated, False if entry not found or no valid fields provided.

*delete_entry(entry_id: int) -> bool*
Deletes watchlist entry by ID. Returns True if deleted, False if not found.

*update_last_run(entry_id: int) -> bool*
Convenience method updating last_run_at timestamp to current time. Internally calls update_entry. Returns True if updated.

*get_entries_by_frequency(frequency: str, enabled_only: bool) -> List[Dict[str, Any]]*
Retrieves watchlist entries matching specific frequency (e.g., 'daily', 'intraday_15m'). Optional enabled_only filter (defaults True). Returns records ordered by created_at descending. Converts enabled integer to boolean. Used by scheduler to identify entries requiring execution.

*_get_connection() -> ContextManager*
Internal context manager for database connections. Configures row_factory for dict-like access. Ensures connection cleanup via finally block.

## Database Relationships

**Foreign Key Constraints:**
- watchlist_entries.preset_id → strategy_presets.id
- watchlist_entries.run_id → strategy_runs.id

**Constraint Logic:**
Watchlist entries must reference either a preset (for template-based monitoring) or a saved run (for result replication monitoring), enforced via CHECK constraint.

**Cascade Behavior:**
No automatic cascade deletes configured. Applications must handle cleanup when deleting referenced presets or runs to maintain referential integrity.

## Common Patterns

**Context Manager Usage:**
All repositories use @contextmanager decorator for database connections, ensuring automatic connection cleanup and transaction management.

**JSON Serialization:**
Strategy parameters stored as JSON strings in database, automatically serialized on write and deserialized on read via json.dumps/json.loads.

**Timestamp Management:**
All timestamps stored in ISO 8601 format using datetime.datetime.now().isoformat() for consistency and timezone awareness.

**Boolean Storage:**
SQLite lacks native boolean type. Enabled flags stored as integers (1/0) and converted to Python booleans in application layer.

**Row Factory:**
All repositories configure sqlite3.Row as row_factory for dict-like column access by name rather than index.

**Pagination Support:**
list_* methods accept limit and offset parameters for efficient large dataset handling, paired with get_*_count methods for total calculation.

## Usage Pattern

Repositories imported throughout application layers (API endpoints, business logic) for data persistence. Each repository manages single database table with CRUD operations, following single responsibility principle. All methods accept and return dictionaries for parameter flexibility and JSON compatibility.

## Import Paths

- from src.data import RunRepository, PresetRepository, WatchlistRepository
- from src.data.run_repository import RunRepository
- from src.data.preset_repository import PresetRepository
- from src.data.watchlist_repository import WatchlistRepository

## Dependencies

**Standard Library:**
- os: path operations for database file location
- sqlite3: embedded database engine
- datetime: timestamp generation
- json: parameter serialization
- typing: type hints (Optional, List, Dict, Any)
- contextlib: context manager decorator

**Database Location:**
Default path: `{project_root}/data/strategy_runs.db`
All three repositories share single SQLite database file containing three tables.

## Notes

**Thread Safety:**
SQLite connections not thread-safe. Each operation creates new connection via context manager. For concurrent access, consider connection pooling or per-thread connections.

**Transaction Management:**
All write operations explicitly commit. Context manager handles rollback on exception. No support for multi-operation transactions across methods.

**Error Handling:**
Minimal error handling in repositories. SQLite constraint violations (unique, foreign key, check) propagate as exceptions to calling layer for appropriate HTTP status code mapping in API layer.
