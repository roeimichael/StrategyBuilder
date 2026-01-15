# StrategyBuilder API - Frontend Implementation Guide

**Version:** 1.0
**Last Updated:** 2026-01-15
**Base URL:** `http://localhost:8000` (or your deployment URL)

This guide provides comprehensive documentation for all newly implemented API endpoints, with a focus on frontend integration, UI/UX recommendations, and practical examples.

---

## Table of Contents

1. [Runs Management](#1-runs-management)
2. [Presets Management](#2-presets-management)
3. [Snapshot Endpoint](#3-snapshot-endpoint)
4. [Watchlist Management](#4-watchlist-management)
5. [Optimization Endpoint](#5-optimization-endpoint)
6. [Frontend Implementation Patterns](#6-frontend-implementation-patterns)
7. [Error Handling](#7-error-handling)

---

## 1. Runs Management

The Runs system allows you to **browse**, **replay**, and **analyze** all historical backtest executions saved in the database.

### 1.1 List All Runs - `GET /runs`

**Purpose:** Retrieve a paginated list of all saved backtest runs with optional filtering.

**Use Cases:**
- Display a history table of all past backtests
- Filter runs by ticker or strategy
- Implement pagination for large datasets
- Show quick performance overview (PNL, return %)

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticker` | string | No | None | Filter by ticker symbol (e.g., "AAPL") |
| `strategy` | string | No | None | Filter by strategy name |
| `limit` | integer | No | 100 | Max results per page (1-1000) |
| `offset` | integer | No | 0 | Results to skip (for pagination) |

**Request Example:**

```javascript
// Fetch first 20 runs for AAPL
const response = await fetch(
  'http://localhost:8000/runs?ticker=AAPL&limit=20&offset=0'
);
const data = await response.json();
```

```bash
# cURL example
curl "http://localhost:8000/runs?ticker=AAPL&strategy=bollinger_bands_strategy&limit=50"
```

**Response Format:**

```json
{
  "success": true,
  "total_count": 245,
  "count": 20,
  "limit": 20,
  "offset": 0,
  "runs": [
    {
      "id": 123,
      "ticker": "AAPL",
      "strategy": "bollinger_bands_strategy",
      "interval": "1d",
      "pnl": 1250.50,
      "return_pct": 12.50,
      "created_at": "2024-12-15T14:30:22"
    },
    {
      "id": 122,
      "ticker": "AAPL",
      "strategy": "rsi_stochastic_strategy",
      "interval": "1h",
      "pnl": -325.75,
      "return_pct": -3.26,
      "created_at": "2024-12-14T09:15:10"
    }
  ]
}
```

**Frontend UI Recommendations:**

1. **Table View:**
   - Columns: Date, Ticker, Strategy, Interval, PNL, Return %, Actions
   - Color-code PNL (green for positive, red for negative)
   - Add sorting by date, PNL, return %
   - Click row to navigate to detail view

2. **Filters:**
   - Dropdown for ticker selection (populate from available runs)
   - Dropdown for strategy selection
   - Date range picker
   - "Reset Filters" button

3. **Pagination:**
   - Show "Showing X-Y of Z results"
   - Previous/Next buttons
   - Page size selector (20, 50, 100)

**Example React Component Structure:**

```jsx
function RunsTable() {
  const [runs, setRuns] = useState([]);
  const [page, setPage] = useState(0);
  const [ticker, setTicker] = useState(null);
  const [strategy, setStrategy] = useState(null);
  const limit = 20;

  useEffect(() => {
    fetchRuns();
  }, [page, ticker, strategy]);

  const fetchRuns = async () => {
    const params = new URLSearchParams({
      limit: limit,
      offset: page * limit,
      ...(ticker && { ticker }),
      ...(strategy && { strategy })
    });

    const response = await fetch(`/runs?${params}`);
    const data = await response.json();
    setRuns(data.runs);
  };

  return (
    <div>
      {/* Filters */}
      <FilterBar
        onTickerChange={setTicker}
        onStrategyChange={setStrategy}
      />

      {/* Table */}
      <table>
        {runs.map(run => (
          <tr key={run.id} onClick={() => navigate(`/runs/${run.id}`)}>
            <td>{formatDate(run.created_at)}</td>
            <td>{run.ticker}</td>
            <td>{run.strategy}</td>
            <td>{run.interval}</td>
            <td className={run.pnl >= 0 ? 'positive' : 'negative'}>
              ${run.pnl.toFixed(2)}
            </td>
            <td>{run.return_pct.toFixed(2)}%</td>
          </tr>
        ))}
      </table>

      {/* Pagination */}
      <Pagination page={page} onChange={setPage} />
    </div>
  );
}
```

---

### 1.2 Get Run Details - `GET /runs/{run_id}`

**Purpose:** Retrieve full details of a specific backtest run.

**Use Cases:**
- Display detailed performance metrics for a single run
- Show complete parameter configuration
- Analyze trade statistics
- Provide "Replay" button to re-run with modifications

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `run_id` | integer | Yes | The ID of the saved run |

**Request Example:**

```javascript
const runId = 123;
const response = await fetch(`http://localhost:8000/runs/${runId}`);
const data = await response.json();
```

**Response Format:**

```json
{
  "id": 123,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  },
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "pnl": 1250.50,
  "return_pct": 12.50,
  "sharpe_ratio": 1.45,
  "max_drawdown": -8.5,
  "total_trades": 24,
  "winning_trades": 15,
  "losing_trades": 9,
  "created_at": "2024-12-15T14:30:22"
}
```

**Frontend UI Recommendations:**

1. **Header Section:**
   - Large ticker symbol badge
   - Strategy name with icon
   - Created date
   - "Replay Run" and "Compare" buttons

2. **Performance Metrics Cards:**
   - Grid layout (2x3 or 3x2)
   - Cards for: Total PNL, Return %, Sharpe Ratio, Max Drawdown, Win Rate, Total Trades
   - Use progress bars for percentages
   - Color-coding for good/bad metrics

3. **Configuration Section:**
   - Collapsible "Parameters" panel
   - Show start/end dates, interval, initial cash
   - Strategy parameters in key-value format

4. **Actions:**
   - "Replay with Different Dates" → Modal with date picker
   - "Replay with Modified Parameters" → Modal with parameter editor
   - "Save as Preset" → Create preset from this run
   - "Add to Watchlist" → Quick watchlist entry

**Example Detail View Component:**

```jsx
function RunDetail({ runId }) {
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRunDetail();
  }, [runId]);

  const fetchRunDetail = async () => {
    const response = await fetch(`/runs/${runId}`);
    const data = await response.json();
    setRun(data);
    setLoading(false);
  };

  const handleReplay = () => {
    // Open replay modal
  };

  if (loading) return <Loader />;

  return (
    <div className="run-detail">
      <header>
        <h1>{run.ticker}</h1>
        <span className="strategy-badge">{run.strategy}</span>
        <button onClick={handleReplay}>Replay Run</button>
      </header>

      <div className="metrics-grid">
        <MetricCard
          title="Total PNL"
          value={`$${run.pnl.toFixed(2)}`}
          positive={run.pnl >= 0}
        />
        <MetricCard
          title="Return %"
          value={`${run.return_pct.toFixed(2)}%`}
          positive={run.return_pct >= 0}
        />
        <MetricCard
          title="Sharpe Ratio"
          value={run.sharpe_ratio?.toFixed(2) || 'N/A'}
        />
        <MetricCard
          title="Max Drawdown"
          value={`${run.max_drawdown?.toFixed(2)}%`}
          positive={false}
        />
        <MetricCard
          title="Win Rate"
          value={`${((run.winning_trades / run.total_trades) * 100).toFixed(1)}%`}
        />
        <MetricCard
          title="Total Trades"
          value={run.total_trades}
        />
      </div>

      <ConfigSection run={run} />
    </div>
  );
}
```

---

### 1.3 Replay Run - `POST /runs/{run_id}/replay`

**Purpose:** Re-execute a saved run with optional parameter overrides.

**Use Cases:**
- Test same strategy with different date ranges
- Adjust parameters without creating new preset
- Quick backtesting iterations
- A/B testing parameter variations

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `run_id` | integer | Yes | The ID of the run to replay |

**Request Body (All Optional):**

```typescript
interface ReplayRunRequest {
  start_date?: string;      // "2024-01-01"
  end_date?: string;        // "2024-12-31"
  interval?: string;        // "1d", "1h", etc.
  cash?: number;            // 10000.0
  parameters?: {            // Strategy parameters to override
    [key: string]: number;
  };
}
```

**Request Example:**

```javascript
// Replay with different date range
const response = await fetch(`http://localhost:8000/runs/123/replay`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start_date: '2024-06-01',
    end_date: '2024-12-31'
  })
});
const data = await response.json();
```

```javascript
// Replay with modified parameters
const response = await fetch(`http://localhost:8000/runs/123/replay`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    parameters: {
      period: 25,
      devfactor: 2.5
    }
  })
});
```

**Response Format:**

Same as `POST /backtest` response (see BacktestResponse schema):

```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_value": 10000.0,
  "end_value": 11250.50,
  "pnl": 1250.50,
  "return_pct": 12.50,
  "sharpe_ratio": 1.45,
  "max_drawdown": -8.5,
  "total_trades": 24,
  "interval": "1d",
  "start_date": "2024-06-01",
  "end_date": "2024-12-31",
  "advanced_metrics": {
    "winning_trades": 15,
    "losing_trades": 9,
    "avg_win": 125.30,
    "avg_loss": -85.20
  },
  "chart_data": null
}
```

**Frontend UI Recommendations:**

1. **Replay Modal:**
   - Show original run configuration (read-only, grayed out)
   - Overlay editable fields for overrides
   - Checkboxes: "Change dates", "Change interval", "Modify parameters"
   - When checked, reveal input fields
   - "Replay" button (primary action)

2. **Comparison View (Advanced):**
   - Split screen: Original vs Replayed
   - Side-by-side metric comparison
   - Highlight differences in green/red
   - Option to save replayed result

**Example Replay Modal:**

```jsx
function ReplayModal({ run, onClose }) {
  const [overrides, setOverrides] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleReplay = async () => {
    setLoading(true);
    const response = await fetch(`/runs/${run.id}/replay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(overrides)
    });
    const data = await response.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <Modal onClose={onClose}>
      <h2>Replay Run #{run.id}</h2>

      <OriginalConfig run={run} />

      <OverrideSection>
        <DateRangeInput
          label="Change Date Range"
          defaultStart={run.start_date}
          defaultEnd={run.end_date}
          onChange={(start, end) => setOverrides({
            ...overrides,
            start_date: start,
            end_date: end
          })}
        />

        <ParameterEditor
          label="Modify Parameters"
          parameters={run.parameters}
          onChange={(params) => setOverrides({
            ...overrides,
            parameters: params
          })}
        />
      </OverrideSection>

      <button onClick={handleReplay} disabled={loading}>
        {loading ? 'Running...' : 'Replay'}
      </button>

      {result && <ResultComparison original={run} replayed={result} />}
    </Modal>
  );
}
```

---

## 2. Presets Management

Presets allow users to **save**, **reuse**, and **share** strategy configurations without re-entering parameters.

### 2.1 Create Preset - `POST /presets`

**Purpose:** Save a strategy configuration as a named preset for future use.

**Use Cases:**
- Save favorite strategy configurations
- Create templates for different market conditions
- Quickly switch between tested setups
- Share configurations with team members

**Request Body:**

```typescript
interface CreatePresetRequest {
  name: string;                // Unique descriptive name (1-200 chars)
  ticker: string;              // Ticker symbol
  strategy: string;            // Strategy module name
  parameters: {                // Strategy parameters
    [key: string]: number;
  };
  interval: string;            // Time interval (default: "1d")
  notes?: string;              // Optional notes (max 1000 chars)
}
```

**Request Example:**

```javascript
const response = await fetch('http://localhost:8000/presets', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "AAPL Bollinger Aggressive",
    ticker: "AAPL",
    strategy: "bollinger_bands_strategy",
    parameters: {
      period: 15,
      devfactor: 2.5
    },
    interval: "1d",
    notes: "More sensitive to volatility, works well in trending markets"
  })
});
const data = await response.json();
```

**Response Format:**

```json
{
  "id": 42,
  "name": "AAPL Bollinger Aggressive",
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "parameters": {
    "period": 15,
    "devfactor": 2.5
  },
  "interval": "1d",
  "notes": "More sensitive to volatility, works well in trending markets",
  "created_at": "2024-12-15T16:45:30"
}
```

**Validation Errors:**

```json
// 409 Conflict - Preset already exists
{
  "detail": "Preset with name 'AAPL Bollinger Aggressive' for strategy 'bollinger_bands_strategy' and ticker 'AAPL' already exists"
}

// 404 Not Found - Strategy doesn't exist
{
  "detail": "Strategy 'invalid_strategy' not found"
}
```

**Frontend UI Recommendations:**

1. **Save as Preset Button:**
   - Place in backtest result view
   - Place in strategy configuration form
   - Show dialog with pre-filled values

2. **Preset Creation Form:**
   - Name input (required, with character counter)
   - Read-only fields showing ticker, strategy, parameters
   - Interval dropdown (if not already selected)
   - Notes textarea (optional, markdown support)
   - Preview panel showing how preset will appear

3. **Validation:**
   - Check name uniqueness before submitting
   - Show warning if similar preset exists
   - Suggest alternative names

**Example Create Preset Component:**

```jsx
function SavePresetDialog({ backtestConfig, onSave, onCancel }) {
  const [name, setName] = useState('');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/presets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          ticker: backtestConfig.ticker,
          strategy: backtestConfig.strategy,
          parameters: backtestConfig.parameters,
          interval: backtestConfig.interval,
          notes
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      const preset = await response.json();
      onSave(preset);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog>
      <h2>Save as Preset</h2>

      <Input
        label="Preset Name"
        value={name}
        onChange={setName}
        placeholder="e.g., AAPL Bollinger Aggressive"
        maxLength={200}
        required
      />

      <PresetPreview config={backtestConfig} />

      <TextArea
        label="Notes (optional)"
        value={notes}
        onChange={setNotes}
        placeholder="Describe when to use this preset..."
        maxLength={1000}
      />

      {error && <ErrorMessage>{error}</ErrorMessage>}

      <Actions>
        <button onClick={onCancel}>Cancel</button>
        <button
          onClick={handleSave}
          disabled={!name || loading}
        >
          {loading ? 'Saving...' : 'Save Preset'}
        </button>
      </Actions>
    </Dialog>
  );
}
```

---

### 2.2 List Presets - `GET /presets`

**Purpose:** Retrieve all saved presets with optional filtering.

**Use Cases:**
- Display preset library
- Quick-select preset for backtesting
- Filter by ticker or strategy
- Preset management dashboard

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticker` | string | No | None | Filter by ticker symbol |
| `strategy` | string | No | None | Filter by strategy name |
| `limit` | integer | No | 100 | Max results (1-1000) |
| `offset` | integer | No | 0 | Pagination offset |

**Request Example:**

```javascript
const response = await fetch('http://localhost:8000/presets?ticker=AAPL&limit=50');
const data = await response.json();
```

**Response Format:**

```json
{
  "success": true,
  "total_count": 15,
  "count": 15,
  "limit": 50,
  "offset": 0,
  "presets": [
    {
      "id": 42,
      "name": "AAPL Bollinger Aggressive",
      "ticker": "AAPL",
      "strategy": "bollinger_bands_strategy",
      "parameters": {
        "period": 15,
        "devfactor": 2.5
      },
      "interval": "1d",
      "notes": "More sensitive to volatility",
      "created_at": "2024-12-15T16:45:30"
    },
    {
      "id": 38,
      "name": "AAPL RSI Oversold",
      "ticker": "AAPL",
      "strategy": "rsi_stochastic_strategy",
      "parameters": {
        "rsi_period": 14,
        "rsi_oversold": 25,
        "rsi_overbought": 75
      },
      "interval": "1h",
      "notes": null,
      "created_at": "2024-12-10T11:20:15"
    }
  ]
}
```

**Frontend UI Recommendations:**

1. **Preset Library View:**
   - Card grid layout (3-4 columns)
   - Each card shows: name, ticker badge, strategy icon, interval
   - Hover reveals: full parameters, notes, actions
   - "Use Preset" button (primary action)

2. **Quick Actions per Preset:**
   - "Run Backtest" → Opens backtest form with preset loaded
   - "Edit" → Modify preset (opens edit dialog)
   - "Clone" → Create copy with different name
   - "Delete" → Remove preset with confirmation
   - "Add to Watchlist" → Quick watchlist entry

3. **Filters & Search:**
   - Search bar (filter by name or notes)
   - Ticker filter dropdown
   - Strategy filter dropdown
   - Sort by: Date created, Name, Ticker

**Example Preset Library:**

```jsx
function PresetLibrary() {
  const [presets, setPresets] = useState([]);
  const [filters, setFilters] = useState({ ticker: null, strategy: null });

  useEffect(() => {
    fetchPresets();
  }, [filters]);

  const fetchPresets = async () => {
    const params = new URLSearchParams({
      ...(filters.ticker && { ticker: filters.ticker }),
      ...(filters.strategy && { strategy: filters.strategy })
    });

    const response = await fetch(`/presets?${params}`);
    const data = await response.json();
    setPresets(data.presets);
  };

  const handleUsePreset = (preset) => {
    // Navigate to backtest page with preset loaded
    navigate('/backtest', { state: { preset } });
  };

  return (
    <div className="preset-library">
      <FilterBar filters={filters} onChange={setFilters} />

      <div className="preset-grid">
        {presets.map(preset => (
          <PresetCard
            key={preset.id}
            preset={preset}
            onUse={() => handleUsePreset(preset)}
            onEdit={() => editPreset(preset.id)}
            onDelete={() => deletePreset(preset.id)}
          />
        ))}
      </div>
    </div>
  );
}

function PresetCard({ preset, onUse, onEdit, onDelete }) {
  return (
    <div className="preset-card">
      <header>
        <h3>{preset.name}</h3>
        <span className="ticker-badge">{preset.ticker}</span>
      </header>

      <div className="strategy-info">
        <span className="strategy">{preset.strategy}</span>
        <span className="interval">{preset.interval}</span>
      </div>

      <ParamsPreview parameters={preset.parameters} />

      {preset.notes && (
        <p className="notes">{preset.notes}</p>
      )}

      <footer>
        <button onClick={onUse} className="primary">
          Run Backtest
        </button>
        <IconButton onClick={onEdit} icon="edit" />
        <IconButton onClick={onDelete} icon="delete" />
      </footer>
    </div>
  );
}
```

---

### 2.3 Delete Preset - `DELETE /presets/{preset_id}`

**Purpose:** Remove a preset from the library.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `preset_id` | integer | Yes | ID of preset to delete |

**Request Example:**

```javascript
const response = await fetch(`http://localhost:8000/presets/42`, {
  method: 'DELETE'
});
const data = await response.json();
```

**Response Format:**

```json
{
  "success": true,
  "message": "Preset 42 deleted successfully"
}
```

**Frontend UI Recommendations:**

1. **Confirmation Dialog:**
   - Show preset name and details
   - Warning: "This action cannot be undone"
   - Note: "Associated watchlist entries will not be deleted but will show as orphaned"
   - Two-step confirmation for important presets

2. **Optimistic Updates:**
   - Remove card from UI immediately
   - Show "Undo" snackbar for 5 seconds
   - Revert if undo clicked

---

### 2.4 Backtest from Preset - `POST /presets/{preset_id}/backtest`

**Purpose:** Run a backtest using a saved preset configuration.

**Use Cases:**
- Quick backtesting with saved configurations
- Test preset on different date ranges
- Batch testing multiple presets

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `preset_id` | integer | Yes | ID of preset to use |

**Query Parameters (All Optional):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_date` | string | None | Override start date ("2024-01-01") |
| `end_date` | string | None | Override end date ("2024-12-31") |
| `cash` | float | 10000 | Override initial cash |

**Request Example:**

```javascript
// Use preset with custom date range
const response = await fetch(
  'http://localhost:8000/presets/42/backtest?start_date=2024-06-01&end_date=2024-12-31',
  { method: 'POST' }
);
const data = await response.json();
```

```javascript
// Use preset with default dates but higher capital
const response = await fetch(
  'http://localhost:8000/presets/42/backtest?cash=50000',
  { method: 'POST' }
);
```

**Response Format:**

Same as `POST /backtest` (BacktestResponse).

**Frontend UI Recommendations:**

1. **Quick Run Button:**
   - Prominent "Run Backtest" button on preset card
   - Click → Immediately runs with default dates (last 1 year)
   - Shows loading spinner on card

2. **Advanced Run Modal:**
   - "Run with Options" button (secondary)
   - Modal with date picker and cash input
   - Preview: "This will run [Strategy] on [Ticker] from [Start] to [End] with $[Cash]"
   - "Run" button

---

## 3. Snapshot Endpoint

The Snapshot endpoint provides **near-real-time** strategy monitoring without running full historical backtests.

### 3.1 Get Strategy Snapshot - `POST /snapshot`

**Purpose:** Get current strategy state, indicators, and position for live monitoring.

**Key Features:**
- Fast execution (only fetches recent data)
- Does not save to database
- Returns last bar OHLC, current indicators, position state
- Optimized for polling/dashboard updates

**Use Cases:**
- Live trading dashboards
- Real-time strategy monitoring
- Position status checks
- Indicator value tracking
- Recent trade history

**Request Body:**

```typescript
interface SnapshotRequest {
  ticker: string;              // Stock symbol
  strategy: string;            // Strategy module name
  parameters?: {               // Optional parameter overrides
    [key: string]: number;
  };
  interval: string;            // "1d", "1h", "15m", etc. (default: "1d")
  lookback_bars: number;       // Number of recent bars (50-1000, default: 200)
  cash: number;                // Starting cash (default: 10000)
}
```

**Request Example:**

```javascript
// Get daily snapshot for AAPL
const response = await fetch('http://localhost:8000/snapshot', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: "AAPL",
    strategy: "bollinger_bands_strategy",
    parameters: {
      period: 20,
      devfactor: 2.0
    },
    interval: "1d",
    lookback_bars: 200
  })
});
const data = await response.json();
```

```javascript
// Get intraday snapshot for crypto (15-minute bars)
const response = await fetch('http://localhost:8000/snapshot', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: "BTC-USD",
    strategy: "rsi_stochastic_strategy",
    interval: "15m",
    lookback_bars: 500,
    cash: 50000
  })
});
```

**Response Format:**

```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "interval": "1d",
  "lookback_bars": 200,
  "last_bar": {
    "date": "2024-12-15",
    "open": 195.50,
    "high": 198.25,
    "low": 194.80,
    "close": 197.40,
    "volume": 52840000
  },
  "indicators": {
    "bollinger_upper": 202.35,
    "bollinger_middle": 196.80,
    "bollinger_lower": 191.25,
    "sma_20": 196.80
  },
  "position_state": {
    "in_position": true,
    "position_type": "long",
    "entry_price": 192.50,
    "current_price": 197.40,
    "size": 51.9,
    "unrealized_pnl": 254.31
  },
  "recent_trades": [
    {
      "date": "2024-12-10",
      "type": "BUY",
      "price": 192.50,
      "size": 51.9,
      "commission": 0.0
    },
    {
      "date": "2024-12-01",
      "type": "SELL",
      "price": 189.30,
      "size": 52.8,
      "pnl": -180.50,
      "commission": 0.0
    }
  ],
  "portfolio_value": 10254.31,
  "cash": 0.0,
  "timestamp": "2024-12-15T21:00:00"
}
```

**Response Fields Explained:**

| Field | Type | Description |
|-------|------|-------------|
| `last_bar` | object | Most recent OHLCV bar |
| `indicators` | object | Current indicator values (strategy-specific) |
| `position_state.in_position` | boolean | Whether currently holding a position |
| `position_state.position_type` | string | "long" or "short" (null if not in position) |
| `position_state.entry_price` | float | Price at which position was entered |
| `position_state.current_price` | float | Latest close price |
| `position_state.size` | float | Number of shares/units held |
| `position_state.unrealized_pnl` | float | Current profit/loss if position closed now |
| `recent_trades` | array | Last 10 trades executed |
| `portfolio_value` | float | Total portfolio value (cash + position value) |
| `cash` | float | Available cash |
| `timestamp` | string | Snapshot generation time |

**Frontend UI Recommendations:**

1. **Live Dashboard Layout:**
   - **Header:** Ticker, Strategy, Last updated timestamp
   - **Position Card:** Large, prominent
     - If in position: Show entry price, current price, unrealized PNL
     - Color-code based on PNL (green/red)
     - Show position type (LONG/SHORT badge)
   - **Price Card:** OHLCV for last bar
   - **Indicators Card:** Current indicator values with visual aids
   - **Recent Trades:** Scrollable list

2. **Auto-Refresh:**
   - For daily interval: Refresh every 5-15 minutes during market hours
   - For intraday: Refresh every 1-5 minutes
   - Show "Last updated X seconds ago"
   - Manual refresh button

3. **Visual Indicators:**
   - Bollinger Bands: Show price relative to bands (horizontal bar)
   - RSI: Gauge with oversold/overbought zones
   - MACD: Signal line crossover indicator
   - Moving Averages: Price above/below MA indicator

**Example Snapshot Dashboard:**

```jsx
function SnapshotDashboard({ ticker, strategy, parameters }) {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    fetchSnapshot();
    const interval = setInterval(fetchSnapshot, 300000); // 5 minutes
    return () => clearInterval(interval);
  }, [ticker, strategy, parameters]);

  const fetchSnapshot = async () => {
    setLoading(true);
    const response = await fetch('/snapshot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticker,
        strategy,
        parameters,
        interval: '1d',
        lookback_bars: 200
      })
    });
    const data = await response.json();
    setSnapshot(data);
    setLastUpdate(new Date());
    setLoading(false);
  };

  if (!snapshot) return <Loader />;

  return (
    <div className="snapshot-dashboard">
      <header>
        <h1>{snapshot.ticker}</h1>
        <span className="strategy-badge">{snapshot.strategy}</span>
        <RefreshButton onClick={fetchSnapshot} loading={loading} />
        <LastUpdated timestamp={lastUpdate} />
      </header>

      <div className="dashboard-grid">
        {/* Position Card */}
        <PositionCard state={snapshot.position_state} />

        {/* Price Card */}
        <PriceCard
          bar={snapshot.last_bar}
          portfolioValue={snapshot.portfolio_value}
          cash={snapshot.cash}
        />

        {/* Indicators Card */}
        <IndicatorsCard
          indicators={snapshot.indicators}
          strategy={snapshot.strategy}
          currentPrice={snapshot.last_bar.close}
        />

        {/* Recent Trades */}
        <TradesCard trades={snapshot.recent_trades} />
      </div>
    </div>
  );
}

function PositionCard({ state }) {
  if (!state.in_position) {
    return (
      <Card className="position-card no-position">
        <h2>No Position</h2>
        <p>Waiting for entry signal...</p>
      </Card>
    );
  }

  const pnlPositive = state.unrealized_pnl >= 0;

  return (
    <Card className={`position-card ${pnlPositive ? 'positive' : 'negative'}`}>
      <header>
        <h2>Current Position</h2>
        <Badge type={state.position_type}>{state.position_type.toUpperCase()}</Badge>
      </header>

      <div className="position-details">
        <div className="detail">
          <span className="label">Entry Price:</span>
          <span className="value">${state.entry_price.toFixed(2)}</span>
        </div>
        <div className="detail">
          <span className="label">Current Price:</span>
          <span className="value">${state.current_price.toFixed(2)}</span>
        </div>
        <div className="detail">
          <span className="label">Size:</span>
          <span className="value">{state.size.toFixed(2)} shares</span>
        </div>
        <div className="detail large">
          <span className="label">Unrealized P&L:</span>
          <span className={`value ${pnlPositive ? 'positive' : 'negative'}`}>
            ${state.unrealized_pnl.toFixed(2)}
          </span>
        </div>
      </div>

      <PnlGauge value={state.unrealized_pnl} />
    </Card>
  );
}

function IndicatorsCard({ indicators, strategy, currentPrice }) {
  // Render different indicator visualizations based on strategy
  if (strategy.includes('bollinger')) {
    return (
      <Card>
        <h2>Bollinger Bands</h2>
        <BollingerVisualization
          upper={indicators.bollinger_upper}
          middle={indicators.bollinger_middle}
          lower={indicators.bollinger_lower}
          price={currentPrice}
        />
      </Card>
    );
  }

  if (strategy.includes('rsi')) {
    return (
      <Card>
        <h2>RSI</h2>
        <RSIGauge value={indicators.rsi} />
      </Card>
    );
  }

  // Generic indicator display
  return (
    <Card>
      <h2>Indicators</h2>
      {Object.entries(indicators).map(([key, value]) => (
        <div key={key} className="indicator-row">
          <span>{key}:</span>
          <span>{value.toFixed(2)}</span>
        </div>
      ))}
    </Card>
  );
}
```

**Performance Considerations:**

- **Lookback Bars:** Use 200-300 for daily, 500-800 for intraday
- **Polling Frequency:**
  - Daily strategies: Every 5-15 minutes
  - Intraday strategies: Every 1-5 minutes
  - Avoid polling more than once per minute
- **Caching:** Consider caching on frontend for 1-2 minutes
- **Error Handling:** Gracefully handle market closed scenarios

---

## 4. Watchlist Management

Watchlists enable **automated monitoring** of strategies by scheduling periodic snapshots or backtests.

### 4.1 Create Watchlist Entry - `POST /watchlist`

**Purpose:** Add a preset or run to the watchlist for automated monitoring.

**Use Cases:**
- Schedule daily strategy checks
- Monitor multiple strategies simultaneously
- Alert on position changes
- Track favorite configurations

**Request Body:**

```typescript
interface CreateWatchlistRequest {
  name: string;                // Descriptive name (1-200 chars)
  preset_id?: number;          // Link to preset (optional)
  run_id?: number;             // Link to run (optional)
  frequency: string;           // Monitoring frequency
  enabled: boolean;            // Active status (default: true)
}
```

**Frequency Options:**
- `"daily"` - Once per day (EOD)
- `"intraday_1m"` - Every 1 minute
- `"intraday_5m"` - Every 5 minutes
- `"intraday_15m"` - Every 15 minutes
- `"intraday_30m"` - Every 30 minutes
- `"intraday_1h"` - Every hour

**Request Example:**

```javascript
// Add preset to watchlist
const response = await fetch('http://localhost:8000/watchlist', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "AAPL Bollinger Daily Check",
    preset_id: 42,
    frequency: "daily",
    enabled: true
  })
});
const data = await response.json();
```

```javascript
// Add run to watchlist for frequent monitoring
const response = await fetch('http://localhost:8000/watchlist', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "BTC Scalping 5min Watch",
    run_id: 123,
    frequency: "intraday_5m",
    enabled: true
  })
});
```

**Response Format:**

```json
{
  "id": 15,
  "name": "AAPL Bollinger Daily Check",
  "preset_id": 42,
  "run_id": null,
  "frequency": "daily",
  "enabled": true,
  "created_at": "2024-12-15T18:30:00",
  "last_run_at": null
}
```

**Validation:**

- **Required:** Either `preset_id` OR `run_id` must be provided (not both)
- **Preset/Run Must Exist:** Returns 404 if referenced preset/run not found

**Frontend UI Recommendations:**

1. **Add to Watchlist Button:**
   - Place on preset cards
   - Place on run detail pages
   - Quick action with minimal clicks

2. **Watchlist Entry Form:**
   - Name input (pre-filled with preset/run name)
   - Frequency dropdown with descriptions:
     - Daily - "Check once per day after market close"
     - 15min - "Monitor every 15 minutes during market hours"
   - Enable/Disable toggle
   - Preview: "This will run [Strategy] on [Ticker] every [Frequency]"

3. **Smart Defaults:**
   - Name: Auto-fill from preset/run
   - Frequency: Suggest based on interval
     - If interval is "1d" → Default to "daily"
     - If interval is "15m" → Default to "intraday_15m"

**Example Add to Watchlist Flow:**

```jsx
function AddToWatchlistButton({ preset }) {
  const [showDialog, setShowDialog] = useState(false);

  return (
    <>
      <button onClick={() => setShowDialog(true)}>
        Add to Watchlist
      </button>

      {showDialog && (
        <AddToWatchlistDialog
          preset={preset}
          onClose={() => setShowDialog(false)}
        />
      )}
    </>
  );
}

function AddToWatchlistDialog({ preset, onClose }) {
  const [name, setName] = useState(`${preset.ticker} ${preset.name} Watch`);
  const [frequency, setFrequency] = useState(
    preset.interval === '1d' ? 'daily' : 'intraday_15m'
  );
  const [enabled, setEnabled] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleAdd = async () => {
    setLoading(true);
    const response = await fetch('/watchlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        preset_id: preset.id,
        frequency,
        enabled
      })
    });

    if (response.ok) {
      toast.success('Added to watchlist!');
      onClose();
    }
    setLoading(false);
  };

  return (
    <Dialog onClose={onClose}>
      <h2>Add to Watchlist</h2>

      <Input
        label="Name"
        value={name}
        onChange={setName}
        placeholder="e.g., AAPL Bollinger Daily Check"
      />

      <Select
        label="Frequency"
        value={frequency}
        onChange={setFrequency}
        options={[
          { value: 'daily', label: 'Daily (once per day)' },
          { value: 'intraday_1m', label: 'Every 1 minute' },
          { value: 'intraday_5m', label: 'Every 5 minutes' },
          { value: 'intraday_15m', label: 'Every 15 minutes' },
          { value: 'intraday_30m', label: 'Every 30 minutes' },
          { value: 'intraday_1h', label: 'Every hour' }
        ]}
      />

      <Toggle
        label="Enabled"
        checked={enabled}
        onChange={setEnabled}
      />

      <PreviewPanel>
        <p>
          Will monitor <strong>{preset.strategy}</strong> on{' '}
          <strong>{preset.ticker}</strong> {frequency}.
        </p>
      </PreviewPanel>

      <button onClick={handleAdd} disabled={loading}>
        {loading ? 'Adding...' : 'Add to Watchlist'}
      </button>
    </Dialog>
  );
}
```

---

### 4.2 List Watchlist Entries - `GET /watchlist`

**Purpose:** Retrieve all watchlist entries.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled_only` | boolean | No | false | Only return enabled entries |

**Request Example:**

```javascript
// Get all watchlist entries
const response = await fetch('http://localhost:8000/watchlist');
const data = await response.json();
```

```javascript
// Get only enabled entries
const response = await fetch('http://localhost:8000/watchlist?enabled_only=true');
const data = await response.json();
```

**Response Format:**

```json
[
  {
    "id": 15,
    "name": "AAPL Bollinger Daily Check",
    "preset_id": 42,
    "run_id": null,
    "frequency": "daily",
    "enabled": true,
    "created_at": "2024-12-15T18:30:00",
    "last_run_at": "2024-12-15T21:00:00"
  },
  {
    "id": 12,
    "name": "BTC RSI 5min Monitor",
    "preset_id": null,
    "run_id": 123,
    "frequency": "intraday_5m",
    "enabled": false,
    "created_at": "2024-12-10T14:20:00",
    "last_run_at": "2024-12-14T16:45:00"
  }
]
```

**Frontend UI Recommendations:**

1. **Watchlist Dashboard:**
   - List view with toggle switches for enable/disable
   - Show: Name, Ticker (from preset/run), Frequency, Last run, Status
   - Color indicators: Green (enabled), Gray (disabled)
   - Quick actions: Enable/Disable, View Details, Delete

2. **Status Indicators:**
   - Last run timestamp with relative time ("5 minutes ago")
   - Next scheduled run countdown
   - Activity history (optional)

3. **Bulk Actions:**
   - Select multiple entries
   - Enable/Disable all selected
   - Delete selected

**Example Watchlist View:**

```jsx
function WatchlistDashboard() {
  const [entries, setEntries] = useState([]);
  const [showEnabledOnly, setShowEnabledOnly] = useState(false);

  useEffect(() => {
    fetchWatchlist();
  }, [showEnabledOnly]);

  const fetchWatchlist = async () => {
    const params = showEnabledOnly ? '?enabled_only=true' : '';
    const response = await fetch(`/watchlist${params}`);
    const data = await response.json();
    setEntries(data);
  };

  const toggleEnabled = async (entryId, enabled) => {
    await fetch(`/watchlist/${entryId}?enabled=${!enabled}`, {
      method: 'PATCH'
    });
    fetchWatchlist();
  };

  return (
    <div className="watchlist-dashboard">
      <header>
        <h1>Watchlist</h1>
        <Toggle
          label="Show enabled only"
          checked={showEnabledOnly}
          onChange={setShowEnabledOnly}
        />
      </header>

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Frequency</th>
            <th>Last Run</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(entry => (
            <WatchlistRow
              key={entry.id}
              entry={entry}
              onToggle={toggleEnabled}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function WatchlistRow({ entry, onToggle }) {
  return (
    <tr className={entry.enabled ? 'enabled' : 'disabled'}>
      <td>
        <strong>{entry.name}</strong>
        <br />
        <small>
          {entry.preset_id ? `Preset #${entry.preset_id}` : `Run #${entry.run_id}`}
        </small>
      </td>
      <td>
        <FrequencyBadge frequency={entry.frequency} />
      </td>
      <td>
        {entry.last_run_at ? (
          <RelativeTime timestamp={entry.last_run_at} />
        ) : (
          <span className="muted">Never</span>
        )}
      </td>
      <td>
        <Toggle
          checked={entry.enabled}
          onChange={() => onToggle(entry.id, entry.enabled)}
        />
      </td>
      <td>
        <IconButton icon="view" onClick={() => viewEntry(entry.id)} />
        <IconButton icon="delete" onClick={() => deleteEntry(entry.id)} />
      </td>
    </tr>
  );
}
```

---

### 4.3 Get Watchlist Entry - `GET /watchlist/{entry_id}`

**Purpose:** Retrieve details of a specific watchlist entry.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Watchlist entry ID |

**Request Example:**

```javascript
const response = await fetch('http://localhost:8000/watchlist/15');
const data = await response.json();
```

**Response Format:**

Same as list response, but single object.

---

### 4.4 Update Watchlist Entry - `PATCH /watchlist/{entry_id}`

**Purpose:** Enable or disable a watchlist entry.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | integer | Yes | Watchlist entry ID |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `enabled` | boolean | Yes | true to enable, false to disable |

**Request Example:**

```javascript
// Disable watchlist entry
const response = await fetch('http://localhost:8000/watchlist/15?enabled=false', {
  method: 'PATCH'
});
const data = await response.json();
```

**Response Format:**

```json
{
  "success": true,
  "message": "Watchlist entry 15 updated successfully"
}
```

---

### 4.5 Delete Watchlist Entry - `DELETE /watchlist/{entry_id}`

**Purpose:** Remove a watchlist entry.

**Request Example:**

```javascript
const response = await fetch('http://localhost:8000/watchlist/15', {
  method: 'DELETE'
});
const data = await response.json();
```

**Response Format:**

```json
{
  "success": true,
  "message": "Watchlist entry 15 deleted successfully"
}
```

---

## 5. Optimization Endpoint

The Optimization endpoint performs **parameter grid search** to find the best-performing parameter combinations.

### 5.1 Optimize Strategy - `POST /optimize`

**Purpose:** Test multiple parameter combinations and rank by performance.

**Use Cases:**
- Find optimal strategy parameters
- Parameter sensitivity analysis
- Strategy robustness testing
- Hyperparameter tuning

**Request Body:**

```typescript
interface OptimizationRequest {
  ticker: string;              // Stock symbol
  strategy: string;            // Strategy module name
  start_date?: string;         // "2024-01-01" (optional)
  end_date?: string;           // "2024-12-31" (optional)
  interval: string;            // "1d", "1h", etc. (default: "1d")
  cash: number;                // Starting cash (default: 10000)
  optimization_params: {       // Parameter grid to test
    [param_name: string]: number[];
  };
}
```

**Request Example:**

```javascript
// Optimize Bollinger Bands parameters
const response = await fetch('http://localhost:8000/optimize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: "AAPL",
    strategy: "bollinger_bands_strategy",
    start_date: "2024-01-01",
    end_date: "2024-12-31",
    interval: "1d",
    cash: 10000,
    optimization_params: {
      period: [10, 15, 20, 25, 30],
      devfactor: [1.5, 2.0, 2.5, 3.0]
    }
  })
});
const data = await response.json();
```

**Parameter Grid Explanation:**

- Above example tests **5 × 4 = 20 combinations**:
  - period=10, devfactor=1.5
  - period=10, devfactor=2.0
  - period=10, devfactor=2.5
  - ... (20 total)

**Response Format:**

```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "total_combinations": 20,
  "top_results": [
    {
      "parameters": {
        "period": 20,
        "devfactor": 2.0
      },
      "pnl": 1850.30,
      "return_pct": 18.50,
      "sharpe_ratio": 1.85,
      "start_value": 10000.0,
      "end_value": 11850.30
    },
    {
      "parameters": {
        "period": 15,
        "devfactor": 2.5
      },
      "pnl": 1620.45,
      "return_pct": 16.20,
      "sharpe_ratio": 1.62,
      "start_value": 10000.0,
      "end_value": 11620.45
    },
    {
      "parameters": {
        "period": 25,
        "devfactor": 2.0
      },
      "pnl": 1450.75,
      "return_pct": 14.51,
      "sharpe_ratio": 1.48,
      "start_value": 10000.0,
      "end_value": 11450.75
    }
    // ... more results (sorted by PNL descending)
  ]
}
```

**Performance Notes:**

- **Execution Time:** Proportional to `total_combinations`
- Small grids (10-50 combinations): ~10-30 seconds
- Medium grids (50-200 combinations): ~1-3 minutes
- Large grids (200+ combinations): 3+ minutes
- **Recommendation:** Keep combinations under 100 for responsive UX

**Frontend UI Recommendations:**

1. **Optimization Setup Form:**
   - Strategy selector
   - Ticker input
   - Date range picker
   - Parameter grid builder:
     - For each optimizable parameter:
       - Range slider (min, max, step)
       - Or manual value entry (comma-separated)
     - Show total combinations count
     - Warning if > 100 combinations

2. **Progress Indicator:**
   - Modal with progress bar
   - "Testing X of Y combinations..."
   - Estimated time remaining
   - Cancel button

3. **Results View:**
   - **Table:** Rank, Parameters, PNL, Return %, Sharpe Ratio
   - Sort by any column
   - Color gradient for PNL (best = green, worst = red)
   - Actions per result:
     - "Run Full Backtest" → Include chart data
     - "Save as Preset" → Quick preset creation
     - "Add to Watchlist" → Monitoring

4. **Visualization:**
   - Heatmap: X-axis = param1, Y-axis = param2, Color = PNL
   - 3D surface plot for 2-parameter optimizations
   - Parameter sensitivity chart

**Example Optimization Flow:**

```jsx
function OptimizationWizard() {
  const [config, setConfig] = useState({
    ticker: 'AAPL',
    strategy: 'bollinger_bands_strategy',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    interval: '1d',
    cash: 10000,
    optimization_params: {}
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleOptimize = async () => {
    setLoading(true);
    setProgress(0);

    // Simulate progress (actual API doesn't provide real-time progress)
    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 5, 95));
    }, 500);

    const response = await fetch('/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    clearInterval(progressInterval);
    setProgress(100);

    const data = await response.json();
    setResults(data);
    setLoading(false);
  };

  if (loading) {
    return (
      <ProgressModal
        progress={progress}
        message={`Testing ${config.optimization_params}...`}
      />
    );
  }

  if (results) {
    return <OptimizationResults results={results} />;
  }

  return (
    <div className="optimization-wizard">
      <h1>Strategy Optimization</h1>

      <ConfigSection config={config} onChange={setConfig} />

      <ParameterGrid
        strategy={config.strategy}
        params={config.optimization_params}
        onChange={(params) => setConfig({ ...config, optimization_params: params })}
      />

      <CombinationsWarning count={calculateCombinations(config.optimization_params)} />

      <button onClick={handleOptimize}>
        Run Optimization
      </button>
    </div>
  );
}

function ParameterGrid({ strategy, params, onChange }) {
  const [strategyInfo, setStrategyInfo] = useState(null);

  useEffect(() => {
    fetchStrategyInfo();
  }, [strategy]);

  const fetchStrategyInfo = async () => {
    const response = await fetch(`/strategies/${strategy}`);
    const data = await response.json();
    setStrategyInfo(data.strategy);
  };

  if (!strategyInfo) return <Loader />;

  return (
    <div className="parameter-grid">
      <h2>Parameter Grid</h2>
      {strategyInfo.optimizable_params.map(param => (
        <ParameterRange
          key={param.name}
          param={param}
          values={params[param.name] || []}
          onChange={(values) => onChange({
            ...params,
            [param.name]: values
          })}
        />
      ))}
    </div>
  );
}

function ParameterRange({ param, values, onChange }) {
  const [mode, setMode] = useState('range'); // 'range' or 'manual'

  const handleRangeChange = (min, max, step) => {
    const range = [];
    for (let i = min; i <= max; i += step) {
      range.push(i);
    }
    onChange(range);
  };

  const handleManualChange = (text) => {
    const values = text.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v));
    onChange(values);
  };

  return (
    <div className="parameter-range">
      <h3>{param.name}</h3>
      <p className="description">{param.description}</p>

      <TabGroup value={mode} onChange={setMode}>
        <Tab value="range">Range</Tab>
        <Tab value="manual">Manual</Tab>
      </TabGroup>

      {mode === 'range' ? (
        <RangeInputs
          min={param.min}
          max={param.max}
          step={param.step}
          onChange={handleRangeChange}
        />
      ) : (
        <Input
          placeholder="e.g., 10, 15, 20, 25, 30"
          onChange={handleManualChange}
        />
      )}

      <div className="values-preview">
        <strong>Values:</strong> {values.join(', ')}
        <span className="count">({values.length} values)</span>
      </div>
    </div>
  );
}

function OptimizationResults({ results }) {
  const [sortBy, setSortBy] = useState('pnl');
  const [sortedResults, setSortedResults] = useState(results.top_results);

  useEffect(() => {
    const sorted = [...results.top_results].sort((a, b) => {
      return b[sortBy] - a[sortBy];
    });
    setSortedResults(sorted);
  }, [sortBy, results]);

  return (
    <div className="optimization-results">
      <header>
        <h1>Optimization Results</h1>
        <p>Tested {results.total_combinations} combinations</p>
        <p>
          {results.ticker} | {results.strategy} |
          {results.start_date} to {results.end_date}
        </p>
      </header>

      <SortBar value={sortBy} onChange={setSortBy} />

      <table className="results-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Parameters</th>
            <th>PNL</th>
            <th>Return %</th>
            <th>Sharpe Ratio</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sortedResults.map((result, index) => (
            <ResultRow
              key={index}
              rank={index + 1}
              result={result}
              bestPnl={sortedResults[0].pnl}
            />
          ))}
        </tbody>
      </table>

      <Visualization results={sortedResults} />
    </div>
  );
}

function ResultRow({ rank, result, bestPnl }) {
  const pnlRatio = result.pnl / bestPnl;
  const bgColor = `rgba(0, 255, 0, ${pnlRatio * 0.3})`;

  return (
    <tr style={{ backgroundColor: bgColor }}>
      <td className="rank">#{rank}</td>
      <td className="parameters">
        {Object.entries(result.parameters).map(([key, value]) => (
          <span key={key} className="param">
            {key}={value}
          </span>
        ))}
      </td>
      <td className={result.pnl >= 0 ? 'positive' : 'negative'}>
        ${result.pnl.toFixed(2)}
      </td>
      <td>{result.return_pct.toFixed(2)}%</td>
      <td>{result.sharpe_ratio?.toFixed(2) || 'N/A'}</td>
      <td>
        <IconButton icon="chart" onClick={() => runFullBacktest(result)} />
        <IconButton icon="save" onClick={() => saveAsPreset(result)} />
        <IconButton icon="watch" onClick={() => addToWatchlist(result)} />
      </td>
    </tr>
  );
}
```

---

## 6. Frontend Implementation Patterns

### 6.1 State Management

**Recommended Approach:**

```javascript
// Use context for global state
const BacktestContext = createContext();

export function BacktestProvider({ children }) {
  const [runs, setRuns] = useState([]);
  const [presets, setPresets] = useState([]);
  const [watchlist, setWatchlist] = useState([]);

  const fetchRuns = async () => {
    const response = await fetch('/runs');
    const data = await response.json();
    setRuns(data.runs);
  };

  const fetchPresets = async () => {
    const response = await fetch('/presets');
    const data = await response.json();
    setPresets(data.presets);
  };

  const fetchWatchlist = async () => {
    const response = await fetch('/watchlist');
    const data = await response.json();
    setWatchlist(data);
  };

  useEffect(() => {
    fetchRuns();
    fetchPresets();
    fetchWatchlist();
  }, []);

  return (
    <BacktestContext.Provider value={{
      runs,
      presets,
      watchlist,
      refreshRuns: fetchRuns,
      refreshPresets: fetchPresets,
      refreshWatchlist: fetchWatchlist
    }}>
      {children}
    </BacktestContext.Provider>
  );
}
```

---

### 6.2 API Client Abstraction

**Create a typed API client:**

```typescript
// api/client.ts
class BacktestAPI {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getRuns(filters?: {
    ticker?: string;
    strategy?: string;
    limit?: number;
    offset?: number;
  }) {
    const params = new URLSearchParams(filters as any);
    const response = await fetch(`${this.baseUrl}/runs?${params}`);
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getRunDetail(runId: number) {
    const response = await fetch(`${this.baseUrl}/runs/${runId}`);
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async replayRun(runId: number, overrides: ReplayRunRequest) {
    const response = await fetch(`${this.baseUrl}/runs/${runId}/replay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(overrides)
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async createPreset(preset: CreatePresetRequest) {
    const response = await fetch(`${this.baseUrl}/presets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(preset)
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getSnapshot(request: SnapshotRequest) {
    const response = await fetch(`${this.baseUrl}/snapshot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async createWatchlistEntry(entry: CreateWatchlistRequest) {
    const response = await fetch(`${this.baseUrl}/watchlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry)
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async optimize(request: OptimizationRequest) {
    const response = await fetch(`${this.baseUrl}/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }
}

export const api = new BacktestAPI('http://localhost:8000');
```

---

### 6.3 Caching Strategy

**Use SWR or React Query for data fetching:**

```javascript
import useSWR from 'swr';

function useRuns(filters) {
  const params = new URLSearchParams(filters);
  const { data, error, mutate } = useSWR(
    `/runs?${params}`,
    fetcher,
    { refreshInterval: 60000 } // Refresh every minute
  );

  return {
    runs: data?.runs || [],
    loading: !data && !error,
    error,
    refresh: mutate
  };
}

function useSnapshot(config, enabled) {
  const { data, error } = useSWR(
    enabled ? ['/snapshot', config] : null,
    () => api.getSnapshot(config),
    { refreshInterval: 300000 } // 5 minutes
  );

  return {
    snapshot: data,
    loading: !data && !error,
    error
  };
}
```

---

## 7. Error Handling

### 7.1 Common Error Codes

| Status Code | Meaning | Example Scenario |
|-------------|---------|------------------|
| 400 | Bad Request | Invalid parameters, missing required fields |
| 404 | Not Found | Strategy not found, run/preset doesn't exist |
| 409 | Conflict | Preset with same name already exists |
| 500 | Server Error | Backtest crashed, database error |

### 7.2 Error Response Format

```json
{
  "detail": "Strategy 'invalid_strategy' not found"
}
```

### 7.3 Frontend Error Handling

```javascript
async function safeApiCall(apiFunction, errorHandler) {
  try {
    return await apiFunction();
  } catch (error) {
    const message = error.message || 'An unexpected error occurred';

    // Log to monitoring service
    console.error('API Error:', error);

    // Show user-friendly message
    if (errorHandler) {
      errorHandler(message);
    } else {
      toast.error(message);
    }

    return null;
  }
}

// Usage
const runs = await safeApiCall(
  () => api.getRuns({ ticker: 'AAPL' }),
  (error) => showErrorDialog(error)
);
```

---

## Appendix: Complete Type Definitions

```typescript
// Complete TypeScript interfaces for all endpoints

interface BacktestRequest {
  ticker: string;
  strategy: string;
  start_date?: string;
  end_date?: string;
  interval: string;
  cash: number;
  parameters?: Record<string, number>;
  include_chart_data?: boolean;
  columnar_format?: boolean;
}

interface BacktestResponse {
  success: boolean;
  ticker: string;
  strategy: string;
  start_value: number;
  end_value: number;
  pnl: number;
  return_pct: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_trades: number;
  interval: string;
  start_date: string;
  end_date: string;
  advanced_metrics?: Record<string, any>;
  chart_data?: any;
}

interface SavedRunSummaryResponse {
  id: number;
  ticker: string;
  strategy: string;
  interval: string;
  pnl?: number;
  return_pct?: number;
  created_at: string;
}

interface SavedRunDetailResponse extends SavedRunSummaryResponse {
  parameters: Record<string, number>;
  start_date: string;
  end_date: string;
  cash: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_trades?: number;
  winning_trades?: number;
  losing_trades?: number;
}

interface ReplayRunRequest {
  start_date?: string;
  end_date?: string;
  interval?: string;
  cash?: number;
  parameters?: Record<string, number>;
}

interface CreatePresetRequest {
  name: string;
  ticker: string;
  strategy: string;
  parameters: Record<string, number>;
  interval: string;
  notes?: string;
}

interface PresetResponse {
  id: number;
  name: string;
  ticker: string;
  strategy: string;
  parameters: Record<string, number>;
  interval: string;
  notes?: string;
  created_at: string;
}

interface SnapshotRequest {
  ticker: string;
  strategy: string;
  parameters?: Record<string, number>;
  interval: string;
  lookback_bars: number;
  cash: number;
}

interface SnapshotPositionState {
  in_position: boolean;
  position_type?: 'long' | 'short';
  entry_price?: number;
  current_price?: number;
  size?: number;
  unrealized_pnl?: number;
}

interface SnapshotResponse {
  success: boolean;
  ticker: string;
  strategy: string;
  interval: string;
  lookback_bars: number;
  last_bar: {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  };
  indicators: Record<string, any>;
  position_state: SnapshotPositionState;
  recent_trades: Array<{
    date: string;
    type: string;
    price: number;
    size: number;
    pnl?: number;
    commission: number;
  }>;
  portfolio_value: number;
  cash: number;
  timestamp: string;
}

interface CreateWatchlistRequest {
  name: string;
  preset_id?: number;
  run_id?: number;
  frequency: string;
  enabled: boolean;
}

interface WatchlistEntryResponse {
  id: number;
  name: string;
  preset_id?: number;
  run_id?: number;
  frequency: string;
  enabled: boolean;
  created_at: string;
  last_run_at?: string;
}

interface OptimizationRequest {
  ticker: string;
  strategy: string;
  start_date?: string;
  end_date?: string;
  interval: string;
  cash: number;
  optimization_params: Record<string, number[]>;
}

interface OptimizationResult {
  parameters: Record<string, number>;
  pnl: number;
  return_pct: number;
  sharpe_ratio?: number;
  start_value: number;
  end_value: number;
}

interface OptimizationResponse {
  success: boolean;
  ticker: string;
  strategy: string;
  interval: string;
  start_date: string;
  end_date: string;
  total_combinations: number;
  top_results: OptimizationResult[];
}
```

---

## Quick Reference: All Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/runs` | List all saved backtest runs |
| GET | `/runs/{id}` | Get run details |
| POST | `/runs/{id}/replay` | Replay run with overrides |
| POST | `/presets` | Create new preset |
| GET | `/presets` | List all presets |
| DELETE | `/presets/{id}` | Delete preset |
| POST | `/presets/{id}/backtest` | Run backtest from preset |
| POST | `/snapshot` | Get real-time strategy snapshot |
| POST | `/watchlist` | Add watchlist entry |
| GET | `/watchlist` | List watchlist entries |
| GET | `/watchlist/{id}` | Get watchlist entry details |
| PATCH | `/watchlist/{id}` | Update watchlist entry |
| DELETE | `/watchlist/{id}` | Delete watchlist entry |
| POST | `/optimize` | Optimize strategy parameters |

---

**End of Guide**
