# StrategyBuilder API Documentation v2.0

**Base URL:** `http://localhost:8000`
**Last Updated:** January 2026
**Breaking Changes:** Input validation added, CORS restrictions enabled

---

## 🔴 CRITICAL CHANGES

### Input Validation (NEW)
All request models now validate input and return **422 Unprocessable Entity** for invalid data:
- Ticker symbols must be alphanumeric with hyphens/dots only
- Dates must be in `YYYY-MM-DD` format
- Cash values must be > 0
- Intervals must be from predefined list

### CORS Configuration (CHANGED)
CORS now restricted to specific origins (default: `localhost:3000`, `localhost:8080`).
Set `CORS_ORIGINS` environment variable for production.

---

## 📋 ENDPOINTS BY DOMAIN

## 1. SYSTEM

### GET `/`
**Description:** API root information
**Request:** None
**Response:**
```json
{
  "message": "StrategyBuilder API v2.0.0",
  "status": "operational",
  "docs": "/docs",
  "endpoints": [...]
}
```

### GET `/health`
**Description:** Health check
**Request:** None
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-25T10:30:00"
}
```

### GET `/parameters/default`
**Description:** Get default strategy parameters
**Request:** None
**Response:**
```json
{
  "cash": 10000.0,
  "commission": 0.001,
  "position_size_pct": 95.0
}
```

---

## 2. STRATEGIES

### GET `/strategies`
**Description:** List all available strategies
**Request:** None
**Response:**
```json
{
  "success": true,
  "count": 12,
  "strategies": [
    {
      "module": "bollinger_bands_strategy",
      "class_name": "Bollinger_three",
      "description": ""
    }
  ]
}
```

### GET `/strategies/{strategy_name}`
**Description:** Get detailed strategy information
**Parameters:**
- `strategy_name` (path): Strategy module name

**Response:**
```json
{
  "module": "bollinger_bands_strategy",
  "class_name": "Bollinger_three",
  "description": "",
  "parameters": {
    "period": 20,
    "devfactor": 2
  },
  "optimizable_params": {
    "period": [10, 50],
    "devfactor": [1.0, 3.0]
  }
}
```

---

## 3. BACKTESTS

### POST `/backtest`
**Description:** Run strategy backtest on single ticker
**Request Body:**
```typescript
{
  ticker: string;           // 1-10 chars, alphanumeric/hyphens/dots, UPPERCASE
  strategy: string;         // 1-100 chars
  start_date?: string;      // YYYY-MM-DD format
  end_date?: string;        // YYYY-MM-DD format
  interval?: string;        // Default: "1d", Valid: 1m|5m|15m|30m|1h|1d|1wk|1mo
  cash?: number;            // Default: 10000, must be > 0
  parameters?: {            // Strategy-specific parameters
    [key: string]: number;
  };
  include_chart_data?: boolean;  // Default: false
  columnar_format?: boolean;     // Default: true
}
```

**Example Request:**
```json
{
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000,
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  }
}
```

**Response:**
```typescript
{
  success: boolean;
  ticker: string;
  strategy: string;
  start_value: number;
  end_value: number;
  pnl: number;
  return_pct: number;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  total_trades: number;
  interval: string;
  start_date: string;
  end_date: string;
  advanced_metrics?: {
    winning_trades?: number;
    losing_trades?: number;
    win_rate?: number;
    // ... more metrics
  };
  chart_data?: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }> | {
    date: string[];
    open: number[];
    high: number[];
    // ... columnar format
  };
}
```

**Example Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_value": 10000.0,
  "end_value": 10998.16,
  "pnl": 998.16,
  "return_pct": 9.98,
  "sharpe_ratio": 1.23,
  "max_drawdown": -2.5,
  "total_trades": 6,
  "interval": "1d",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31"
}
```

**Validation Errors (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "ticker"],
      "msg": "Value error, Ticker must contain only alphanumeric characters, hyphens, and dots"
    },
    {
      "type": "value_error",
      "loc": ["body", "start_date"],
      "msg": "Value error, Date must be in YYYY-MM-DD format"
    },
    {
      "type": "greater_than",
      "loc": ["body", "cash"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

---

## 4. OPTIMIZATIONS

### POST `/optimize`
**Description:** Optimize strategy parameters across ranges
**Request Body:**
```typescript
{
  ticker: string;           // 1-10 chars, alphanumeric/hyphens/dots, UPPERCASE
  strategy: string;         // 1-100 chars
  start_date: string;       // YYYY-MM-DD format, REQUIRED
  end_date: string;         // YYYY-MM-DD format, REQUIRED
  interval?: string;        // Default: "1d"
  cash?: number;            // Default: 10000, must be > 0
  param_ranges: {           // REQUIRED, not empty
    [paramName: string]: number[];  // Each param: max 100 values
  };
}
```

**Example Request:**
```json
{
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000,
  "param_ranges": {
    "period": [20, 25, 30],
    "devfactor": [1.5, 2.0, 2.5]
  }
}
```

**Response:**
```typescript
{
  success: boolean;
  ticker: string;
  strategy: string;
  interval: string;
  start_date: string;
  end_date: string;
  total_combinations: number;
  top_results: Array<{
    parameters: { [key: string]: number };
    pnl: number;
    return_pct: number;
    sharpe_ratio: number | null;
    start_value: number;
    end_value: number;
  }>;
}
```

**Example Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "interval": "1d",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "total_combinations": 9,
  "top_results": [
    {
      "parameters": {"period": 20, "devfactor": 2.0},
      "pnl": 998.16,
      "return_pct": 9.98,
      "sharpe_ratio": 1.23,
      "start_value": 10000.0,
      "end_value": 10998.16
    }
  ]
}
```

---

## 5. MARKET SCANS

### POST `/market-scan`
**Description:** Run strategy across multiple tickers to find top performers
**Request Body:**
```typescript
{
  tickers?: string[];       // OPTIONAL: Array of ticker symbols (defaults to S&P 500)
  strategy: string;         // Strategy name, REQUIRED
  start_date: string;       // YYYY-MM-DD format, REQUIRED
  end_date: string;         // YYYY-MM-DD format, REQUIRED
  interval?: string;        // Default: "1d"
  cash?: number;            // Default: 10000
  parameters?: {
    [key: string]: number;
  };
  min_return_pct?: number;  // Filter results
  min_sharpe_ratio?: number;
}
```

**⚠️ IMPORTANT:** The `tickers` field is now **OPTIONAL**. If not provided or empty, the system automatically uses the S&P 500 ticker list (fetched from Wikipedia or fallback to `data/tickers.txt`).

**Example Request (with custom tickers):**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000,
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  }
}
```

**Example Request (S&P 500 scan - no tickers specified):**
```json
{
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000,
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  }
}
```

**Response:**
```typescript
{
  success: boolean;
  strategy: string;
  start_date: string;
  end_date: string;
  interval: string;
  total_tickers: number;
  successful_scans: number;
  failed_scans: number;
  results: Array<{
    ticker: string;
    success: boolean;
    pnl?: number;
    return_pct?: number;
    sharpe_ratio?: number;
    max_drawdown?: number;
    total_trades?: number;
    error?: string;
  }>;
  top_performers: Array<{...}>;  // Same as results, sorted by return_pct
}
```

**Example Response:**
```json
{
  "success": true,
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "total_tickers": 3,
  "successful_scans": 3,
  "failed_scans": 0,
  "results": [
    {
      "ticker": "AAPL",
      "success": true,
      "pnl": 998.16,
      "return_pct": 9.98,
      "sharpe_ratio": 1.23,
      "max_drawdown": -2.5,
      "total_trades": 6
    }
  ],
  "top_performers": [...]
}
```

---

## 6. RUN HISTORY

### GET `/runs`
**Description:** List saved backtest runs with pagination
**Query Parameters:**
- `ticker` (optional): Filter by ticker symbol
- `strategy` (optional): Filter by strategy name
- `limit` (optional): Max results, 1-1000, default 100
- `offset` (optional): Skip results, ≥0, default 0

**Response:**
```typescript
{
  success: boolean;
  total_count: number;
  count: number;
  limit: number;
  offset: number;
  runs: Array<{
    id: number;
    ticker: string;
    strategy: string;
    interval: string;
    pnl?: number;
    return_pct?: number;
    created_at: string;
  }>;
}
```

**Example Request:**
`GET /runs?ticker=AAPL&limit=10&offset=0`

**Example Response:**
```json
{
  "success": true,
  "total_count": 25,
  "count": 10,
  "limit": 10,
  "offset": 0,
  "runs": [
    {
      "id": 1,
      "ticker": "AAPL",
      "strategy": "bollinger_bands_strategy",
      "interval": "1d",
      "pnl": 998.16,
      "return_pct": 9.98,
      "created_at": "2026-01-25T10:30:00"
    }
  ]
}
```

### GET `/runs/{run_id}`
**Description:** Get complete details of a saved run
**Parameters:**
- `run_id` (path): Run ID

**Response:**
```typescript
{
  id: number;
  ticker: string;
  strategy: string;
  parameters: { [key: string]: number };
  start_date: string;
  end_date: string;
  interval: string;
  cash: number;
  pnl?: number;
  return_pct?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_trades?: number;
  winning_trades?: number;
  losing_trades?: number;
  created_at: string;
}
```

### POST `/runs/{run_id}/replay`
**Description:** Replay a saved run with optional parameter overrides
**Parameters:**
- `run_id` (path): Run ID

**Request Body:**
```typescript
{
  start_date?: string;      // YYYY-MM-DD format
  end_date?: string;        // YYYY-MM-DD format
  interval?: string;
  cash?: number;
  parameters?: {
    [key: string]: number;
  };
}
```

**Response:** Same as `/backtest` endpoint (BacktestResponse)

---

## 7. PRESETS

### POST `/presets` ✨ Status: 201
**Description:** Create reusable strategy configuration
**Request Body:**
```typescript
{
  name: string;             // 1-100 chars, REQUIRED
  description?: string;     // Max 500 chars
  strategy: string;         // 1-100 chars, REQUIRED
  parameters: {             // REQUIRED
    [key: string]: number;
  };
  interval?: string;        // Default: "1d", Valid: 1m|5m|15m|30m|1h|1d|1wk|1mo
  cash?: number;            // Default: 10000, must be > 0
}
```

**Example Request:**
```json
{
  "name": "Conservative Bollinger",
  "description": "Bollinger Bands with 2.5 std dev",
  "strategy": "bollinger_bands_strategy",
  "parameters": {
    "period": 20,
    "devfactor": 2.5
  },
  "interval": "1d",
  "cash": 10000
}
```

**Response:**
```typescript
{
  id: number;
  name: string;
  description: string | null;
  strategy: string;
  parameters: { [key: string]: number };
  interval: string;
  cash: number;
  created_at: string;
  updated_at: string;
}
```

### GET `/presets`
**Description:** List all presets with optional filters
**Query Parameters:**
- `strategy` (optional): Filter by strategy name
- `limit` (optional): Max results, 1-500, default 100
- `offset` (optional): Skip results, ≥0, default 0

**Response:**
```typescript
{
  success: boolean;
  count: number;
  presets: Array<{
    id: number;
    name: string;
    description: string | null;
    strategy: string;
    parameters: { [key: string]: number };
    interval: string;
    cash: number;
    created_at: string;
    updated_at: string;
  }>;
}
```

### GET `/presets/{preset_id}`
**Description:** Get specific preset by ID
**Parameters:**
- `preset_id` (path): Preset ID

**Response:** Same as POST response

### PATCH `/presets/{preset_id}`
**Description:** Update specific preset fields
**Parameters:**
- `preset_id` (path): Preset ID

**Request Body:**
```typescript
{
  name?: string;            // 1-100 chars
  description?: string;     // Max 500 chars
  parameters?: {
    [key: string]: number;
  };
  interval?: string;        // Valid: 1m|5m|15m|30m|1h|1d|1wk|1mo
  cash?: number;            // Must be > 0
}
```

**Response:** Updated preset (same as POST response)

### DELETE `/presets/{preset_id}` ✨ Status: 204
**Description:** Delete a preset
**Parameters:**
- `preset_id` (path): Preset ID

**Response:** No content (204)

---

## 8. WATCHLISTS

### POST `/watchlists` ✨ Status: 201
**Description:** Create watchlist to track strategy on a ticker
**Request Body:**
```typescript
{
  name: string;             // REQUIRED
  description?: string;
  ticker: string;           // REQUIRED
  strategy: string;         // REQUIRED
  parameters: {             // REQUIRED
    [key: string]: number;
  };
  interval?: string;        // Default: "1d"
  cash?: number;            // Default: 10000
  active?: boolean;         // Default: true
}
```

**Example Request:**
```json
{
  "name": "AAPL Bollinger Watch",
  "description": "Track AAPL with Bollinger Bands",
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  },
  "interval": "1d",
  "cash": 10000,
  "active": true
}
```

**Response:**
```typescript
{
  id: number;
  name: string;
  description: string | null;
  ticker: string;
  strategy: string;
  parameters: { [key: string]: number };
  interval: string;
  cash: number;
  active: boolean;
  current_value?: number;
  pnl?: number;
  return_pct?: number;
  created_at: string;
  last_updated: string;
}
```

### GET `/watchlists`
**Description:** List all watchlists
**Query Parameters:**
- `active_only` (optional): Filter active only, default false
- `ticker` (optional): Filter by ticker symbol

**Response:**
```typescript
{
  success: boolean;
  count: number;
  watchlists: Array<{
    id: number;
    name: string;
    description: string | null;
    ticker: string;
    strategy: string;
    parameters: { [key: string]: number };
    interval: string;
    cash: number;
    active: boolean;
    current_value?: number;
    pnl?: number;
    return_pct?: number;
    created_at: string;
    last_updated: string;
  }>;
}
```

### GET `/watchlists/{watchlist_id}`
**Description:** Get watchlist with all positions and stats
**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Response:**
```typescript
{
  watchlist: {
    id: number;
    name: string;
    // ... same as above
  };
  open_positions: Array<{
    id: number;
    watchlist_id: number;
    position_type: "LONG" | "SHORT";
    entry_date: string;
    entry_price: number;
    size: number;
    exit_date: string | null;
    exit_price: number | null;
    pnl: number | null;
    status: "OPEN" | "CLOSED";
  }>;
  closed_positions: Array<{...}>;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
}
```

### PATCH `/watchlists/{watchlist_id}`
**Description:** Update watchlist fields
**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Request Body:**
```typescript
{
  name?: string;
  description?: string;
  active?: boolean;
}
```

**Response:** Updated watchlist

### DELETE `/watchlists/{watchlist_id}` ✨ Status: 204
**Description:** Delete watchlist and all its positions
**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Response:** No content (204)

---

## 9. PORTFOLIOS

### POST `/portfolios` ✨ Status: 201
**Description:** Create portfolio with stock holdings
**Request Body:**
```typescript
{
  name: string;             // REQUIRED
  description?: string;
  holdings: Array<{         // REQUIRED, min 1 holding
    ticker: string;         // REQUIRED
    shares: number;         // REQUIRED
    weight?: number;        // Portfolio weight 0-1
  }>;
}
```

**Example Request:**
```json
{
  "name": "Tech Portfolio",
  "description": "Major tech stocks",
  "holdings": [
    {
      "ticker": "AAPL",
      "shares": 100,
      "weight": 0.5
    },
    {
      "ticker": "MSFT",
      "shares": 50,
      "weight": 0.5
    }
  ]
}
```

**Response:**
```typescript
{
  id: number;
  name: string;
  description: string | null;
  holdings: Array<{
    ticker: string;
    shares: number;
    weight?: number;
  }>;
  total_stocks: number;
  created_at: string;
  updated_at: string;
}
```

### GET `/portfolios`
**Description:** List all portfolios
**Response:**
```typescript
{
  success: boolean;
  count: number;
  portfolios: Array<{
    id: number;
    name: string;
    description: string | null;
    holdings: Array<{...}>;
    total_stocks: number;
    created_at: string;
    updated_at: string;
  }>;
}
```

### GET `/portfolios/{portfolio_id}`
**Description:** Get specific portfolio
**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Response:** Same as POST response

### PATCH `/portfolios/{portfolio_id}`
**Description:** Update portfolio fields
**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Request Body:**
```typescript
{
  name?: string;
  description?: string;
  holdings?: Array<{
    ticker: string;
    shares: number;
    weight?: number;
  }>;
}
```

**Response:** Updated portfolio

### DELETE `/portfolios/{portfolio_id}` ✨ Status: 204
**Description:** Delete a portfolio
**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Response:** No content (204)

### POST `/portfolios/{portfolio_id}/backtest`
**Description:** Backtest all stocks in portfolio with a preset strategy
**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Request Body:**
```typescript
{
  preset_id: number;        // REQUIRED, preset to apply
  start_date: string;       // YYYY-MM-DD format, REQUIRED
  end_date: string;         // YYYY-MM-DD format, REQUIRED
  use_weights?: boolean;    // Default: false
}
```

**Example Request:**
```json
{
  "preset_id": 1,
  "start_date": "2024-07-01",
  "end_date": "2024-12-31",
  "use_weights": true
}
```

**Response:**
```typescript
{
  success: boolean;
  portfolio_name: string;
  strategy: string;
  weighted_pnl?: number;
  weighted_return_pct?: number;
  results: Array<{
    ticker: string;
    weight?: number;
    pnl: number;
    return_pct: number;
    sharpe_ratio?: number;
  }>;
}
```

---

## 10. LIVE MONITOR

### POST `/live-monitor`
**Description:** Get current prices for tickers (no strategy analysis)
**Request Body:**
```typescript
{
  tickers: string[];        // REQUIRED, max 50 items
}
```

**Example Request:**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

**Response:**
```typescript
{
  success: boolean;
  timestamp: string;
  prices: Array<{
    ticker: string;
    price?: number;
    change?: number;
    change_pct?: number;
    volume?: number;
    timestamp: string;
    error?: string;
  }>;
}
```

**Example Response:**
```json
{
  "success": true,
  "timestamp": "2026-01-25T10:30:00",
  "prices": [
    {
      "ticker": "AAPL",
      "price": 178.50,
      "change": 2.30,
      "change_pct": 1.31,
      "volume": 52430000,
      "timestamp": "2026-01-25T16:00:00"
    }
  ]
}
```

---

## 11. MARKET DATA

### POST `/market-data`
**Description:** Fetch historical price data with statistics
**Request Body:**
```typescript
{
  ticker: string;           // 1-10 chars, alphanumeric/hyphens/dots, UPPERCASE, REQUIRED
  period?: string;          // Default: "1mo", Valid: 1d|5d|1mo|3mo|6mo|1y|2y|5y|ytd|max
  interval?: string;        // Default: "1d", Valid: 1m|5m|15m|30m|1h|1d|1wk|1mo
}
```

**Example Request:**
```json
{
  "ticker": "AAPL",
  "period": "1mo",
  "interval": "1d"
}
```

**Response:**
```typescript
{
  success: boolean;
  ticker: string;
  period: string;
  interval: string;
  data_points: number;
  data: Array<{
    Date: string;
    Open: number;
    High: number;
    Low: number;
    Close: number;
    Volume: number;
  }>;
  statistics: {
    mean?: number;
    std?: number;
    min?: number;
    max?: number;
    volume_avg?: number;
  };
}
```

**Example Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "period": "1mo",
  "interval": "1d",
  "data_points": 21,
  "data": [
    {
      "Date": "2024-12-01",
      "Open": 175.20,
      "High": 177.50,
      "Low": 174.80,
      "Close": 176.90,
      "Volume": 48230000
    }
  ],
  "statistics": {
    "mean": 176.45,
    "std": 2.34,
    "min": 172.10,
    "max": 181.20,
    "volume_avg": 52430000
  }
}
```

---

## 📊 VALIDATION REFERENCE

### Ticker Validation
- **Pattern:** `^[A-Z0-9\-\.]+$`
- **Length:** 1-10 characters
- **Case:** Automatically converted to uppercase
- **Examples:** `AAPL`, `BRK-B`, `BRK.B`

### Date Validation
- **Format:** `YYYY-MM-DD`
- **Examples:** `2024-01-01`, `2024-12-31`
- **Invalid:** `01/01/2024`, `2024-1-1`, `01-01-2024`

### Interval Validation
**Valid Values:**
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `1d` - 1 day (default)
- `1wk` - 1 week
- `1mo` - 1 month

### Period Validation (Market Data Only)
**Valid Values:**
- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month (default)
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year
- `2y` - 2 years
- `5y` - 5 years
- `ytd` - Year to date
- `max` - Maximum available

### Cash Validation
- **Type:** number (float)
- **Constraint:** Must be > 0
- **Default:** 10000.0

---

## 🚨 ERROR HANDLING

### HTTP Status Codes
- **200** - Success
- **201** - Created (POST presets, portfolios, watchlists)
- **204** - No Content (DELETE operations)
- **400** - Bad Request (invalid operation)
- **404** - Not Found (resource doesn't exist)
- **422** - Unprocessable Entity (validation error)
- **500** - Internal Server Error

### Validation Error Format (422)
```typescript
{
  detail: Array<{
    type: string;           // Error type (e.g., "value_error", "greater_than")
    loc: string[];          // Location of error (e.g., ["body", "ticker"])
    msg: string;            // Human-readable error message
    input: any;             // Invalid input that caused error
    ctx?: {                 // Additional context
      error?: any;
      gt?: number;          // For greater_than validation
      // ... other context
    };
  }>;
}
```

**Example Validation Error:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "ticker"],
      "msg": "Value error, Ticker must contain only alphanumeric characters, hyphens, and dots",
      "input": "INVALID@@@"
    },
    {
      "type": "greater_than",
      "loc": ["body", "cash"],
      "msg": "Input should be greater than 0",
      "input": -1000,
      "ctx": { "gt": 0.0 }
    }
  ]
}
```

---

## 💡 FRONTEND INTEGRATION TIPS

### Handling Validation
Always check for `422` status code and display validation errors to users:
```typescript
try {
  const response = await fetch('/backtest', {
    method: 'POST',
    body: JSON.stringify(request)
  });

  if (response.status === 422) {
    const errors = await response.json();
    // Display errors.detail array to user
    errors.detail.forEach(err => {
      console.log(`${err.loc.join('.')}: ${err.msg}`);
    });
  }
} catch (error) {
  // Handle network errors
}
```

### Ticker Input Normalization
Always uppercase tickers before sending:
```typescript
const normalizedTicker = ticker.toUpperCase().trim();
```

### Date Formatting
Ensure dates are in YYYY-MM-DD format:
```typescript
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};
```

### Null Handling
Some fields can be `null` (e.g., `sharpe_ratio`, `max_drawdown`). Always check:
```typescript
const sharpe = data.sharpe_ratio ?? 0;  // Use default if null
const sharpe = data.sharpe_ratio || 0;   // Use default if null/0/false
```

### Pagination
For paginated endpoints (runs, presets), use limit/offset:
```typescript
// Get next page
const nextOffset = currentOffset + limit;
const url = `/runs?limit=${limit}&offset=${nextOffset}`;
```

---

## 📝 CHANGELOG FROM v1.0

### ✅ Added
- Input validation on all request models (422 errors)
- Ticker format validation (alphanumeric, hyphens, dots only)
- Date format validation (YYYY-MM-DD)
- Cash value validation (must be > 0)
- Interval validation (predefined list)
- Period validation for market data
- Parameter range validation for optimization
- String length constraints (name, description, etc.)

### ⚠️ Changed
- CORS now restricted (was wildcard `*`)
- Tickers automatically converted to uppercase
- Environment variable support for API configuration

### 🔴 Breaking Changes
- Invalid input now returns `422` instead of `500`
- CORS restrictions may block unauthorized origins
- Ticker symbols with special characters (except `-` and `.`) rejected
- Date format must be `YYYY-MM-DD` (other formats rejected)
- Negative cash values rejected

---

**Generated:** January 2026
**API Version:** 2.0.0
**Total Endpoints:** 29
