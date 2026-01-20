# StrategyBuilder API Reference

**Version:** Latest
**Base URL:** `http://localhost:8000`
**Last Updated:** 2024-01-20

---

## Table of Contents

1. [Overview](#overview)
2. [Available Strategies](#available-strategies)
3. [Core Endpoints](#core-endpoints)
   - [Health & Info](#health--info)
   - [Strategies](#strategies)
   - [Backtesting](#backtesting)
   - [Optimization](#optimization)
   - [Market Scan](#market-scan)
   - [Market Data](#market-data)
4. [Run History](#run-history)
5. [Presets](#presets)
6. [Portfolio Management](#portfolio-management)
7. [Snapshot](#snapshot)
8. [Watchlist](#watchlist)
9. [Live Market Monitor](#live-market-monitor)
10. [Data Models](#data-models)
11. [TypeScript Interfaces](#typescript-interfaces)
12. [Common Patterns](#common-patterns)

---

## Overview

The StrategyBuilder API is a comprehensive backtesting platform for algorithmic trading strategies. It supports:

- 12+ built-in trading strategies
- Single-stock backtesting
- Strategy optimization
- Market-wide scanning (S&P 500)
- Portfolio analysis with weighted returns
- Real-time snapshots
- Run history and presets management
- Watchlist tracking

**Key Features:**
- Automatic run persistence
- Strategy parameter optimization
- Weighted portfolio analysis
- Market-wide strategy scanning
- Real-time strategy snapshots

---

## Available Strategies

| Strategy Name | Module | Key Parameters |
|---------------|--------|----------------|
| `adx_strategy` | ADX Strategy | `adx_period`, `adx_threshold` |
| `alligator_strategy` | Alligator Strategy | `jaw_period`, `teeth_period`, `lips_period` |
| `bollinger_bands_strategy` | Bollinger Bands | `period`, `devfactor` |
| `cci_atr_strategy` | CCI + ATR Strategy | `cci_period`, `atr_period` |
| `cmf_atr_macd_strategy` | CMF + ATR + MACD | `cmf_period`, `atr_period`, `macd_fast`, `macd_slow` |
| `keltner_channel_strategy` | Keltner Channel | `ema_period`, `atr_period`, `atr_multiplier` |
| `mfi_strategy` | Money Flow Index | `mfi_period`, `mfi_overbought`, `mfi_oversold` |
| `momentum_multi_strategy` | Momentum Multi | `momentum_period`, `ma_period` |
| `rsi_stochastic_strategy` | RSI + Stochastic | `rsi_period`, `rsi_oversold`, `rsi_overbought`, `stoch_period` |
| `tema_crossover_strategy` | TEMA Crossover | `tema_fast`, `tema_slow` |
| `tema_macd_strategy` | TEMA + MACD | `tema_period`, `macd_fast`, `macd_slow` |
| `williams_r_strategy` | Williams %R | `period`, `oversold`, `overbought` |

---

## Core Endpoints

### Health & Info

#### GET `/`
Root endpoint with API information.

**Response:**
```json
{
  "name": "StrategyBuilder API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "endpoints": {
    "strategies": "/strategies",
    "backtest": "/backtest",
    "optimize": "/optimize",
    "market_scan": "/market-scan",
    "portfolio": "/portfolio",
    ...
  }
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00.000Z"
}
```

---

### Strategies

#### GET `/strategies`
List all available trading strategies.

**Response:**
```json
{
  "success": true,
  "count": 12,
  "strategies": [
    {
      "module": "bollinger_bands_strategy",
      "class_name": "BollingerBandsStrategy",
      "description": "Bollinger Bands mean reversion strategy",
      "optimizable_params": [
        {
          "name": "period",
          "type": "int",
          "default": 20,
          "min": 10,
          "max": 50,
          "step": 5,
          "description": "Moving average period"
        },
        {
          "name": "devfactor",
          "type": "float",
          "default": 2.0,
          "min": 1.0,
          "max": 3.0,
          "step": 0.5,
          "description": "Standard deviation multiplier"
        }
      ]
    }
  ]
}
```

#### GET `/strategies/{strategy_name}`
Get detailed information about a specific strategy.

**Parameters:**
- `strategy_name` (path) - Strategy module name (e.g., `bollinger_bands_strategy`)

**Response:**
```json
{
  "success": true,
  "strategy": {
    "module": "bollinger_bands_strategy",
    "class_name": "BollingerBandsStrategy",
    "description": "Bollinger Bands mean reversion strategy",
    "optimizable_params": [...]
  }
}
```

**Error Responses:**
- `404` - Strategy not found

---

### Backtesting

#### POST `/backtest`
Run a backtest for a single stock with a specific strategy.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  },
  "include_chart_data": false,
  "columnar_format": true
}
```

**Request Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | string | Yes | - | Stock ticker symbol |
| `strategy` | string | Yes | - | Strategy module name |
| `start_date` | string | No | 1 year ago | Start date (YYYY-MM-DD) |
| `end_date` | string | No | Today | End date (YYYY-MM-DD) |
| `interval` | string | No | `"1d"` | Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo) |
| `cash` | float | No | `10000.0` | Starting cash |
| `parameters` | object | No | Strategy defaults | Strategy parameters |
| `include_chart_data` | boolean | No | `false` | Include OHLCV chart data in response |
| `columnar_format` | boolean | No | `true` | Return chart data in columnar format (for performance) |

**Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_value": 10000.0,
  "end_value": 12500.75,
  "pnl": 2500.75,
  "return_pct": 25.01,
  "sharpe_ratio": 1.45,
  "max_drawdown": -8.5,
  "total_trades": 24,
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "advanced_metrics": {
    "winning_trades": 16,
    "losing_trades": 8,
    "win_rate": 66.67,
    "avg_win": 250.5,
    "avg_loss": -125.25,
    "largest_win": 450.0,
    "largest_loss": -280.0,
    "profit_factor": 2.0
  },
  "chart_data": null
}
```

**Chart Data Format:**

When `include_chart_data=true` and `columnar_format=true`:
```json
{
  "chart_data": {
    "datetime": ["2024-01-01T00:00:00", "2024-01-02T00:00:00", ...],
    "open": [150.5, 151.2, ...],
    "high": [152.0, 153.5, ...],
    "low": [149.8, 150.5, ...],
    "close": [151.5, 152.8, ...],
    "volume": [1000000, 1200000, ...]
  }
}
```

When `columnar_format=false`:
```json
{
  "chart_data": [
    {
      "datetime": "2024-01-01T00:00:00",
      "open": 150.5,
      "high": 152.0,
      "low": 149.8,
      "close": 151.5,
      "volume": 1000000
    }
  ]
}
```

**Error Responses:**
- `400` - Invalid ticker, no data available, or insufficient data
- `404` - Strategy not found
- `422` - Validation error (invalid request format)
- `500` - Backtest execution failed

---

### Optimization

#### POST `/optimize`
Optimize strategy parameters across multiple combinations.

**Request Body:**
```json
{
  "ticker": "BTC-USD",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "optimization_params": {
    "period": [10, 20, 30, 40, 50],
    "devfactor": [1.5, 2.0, 2.5, 3.0]
  }
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker symbol |
| `strategy` | string | Yes | Strategy module name |
| `start_date` | string | No | Start date (YYYY-MM-DD) |
| `end_date` | string | No | End date (YYYY-MM-DD) |
| `interval` | string | No | Data interval |
| `cash` | float | No | Starting cash |
| `optimization_params` | object | Yes | Parameters to optimize (each key has array of values to test) |

**Response:**
```json
{
  "success": true,
  "ticker": "BTC-USD",
  "strategy": "bollinger_bands_strategy",
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "total_combinations": 20,
  "top_results": [
    {
      "parameters": {
        "period": 30,
        "devfactor": 2.0
      },
      "pnl": 3500.50,
      "return_pct": 35.01,
      "sharpe_ratio": 1.85,
      "start_value": 10000.0,
      "end_value": 13500.50
    },
    {
      "parameters": {
        "period": 20,
        "devfactor": 2.5
      },
      "pnl": 3200.25,
      "return_pct": 32.00,
      "sharpe_ratio": 1.72,
      "start_value": 10000.0,
      "end_value": 13200.25
    }
  ]
}
```

**Notes:**
- Results are sorted by PnL (highest first)
- Top 10 results are returned by default
- `total_combinations` = product of all parameter array lengths

**Error Responses:**
- `400` - Invalid parameters or ticker
- `404` - Strategy not found
- `500` - Optimization failed

---

### Market Scan

#### POST `/market-scan`
Run a strategy across all S&P 500 stocks (503 tickers).

**Request Body:**
```json
{
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  }
}
```

**Request Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `strategy` | string | Yes | - | Strategy module name |
| `start_date` | string | No | 1 year ago | Start date (YYYY-MM-DD) |
| `end_date` | string | No | Today | End date (YYYY-MM-DD) |
| `interval` | string | No | `"1d"` | Data interval |
| `cash` | float | No | `10000.0` | Starting cash per stock |
| `parameters` | object | No | Strategy defaults | Strategy parameters |

**Response:**
```json
{
  "success": true,
  "strategy": "bollinger_bands_strategy",
  "start_value": 5030000.0,
  "end_value": 6250000.0,
  "pnl": 1220000.0,
  "return_pct": 24.25,
  "sharpe_ratio": 1.35,
  "max_drawdown": -12.5,
  "total_trades": 8500,
  "winning_trades": 5200,
  "losing_trades": 3300,
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "stocks_scanned": 503,
  "stocks_with_trades": 485,
  "stock_results": [
    {
      "ticker": "NVDA",
      "pnl": 8500.50,
      "return_pct": 85.01,
      "total_trades": 18,
      "winning_trades": 14,
      "losing_trades": 4,
      "sharpe_ratio": 2.15,
      "max_drawdown": -8.5,
      "start_value": 10000.0,
      "end_value": 18500.50
    },
    {
      "ticker": "AAPL",
      "pnl": 4200.75,
      "return_pct": 42.01,
      "total_trades": 22,
      "winning_trades": 15,
      "losing_trades": 7,
      "sharpe_ratio": 1.65,
      "max_drawdown": -6.2,
      "start_value": 10000.0,
      "end_value": 14200.75
    }
  ],
  "macro_statistics": {
    "avg_pnl": 2425.54,
    "median_pnl": 1850.25,
    "std_pnl": 1500.75,
    "min_pnl": -3500.0,
    "max_pnl": 8500.50,
    "avg_return_pct": 24.26,
    "median_return_pct": 18.50,
    "std_return_pct": 15.01,
    "profitable_stocks": 380,
    "unprofitable_stocks": 123,
    "profitability_rate": 75.55,
    "avg_sharpe_ratio": 1.25,
    "avg_max_drawdown": -9.5,
    "total_winning_trades": 5200,
    "total_losing_trades": 3300,
    "overall_win_rate": 61.18
  }
}
```

**Response Structure:**
- **Aggregate Metrics**: Total PnL, return %, Sharpe ratio across all stocks
- **Stock Results**: Per-stock breakdown (sorted by PnL descending)
- **Macro Statistics**: Statistical analysis across the portfolio

**Notes:**
- Scans 503 S&P 500 stocks
- Results are pre-sorted by PnL (best performers first)
- Frontend can filter/sort on client side
- Takes 5-15 minutes to complete (depending on date range)

**Error Responses:**
- `404` - Strategy not found
- `400` - Invalid parameters
- `500` - Market scan failed

---

### Market Data

#### POST `/market-data`
Fetch raw market data for a ticker.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "period": "1mo",
  "interval": "1d"
}
```

**Request Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | string | Yes | - | Stock ticker symbol |
| `period` | string | No | `"1mo"` | Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, ytd, max) |
| `interval` | string | No | `"1d"` | Data interval |

**Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "period": "1mo",
  "interval": "1d",
  "data_points": 21,
  "data": [
    {
      "Date": "2024-01-01T00:00:00",
      "Open": 150.5,
      "High": 152.0,
      "Low": 149.8,
      "Close": 151.5,
      "Volume": 1000000
    }
  ],
  "statistics": {
    "mean": 151.25,
    "std": 2.5,
    "min": 148.0,
    "max": 155.0,
    "volume_avg": 1200000
  }
}
```

**Error Responses:**
- `404` - No data found for ticker
- `500` - Failed to fetch market data

---

## Run History

Run history automatically saves every backtest execution for later reference and replay.

#### GET `/runs`
List saved backtest runs with filtering and pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ticker` | string | None | Filter by ticker symbol |
| `strategy` | string | None | Filter by strategy name |
| `limit` | int | 100 | Max results (1-1000) |
| `offset` | int | 0 | Pagination offset |

**Example Request:**
```
GET /runs?ticker=AAPL&strategy=bollinger_bands_strategy&limit=50&offset=0
```

**Response:**
```json
{
  "success": true,
  "total_count": 250,
  "count": 50,
  "limit": 50,
  "offset": 0,
  "runs": [
    {
      "id": 142,
      "ticker": "AAPL",
      "strategy": "bollinger_bands_strategy",
      "interval": "1d",
      "pnl": 2500.75,
      "return_pct": 25.01,
      "created_at": "2024-01-20T10:30:00"
    }
  ]
}
```

#### GET `/runs/{run_id}`
Get detailed information about a specific run.

**Parameters:**
- `run_id` (path) - Run ID

**Response:**
```json
{
  "id": 142,
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
  "pnl": 2500.75,
  "return_pct": 25.01,
  "sharpe_ratio": 1.45,
  "max_drawdown": -8.5,
  "total_trades": 24,
  "winning_trades": 16,
  "losing_trades": 8,
  "created_at": "2024-01-20T10:30:00"
}
```

**Error Responses:**
- `404` - Run not found

#### POST `/runs/{run_id}/replay`
Replay a saved run with optional parameter overrides.

**Parameters:**
- `run_id` (path) - Run ID to replay

**Request Body (all fields optional):**
```json
{
  "start_date": "2024-06-01",
  "end_date": "2024-12-31",
  "interval": "1h",
  "cash": 20000.0,
  "parameters": {
    "period": 30,
    "devfactor": 2.5
  }
}
```

**Response:**
Same as `/backtest` endpoint response.

**Notes:**
- Any field can be overridden from the original run
- Original ticker and strategy are preserved
- New run is saved as a separate entry

**Error Responses:**
- `404` - Run not found
- `400` - Invalid override parameters
- `500` - Replay failed

---

## Presets

Presets are saved strategy configurations (parameters only, no ticker/interval).

### Key Concept Change
**IMPORTANT**: Presets now store **only strategy name and parameters**, NOT ticker or interval. This makes them reusable across different tickers, portfolios, and market scans.

#### POST `/presets`
Create a new preset.

**Request Body:**
```json
{
  "name": "Aggressive RSI Strategy",
  "strategy": "rsi_stochastic_strategy",
  "parameters": {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "stoch_period": 14
  },
  "notes": "Aggressive mean reversion strategy for volatile markets"
}
```

**Request Fields:**
| Field | Type | Required | Max Length | Description |
|-------|------|----------|------------|-------------|
| `name` | string | Yes | 200 | Preset name |
| `strategy` | string | Yes | - | Strategy module name |
| `parameters` | object | Yes | - | Strategy parameters |
| `notes` | string | No | 1000 | Optional notes |

**Response:**
```json
{
  "id": 5,
  "name": "Aggressive RSI Strategy",
  "strategy": "rsi_stochastic_strategy",
  "parameters": {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "stoch_period": 14
  },
  "notes": "Aggressive mean reversion strategy for volatile markets",
  "created_at": "2024-01-20T10:30:00"
}
```

**Error Responses:**
- `404` - Strategy not found
- `409` - Preset with same name and strategy already exists
- `422` - Validation error

#### GET `/presets`
List all presets with filtering and pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy` | string | None | Filter by strategy name |
| `limit` | int | 100 | Max results (1-1000) |
| `offset` | int | 0 | Pagination offset |

**Example Request:**
```
GET /presets?strategy=bollinger_bands_strategy&limit=50
```

**Response:**
```json
{
  "success": true,
  "total_count": 15,
  "count": 15,
  "limit": 50,
  "offset": 0,
  "presets": [
    {
      "id": 1,
      "name": "Conservative Bollinger",
      "strategy": "bollinger_bands_strategy",
      "parameters": {
        "period": 30,
        "devfactor": 2.5
      },
      "notes": null,
      "created_at": "2024-01-15T08:00:00"
    }
  ]
}
```

#### GET `/presets/{preset_id}`
Get a specific preset by ID.

**Parameters:**
- `preset_id` (path) - Preset ID

**Response:**
```json
{
  "id": 1,
  "name": "Conservative Bollinger",
  "strategy": "bollinger_bands_strategy",
  "parameters": {
    "period": 30,
    "devfactor": 2.5
  },
  "notes": null,
  "created_at": "2024-01-15T08:00:00"
}
```

**Error Responses:**
- `404` - Preset not found

#### DELETE `/presets/{preset_id}`
Delete a preset.

**Parameters:**
- `preset_id` (path) - Preset ID

**Response:**
```json
{
  "success": true,
  "message": "Preset 1 deleted successfully"
}
```

**Error Responses:**
- `404` - Preset not found

#### POST `/presets/{preset_id}/backtest`
Run a backtest using a preset's strategy configuration.

**Parameters:**
- `preset_id` (path) - Preset ID

**Query Parameters (ALL REQUIRED):**
| Parameter | Type | Required | Example | Description |
|-----------|------|----------|---------|-------------|
| `ticker` | string | **Yes** | `"AAPL"` | Stock ticker symbol |
| `interval` | string | **Yes** | `"1d"` | Data interval |
| `start_date` | string | No | `"2024-01-01"` | Start date |
| `end_date` | string | No | `"2024-12-31"` | End date |
| `cash` | float | No | `10000.0` | Starting cash |

**Example Request:**
```
POST /presets/5/backtest?ticker=AAPL&interval=1d&start_date=2024-01-01&end_date=2024-12-31&cash=10000
```

**Response:**
Same as `/backtest` endpoint response.

**Notes:**
- Ticker and interval are now **required query parameters** (not stored in preset)
- Preset provides strategy name and parameters
- This allows reusing the same strategy config across different tickers

**Error Responses:**
- `404` - Preset not found
- `400` - Invalid parameters or strategy not found
- `422` - Missing required query parameters
- `500` - Backtest failed

---

## Portfolio Management

Portfolio management allows tracking multiple positions and running weighted strategy analysis across the entire portfolio.

### Key Concepts
- **Position Size**: Automatically calculated as `quantity × entry_price`
- **Weighted Analysis**: Returns are weighted by position size (larger positions have more impact)
- **Persistent Storage**: All positions are saved in SQLite database

#### POST `/portfolio`
Add a new position to the portfolio.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "quantity": 100.0,
  "entry_price": 150.50,
  "entry_date": "2024-01-15",
  "notes": "Initial position"
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker (max 10 chars) |
| `quantity` | float | Yes | Number of shares (> 0) |
| `entry_price` | float | Yes | Entry price per share (> 0) |
| `entry_date` | string | Yes | Entry date (YYYY-MM-DD) |
| `notes` | string | No | Optional notes (max 500 chars) |

**Response:**
```json
{
  "id": 1,
  "ticker": "AAPL",
  "quantity": 100.0,
  "entry_price": 150.50,
  "entry_date": "2024-01-15",
  "position_size": 15050.0,
  "notes": "Initial position",
  "created_at": "2024-01-20T10:30:00",
  "updated_at": "2024-01-20T10:30:00"
}
```

**Notes:**
- `position_size` is automatically calculated as `quantity × entry_price`
- Ticker is automatically uppercased

#### GET `/portfolio`
Get all portfolio positions with summary.

**Response:**
```json
{
  "total_positions": 5,
  "total_portfolio_value": 75250.50,
  "positions": [
    {
      "id": 1,
      "ticker": "AAPL",
      "quantity": 100.0,
      "entry_price": 150.50,
      "entry_date": "2024-01-15",
      "position_size": 15050.0,
      "notes": "Initial position",
      "created_at": "2024-01-20T10:30:00",
      "updated_at": "2024-01-20T10:30:00"
    },
    {
      "id": 2,
      "ticker": "MSFT",
      "quantity": 50.0,
      "entry_price": 380.25,
      "entry_date": "2024-01-18",
      "position_size": 19012.50,
      "notes": null,
      "created_at": "2024-01-20T11:00:00",
      "updated_at": "2024-01-20T11:00:00"
    }
  ]
}
```

#### GET `/portfolio/{position_id}`
Get a specific position by ID.

**Parameters:**
- `position_id` (path) - Position ID

**Response:**
```json
{
  "id": 1,
  "ticker": "AAPL",
  "quantity": 100.0,
  "entry_price": 150.50,
  "entry_date": "2024-01-15",
  "position_size": 15050.0,
  "notes": "Initial position",
  "created_at": "2024-01-20T10:30:00",
  "updated_at": "2024-01-20T10:30:00"
}
```

**Error Responses:**
- `404` - Position not found

#### PUT `/portfolio/{position_id}`
Update an existing position.

**Parameters:**
- `position_id` (path) - Position ID

**Request Body (all fields optional):**
```json
{
  "ticker": "AAPL",
  "quantity": 150.0,
  "entry_price": 148.25,
  "entry_date": "2024-01-16",
  "notes": "Updated position"
}
```

**Response:**
```json
{
  "id": 1,
  "ticker": "AAPL",
  "quantity": 150.0,
  "entry_price": 148.25,
  "entry_date": "2024-01-16",
  "position_size": 22237.50,
  "notes": "Updated position",
  "created_at": "2024-01-20T10:30:00",
  "updated_at": "2024-01-20T15:45:00"
}
```

**Notes:**
- `position_size` is automatically recalculated if `quantity` or `entry_price` changes
- At least one field must be provided

**Error Responses:**
- `404` - Position not found
- `400` - No fields to update

#### DELETE `/portfolio/{position_id}`
Delete a position from the portfolio.

**Parameters:**
- `position_id` (path) - Position ID

**Response:**
```json
{
  "success": true,
  "message": "Position 1 deleted successfully"
}
```

**Error Responses:**
- `404` - Position not found

#### POST `/portfolio/analyze`
Run strategy analysis across entire portfolio with weighted returns.

**Request Body:**
```json
{
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  }
}
```

**Request Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `strategy` | string | Yes | - | Strategy module name |
| `start_date` | string | No | 1 year ago | Start date (YYYY-MM-DD) |
| `end_date` | string | No | Today | End date (YYYY-MM-DD) |
| `interval` | string | No | `"1d"` | Data interval |
| `parameters` | object | No | Strategy defaults | Strategy parameters |

**Response:**
```json
{
  "success": true,
  "strategy": "bollinger_bands_strategy",
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "total_portfolio_value": 75250.50,
  "weighted_pnl": 18500.75,
  "weighted_return_pct": 24.58,
  "weighted_sharpe_ratio": 1.65,
  "weighted_max_drawdown": -7.8,
  "total_trades": 95,
  "winning_trades": 62,
  "losing_trades": 33,
  "positions_analyzed": 5,
  "position_results": [
    {
      "position_id": 1,
      "ticker": "AAPL",
      "position_size": 15050.0,
      "weight": 20.0,
      "pnl": 3500.50,
      "return_pct": 23.26,
      "total_trades": 24,
      "winning_trades": 16,
      "losing_trades": 8,
      "sharpe_ratio": 1.45,
      "max_drawdown": -6.5,
      "start_value": 15050.0,
      "end_value": 18550.50
    },
    {
      "position_id": 2,
      "ticker": "MSFT",
      "position_size": 19012.50,
      "weight": 25.27,
      "pnl": 5200.25,
      "return_pct": 27.35,
      "total_trades": 18,
      "winning_trades": 13,
      "losing_trades": 5,
      "sharpe_ratio": 1.82,
      "max_drawdown": -5.2,
      "start_value": 19012.50,
      "end_value": 24212.75
    }
  ],
  "portfolio_statistics": {
    "best_position": {
      "ticker": "MSFT",
      "pnl": 5200.25,
      "return_pct": 27.35
    },
    "worst_position": {
      "ticker": "IBM",
      "pnl": -850.50,
      "return_pct": -8.5
    },
    "avg_return_pct": 18.75,
    "std_return_pct": 12.5,
    "positions_profitable": 4,
    "positions_unprofitable": 1
  }
}
```

**Response Structure:**
- **Weighted Metrics**: Portfolio-level returns weighted by position size
- **Position Results**: Per-position breakdown with individual metrics
- **Portfolio Statistics**: Aggregate statistics and best/worst performers

**Weighting Formula:**
```
Weight = position_size / total_portfolio_value
Weighted Return = Σ(weight_i × return_pct_i)
Weighted PnL = Σ(pnl_i)  (simple sum, not weighted)
```

**Notes:**
- Each position is backtested independently
- Position size determines capital allocated per backtest
- Weighted metrics reflect realistic portfolio-level performance
- Requires at least one position in portfolio

**Error Responses:**
- `404` - Strategy not found
- `400` - Portfolio is empty or invalid parameters
- `500` - Analysis failed

---

## Snapshot

Get real-time strategy state for a ticker (current indicators, position, recent trades).

#### POST `/snapshot`
Get current strategy snapshot.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  },
  "interval": "1d",
  "lookback_bars": 200,
  "cash": 10000.0
}
```

**Request Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | string | Yes | - | Stock ticker symbol |
| `strategy` | string | Yes | - | Strategy module name |
| `parameters` | object | No | Strategy defaults | Strategy parameters |
| `interval` | string | No | `"1d"` | Data interval |
| `lookback_bars` | int | No | `200` | Number of historical bars (50-1000) |
| `cash` | float | No | `10000.0` | Starting cash |

**Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "interval": "1d",
  "lookback_bars": 200,
  "last_bar": {
    "datetime": "2024-01-19T16:00:00",
    "open": 185.5,
    "high": 187.2,
    "low": 184.8,
    "close": 186.5,
    "volume": 45000000
  },
  "indicators": {
    "middle_band": 185.0,
    "upper_band": 190.0,
    "lower_band": 180.0,
    "bb_width": 10.0
  },
  "position_state": {
    "in_position": true,
    "position_type": "long",
    "entry_price": 181.5,
    "current_price": 186.5,
    "size": 55.0,
    "unrealized_pnl": 275.0
  },
  "recent_trades": [
    {
      "datetime": "2024-01-15T16:00:00",
      "type": "buy",
      "price": 181.5,
      "size": 55.0,
      "pnl": 0.0
    }
  ],
  "portfolio_value": 10275.0,
  "cash": 25.0,
  "timestamp": "2024-01-20T10:30:00"
}
```

**Notes:**
- Shows current strategy state based on latest market data
- Indicators are strategy-specific (each strategy returns different indicators)
- Position state shows if strategy is currently in a position
- Recent trades show last 5 trades

**Error Responses:**
- `404` - Strategy not found
- `400` - Invalid ticker, no data available, or invalid parameters
- `500` - Snapshot failed

---

## Watchlist

Watchlist allows tracking specific preset or run configurations for scheduled monitoring.

#### POST `/watchlist`
Create a new watchlist entry.

**Request Body:**
```json
{
  "name": "AAPL RSI Daily Check",
  "preset_id": 5,
  "run_id": null,
  "frequency": "daily",
  "enabled": true
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Watchlist entry name (max 200 chars) |
| `preset_id` | int | Conditional | Preset ID (required if no run_id) |
| `run_id` | int | Conditional | Run ID (required if no preset_id) |
| `frequency` | string | Yes | Frequency (daily, weekly, hourly, etc.) |
| `enabled` | bool | No | Whether entry is enabled (default: true) |

**Response:**
```json
{
  "id": 10,
  "name": "AAPL RSI Daily Check",
  "preset_id": 5,
  "run_id": null,
  "frequency": "daily",
  "enabled": true,
  "created_at": "2024-01-20T10:30:00",
  "last_run_at": null
}
```

**Notes:**
- Either `preset_id` OR `run_id` must be provided (not both)
- Preset/Run must exist or 404 error is returned

**Error Responses:**
- `400` - Neither preset_id nor run_id provided
- `404` - Preset or Run not found

#### GET `/watchlist`
List all watchlist entries.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled_only` | bool | false | Only return enabled entries |

**Example Request:**
```
GET /watchlist?enabled_only=true
```

**Response:**
```json
[
  {
    "id": 10,
    "name": "AAPL RSI Daily Check",
    "preset_id": 5,
    "run_id": null,
    "frequency": "daily",
    "enabled": true,
    "created_at": "2024-01-20T10:30:00",
    "last_run_at": null
  }
]
```

#### GET `/watchlist/{entry_id}`
Get a specific watchlist entry.

**Parameters:**
- `entry_id` (path) - Watchlist entry ID

**Response:**
```json
{
  "id": 10,
  "name": "AAPL RSI Daily Check",
  "preset_id": 5,
  "run_id": null,
  "frequency": "daily",
  "enabled": true,
  "created_at": "2024-01-20T10:30:00",
  "last_run_at": "2024-01-21T08:00:00"
}
```

**Error Responses:**
- `404` - Watchlist entry not found

#### PATCH `/watchlist/{entry_id}`
Update watchlist entry (enable/disable).

**Parameters:**
- `entry_id` (path) - Watchlist entry ID

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `enabled` | bool | Yes | New enabled status |

**Example Request:**
```
PATCH /watchlist/10?enabled=false
```

**Response:**
```json
{
  "success": true,
  "message": "Watchlist entry 10 updated successfully"
}
```

**Error Responses:**
- `404` - Watchlist entry not found
- `400` - No enabled parameter provided

#### DELETE `/watchlist/{entry_id}`
Delete a watchlist entry.

**Parameters:**
- `entry_id` (path) - Watchlist entry ID

**Response:**
```json
{
  "success": true,
  "message": "Watchlist entry 10 deleted successfully"
}
```

**Error Responses:**
- `404` - Watchlist entry not found

---

## Live Market Monitor

The live market monitor displays real-time data for a configured list of tickers. This section manages which tickers appear in the monitor.

### Key Concepts
- **Simple ticker list** - No complex configuration, just ticker symbols
- **Display order** - Tickers are shown in specified order
- **Persistent** - Saved in database across sessions
- **Initialized with defaults** - AAPL, MSFT, GOOGL on first run

#### GET `/monitor/tickers`
Get list of tickers for live market monitor (for initialization).

**Response:**
```json
{
  "success": true,
  "count": 3,
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

**Notes:**
- Returns simple array of ticker symbols
- Ordered by `display_order` field
- Frontend should call this on initialization
- Defaults to ["AAPL", "MSFT", "GOOGL"] on first run

**Use Case:**
```typescript
// Frontend on mount
useEffect(() => {
  const loadMonitorTickers = async () => {
    const response = await fetch('/monitor/tickers');
    const data = await response.json();
    setMonitorTickers(data.tickers); // ["AAPL", "MSFT", "GOOGL"]
  };
  loadMonitorTickers();
}, []);
```

#### GET `/monitor/tickers/detailed`
Get detailed list of monitor tickers with metadata.

**Response:**
```json
{
  "success": true,
  "count": 3,
  "tickers": [
    {
      "id": 1,
      "ticker": "AAPL",
      "display_order": 0,
      "created_at": "2024-01-20T10:00:00"
    },
    {
      "id": 2,
      "ticker": "MSFT",
      "display_order": 1,
      "created_at": "2024-01-20T10:00:00"
    },
    {
      "id": 3,
      "ticker": "GOOGL",
      "display_order": 2,
      "created_at": "2024-01-20T10:00:00"
    }
  ]
}
```

**Notes:**
- Returns full ticker objects with IDs and order
- Useful for admin UI showing ticker management

#### POST `/monitor/tickers`
Add a ticker to the live market monitor.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | Yes | Ticker symbol to add (1-10 chars) |

**Example Request:**
```
POST /monitor/tickers?ticker=NVDA
```

**Response:**
```json
{
  "success": true,
  "message": "Ticker NVDA added to monitor",
  "id": 4,
  "ticker": "NVDA"
}
```

**Notes:**
- Ticker is automatically uppercased
- Added to end of display order
- Duplicate tickers are rejected

**Error Responses:**
- `400` - Ticker already exists or invalid format
- `500` - Database error

#### DELETE `/monitor/tickers/{ticker}`
Remove a ticker from the live market monitor.

**Parameters:**
- `ticker` (path) - Ticker symbol to remove

**Example Request:**
```
DELETE /monitor/tickers/NVDA
```

**Response:**
```json
{
  "success": true,
  "message": "Ticker NVDA removed from monitor"
}
```

**Error Responses:**
- `404` - Ticker not found in monitor list
- `500` - Database error

#### PUT `/monitor/tickers/reorder`
Update the display order of monitor tickers.

**Request Body:**
```json
["MSFT", "AAPL", "GOOGL", "NVDA"]
```

**Response:**
```json
{
  "success": true,
  "message": "Updated display order for 4 tickers"
}
```

**Notes:**
- Pass array of tickers in desired display order
- All tickers must exist in monitor list
- Frontend can implement drag-and-drop reordering

**Error Responses:**
- `400` - Empty ticker list
- `500` - Database error

#### DELETE `/monitor/tickers`
Remove all tickers from the live market monitor.

**Response:**
```json
{
  "success": true,
  "message": "Removed 3 tickers from monitor",
  "count": 3
}
```

**Notes:**
- Clears entire monitor list
- Useful for "reset to defaults" functionality

### Frontend Integration Example

```typescript
// Initialize monitor on app load
const MonitorPage: React.FC = () => {
  const [tickers, setTickers] = useState<string[]>([]);

  useEffect(() => {
    loadTickers();
  }, []);

  const loadTickers = async () => {
    const res = await fetch('http://localhost:8000/monitor/tickers');
    const data = await res.json();
    setTickers(data.tickers);
  };

  const addTicker = async (ticker: string) => {
    await fetch(`http://localhost:8000/monitor/tickers?ticker=${ticker}`, {
      method: 'POST'
    });
    loadTickers(); // Refresh
  };

  const removeTicker = async (ticker: string) => {
    await fetch(`http://localhost:8000/monitor/tickers/${ticker}`, {
      method: 'DELETE'
    });
    loadTickers(); // Refresh
  };

  return (
    <div>
      <h2>Live Market Monitor</h2>
      {tickers.map(ticker => (
        <TickerCard
          key={ticker}
          ticker={ticker}
          onRemove={() => removeTicker(ticker)}
        />
      ))}
      <AddTickerButton onAdd={addTicker} />
    </div>
  );
};
```

---

## Data Models

### Request Models

#### BacktestRequest
```typescript
{
  ticker: string;                    // Required
  strategy: string;                  // Required
  start_date?: string;               // Optional, YYYY-MM-DD
  end_date?: string;                 // Optional, YYYY-MM-DD
  interval?: string;                 // Default: "1d"
  cash?: number;                     // Default: 10000.0
  parameters?: Record<string, number>;  // Strategy params
  include_chart_data?: boolean;      // Default: false
  columnar_format?: boolean;         // Default: true
}
```

#### OptimizationRequest
```typescript
{
  ticker: string;                    // Required
  strategy: string;                  // Required
  start_date?: string;               // Optional
  end_date?: string;                 // Optional
  interval?: string;                 // Default: "1d"
  cash?: number;                     // Default: 10000.0
  optimization_params: Record<string, number[]>;  // Required
}
```

#### MarketScanRequest
```typescript
{
  strategy: string;                  // Required
  start_date?: string;               // Optional
  end_date?: string;                 // Optional
  interval?: string;                 // Default: "1d"
  cash?: number;                     // Default: 10000.0
  parameters?: Record<string, number>;  // Strategy params
}
```

#### CreatePresetRequest
```typescript
{
  name: string;                      // Required, max 200 chars
  strategy: string;                  // Required
  parameters: Record<string, number>;  // Required
  notes?: string;                    // Optional, max 1000 chars
}
```

#### AddPortfolioPositionRequest
```typescript
{
  ticker: string;                    // Required, max 10 chars
  quantity: number;                  // Required, > 0
  entry_price: number;               // Required, > 0
  entry_date: string;                // Required, YYYY-MM-DD
  notes?: string;                    // Optional, max 500 chars
}
```

#### PortfolioAnalysisRequest
```typescript
{
  strategy: string;                  // Required
  start_date?: string;               // Optional
  end_date?: string;                 // Optional
  interval?: string;                 // Default: "1d"
  parameters?: Record<string, number>;  // Strategy params
}
```

### Response Models

#### BacktestResponse
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
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    avg_win: number;
    avg_loss: number;
    largest_win: number;
    largest_loss: number;
    profit_factor: number;
  };
  chart_data?: any;  // Columnar or array format
}
```

#### MarketScanResponse
```typescript
{
  success: boolean;
  strategy: string;
  start_value: number;
  end_value: number;
  pnl: number;
  return_pct: number;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  interval: string;
  start_date: string;
  end_date: string;
  stocks_scanned: number;
  stocks_with_trades: number;
  stock_results: Array<{
    ticker: string;
    pnl: number;
    return_pct: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    sharpe_ratio: number | null;
    max_drawdown: number | null;
    start_value: number;
    end_value: number;
  }>;
  macro_statistics: {
    avg_pnl: number;
    median_pnl: number;
    std_pnl: number;
    min_pnl: number;
    max_pnl: number;
    avg_return_pct: number;
    median_return_pct: number;
    std_return_pct: number;
    profitable_stocks: number;
    unprofitable_stocks: number;
    profitability_rate: number;
    avg_sharpe_ratio: number;
    avg_max_drawdown: number;
    total_winning_trades: number;
    total_losing_trades: number;
    overall_win_rate: number;
  };
}
```

#### PortfolioAnalysisResponse
```typescript
{
  success: boolean;
  strategy: string;
  interval: string;
  start_date: string;
  end_date: string;
  total_portfolio_value: number;
  weighted_pnl: number;
  weighted_return_pct: number;
  weighted_sharpe_ratio: number | null;
  weighted_max_drawdown: number | null;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  positions_analyzed: number;
  position_results: Array<{
    position_id: number;
    ticker: string;
    position_size: number;
    weight: number;
    pnl: number;
    return_pct: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    sharpe_ratio: number | null;
    max_drawdown: number | null;
    start_value: number;
    end_value: number;
  }>;
  portfolio_statistics: {
    best_position: {
      ticker: string;
      pnl: number;
      return_pct: number;
    };
    worst_position: {
      ticker: string;
      pnl: number;
      return_pct: number;
    };
    avg_return_pct: number;
    std_return_pct: number;
    positions_profitable: number;
    positions_unprofitable: number;
  };
}
```

---

## TypeScript Interfaces

Complete TypeScript definitions for frontend integration:

```typescript
// ============================================================================
// REQUEST INTERFACES
// ============================================================================

interface BacktestRequest {
  ticker: string;
  strategy: string;
  start_date?: string;
  end_date?: string;
  interval?: string;
  cash?: number;
  parameters?: Record<string, number>;
  include_chart_data?: boolean;
  columnar_format?: boolean;
}

interface OptimizationRequest {
  ticker: string;
  strategy: string;
  start_date?: string;
  end_date?: string;
  interval?: string;
  cash?: number;
  optimization_params: Record<string, number[]>;
}

interface MarketScanRequest {
  strategy: string;
  start_date?: string;
  end_date?: string;
  interval?: string;
  cash?: number;
  parameters?: Record<string, number>;
}

interface CreatePresetRequest {
  name: string;
  strategy: string;
  parameters: Record<string, number>;
  notes?: string;
}

interface AddPortfolioPositionRequest {
  ticker: string;
  quantity: number;
  entry_price: number;
  entry_date: string;
  notes?: string;
}

interface UpdatePortfolioPositionRequest {
  ticker?: string;
  quantity?: number;
  entry_price?: number;
  entry_date?: string;
  notes?: string;
}

interface PortfolioAnalysisRequest {
  strategy: string;
  start_date?: string;
  end_date?: string;
  interval?: string;
  parameters?: Record<string, number>;
}

interface SnapshotRequest {
  ticker: string;
  strategy: string;
  parameters?: Record<string, number>;
  interval?: string;
  lookback_bars?: number;
  cash?: number;
}

interface CreateWatchlistRequest {
  name: string;
  preset_id?: number;
  run_id?: number;
  frequency: string;
  enabled?: boolean;
}

// ============================================================================
// RESPONSE INTERFACES
// ============================================================================

interface BacktestResponse {
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
  advanced_metrics?: AdvancedMetrics;
  chart_data?: ChartData | ColumnarChartData;
}

interface AdvancedMetrics {
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  largest_win: number;
  largest_loss: number;
  profit_factor: number;
}

interface ChartData {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface ColumnarChartData {
  datetime: string[];
  open: number[];
  high: number[];
  low: number[];
  close: number[];
  volume: number[];
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

interface OptimizationResult {
  parameters: Record<string, number>;
  pnl: number;
  return_pct: number;
  sharpe_ratio: number | null;
  start_value: number;
  end_value: number;
}

interface MarketScanResponse {
  success: boolean;
  strategy: string;
  start_value: number;
  end_value: number;
  pnl: number;
  return_pct: number;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  interval: string;
  start_date: string;
  end_date: string;
  stocks_scanned: number;
  stocks_with_trades: number;
  stock_results: StockScanResult[];
  macro_statistics: MacroStatistics;
}

interface StockScanResult {
  ticker: string;
  pnl: number;
  return_pct: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  start_value: number;
  end_value: number;
}

interface MacroStatistics {
  avg_pnl: number;
  median_pnl: number;
  std_pnl: number;
  min_pnl: number;
  max_pnl: number;
  avg_return_pct: number;
  median_return_pct: number;
  std_return_pct: number;
  profitable_stocks: number;
  unprofitable_stocks: number;
  profitability_rate: number;
  avg_sharpe_ratio: number;
  avg_max_drawdown: number;
  total_winning_trades: number;
  total_losing_trades: number;
  overall_win_rate: number;
}

interface PresetResponse {
  id: number;
  name: string;
  strategy: string;
  parameters: Record<string, number>;
  notes: string | null;
  created_at: string;
}

interface PortfolioPositionResponse {
  id: number;
  ticker: string;
  quantity: number;
  entry_price: number;
  entry_date: string;
  position_size: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

interface PortfolioSummaryResponse {
  total_positions: number;
  total_portfolio_value: number;
  positions: PortfolioPositionResponse[];
}

interface PortfolioAnalysisResponse {
  success: boolean;
  strategy: string;
  interval: string;
  start_date: string;
  end_date: string;
  total_portfolio_value: number;
  weighted_pnl: number;
  weighted_return_pct: number;
  weighted_sharpe_ratio: number | null;
  weighted_max_drawdown: number | null;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  positions_analyzed: number;
  position_results: PositionAnalysisResult[];
  portfolio_statistics: PortfolioStatistics;
}

interface PositionAnalysisResult {
  position_id: number;
  ticker: string;
  position_size: number;
  weight: number;
  pnl: number;
  return_pct: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  start_value: number;
  end_value: number;
}

interface PortfolioStatistics {
  best_position: {
    ticker: string;
    pnl: number;
    return_pct: number;
  };
  worst_position: {
    ticker: string;
    pnl: number;
    return_pct: number;
  };
  avg_return_pct: number;
  std_return_pct: number;
  positions_profitable: number;
  positions_unprofitable: number;
}

interface SnapshotResponse {
  success: boolean;
  ticker: string;
  strategy: string;
  interval: string;
  lookback_bars: number;
  last_bar: OHLCV;
  indicators: Record<string, any>;
  position_state: PositionState;
  recent_trades: Trade[];
  portfolio_value: number;
  cash: number;
  timestamp: string;
}

interface OHLCV {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface PositionState {
  in_position: boolean;
  position_type: string | null;
  entry_price: number | null;
  current_price: number | null;
  size: number | null;
  unrealized_pnl: number | null;
}

interface Trade {
  datetime: string;
  type: string;
  price: number;
  size: number;
  pnl: number;
}

interface SavedRunSummaryResponse {
  id: number;
  ticker: string;
  strategy: string;
  interval: string;
  pnl: number | null;
  return_pct: number | null;
  created_at: string;
}

interface SavedRunDetailResponse {
  id: number;
  ticker: string;
  strategy: string;
  parameters: Record<string, number>;
  start_date: string;
  end_date: string;
  interval: string;
  cash: number;
  pnl: number | null;
  return_pct: number | null;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  total_trades: number | null;
  winning_trades: number | null;
  losing_trades: number | null;
  created_at: string;
}

interface WatchlistEntryResponse {
  id: number;
  name: string;
  preset_id: number | null;
  run_id: number | null;
  frequency: string;
  enabled: boolean;
  created_at: string;
  last_run_at: string | null;
}

interface StrategyInfo {
  module: string;
  class_name: string;
  description: string;
  optimizable_params?: ParameterInfo[];
}

interface ParameterInfo {
  name: string;
  type: string;
  default: number;
  min: number;
  max: number;
  step: number;
  description: string;
}
```

---

## Common Patterns

### 1. Running a Simple Backtest

```typescript
const runBacktest = async () => {
  const response = await fetch('http://localhost:8000/backtest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: 'AAPL',
      strategy: 'bollinger_bands_strategy',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      interval: '1d',
      cash: 10000,
      parameters: {
        period: 20,
        devfactor: 2.0
      }
    })
  });

  const result: BacktestResponse = await response.json();
  console.log(`PnL: $${result.pnl}, Return: ${result.return_pct}%`);
};
```

### 2. Optimizing Strategy Parameters

```typescript
const optimizeStrategy = async () => {
  const response = await fetch('http://localhost:8000/optimize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: 'AAPL',
      strategy: 'bollinger_bands_strategy',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      optimization_params: {
        period: [10, 20, 30, 40, 50],
        devfactor: [1.5, 2.0, 2.5, 3.0]
      }
    })
  });

  const result: OptimizationResponse = await response.json();
  console.log('Best parameters:', result.top_results[0].parameters);
};
```

### 3. Market-Wide Scan

```typescript
const runMarketScan = async () => {
  const response = await fetch('http://localhost:8000/market-scan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      strategy: 'rsi_stochastic_strategy',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      parameters: {
        rsi_period: 14,
        rsi_oversold: 30
      }
    })
  });

  const result: MarketScanResponse = await response.json();

  // Filter profitable stocks
  const profitable = result.stock_results.filter(s => s.pnl > 0);
  console.log(`Profitable stocks: ${profitable.length}/${result.stocks_scanned}`);

  // Sort by return %
  const sorted = [...result.stock_results].sort((a, b) => b.return_pct - a.return_pct);
  console.log('Top performer:', sorted[0].ticker, sorted[0].return_pct + '%');
};
```

### 4. Managing Portfolio

```typescript
// Add positions
const addPosition = async () => {
  const response = await fetch('http://localhost:8000/portfolio', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: 'AAPL',
      quantity: 100,
      entry_price: 150.50,
      entry_date: '2024-01-15',
      notes: 'Initial position'
    })
  });

  const position: PortfolioPositionResponse = await response.json();
  console.log('Position size:', position.position_size);
};

// Analyze portfolio
const analyzePortfolio = async () => {
  const response = await fetch('http://localhost:8000/portfolio/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      strategy: 'bollinger_bands_strategy',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      parameters: {
        period: 20,
        devfactor: 2.0
      }
    })
  });

  const result: PortfolioAnalysisResponse = await response.json();
  console.log('Weighted return:', result.weighted_return_pct + '%');
  console.log('Best position:', result.portfolio_statistics.best_position.ticker);
};
```

### 5. Using Presets

```typescript
// Create preset
const createPreset = async () => {
  const response = await fetch('http://localhost:8000/presets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'Aggressive RSI',
      strategy: 'rsi_stochastic_strategy',
      parameters: {
        rsi_period: 14,
        rsi_oversold: 30,
        rsi_overbought: 70
      },
      notes: 'Aggressive mean reversion'
    })
  });

  const preset: PresetResponse = await response.json();
  return preset.id;
};

// Backtest with preset
const backtestFromPreset = async (presetId: number) => {
  const params = new URLSearchParams({
    ticker: 'AAPL',
    interval: '1d',
    start_date: '2024-01-01',
    end_date: '2024-12-31'
  });

  const response = await fetch(
    `http://localhost:8000/presets/${presetId}/backtest?${params}`,
    { method: 'POST' }
  );

  const result: BacktestResponse = await response.json();
  console.log('PnL:', result.pnl);
};
```

### 6. Real-Time Snapshot

```typescript
const getSnapshot = async () => {
  const response = await fetch('http://localhost:8000/snapshot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: 'AAPL',
      strategy: 'bollinger_bands_strategy',
      parameters: {
        period: 20,
        devfactor: 2.0
      },
      interval: '1d',
      lookback_bars: 200
    })
  });

  const snapshot: SnapshotResponse = await response.json();
  console.log('Current price:', snapshot.last_bar.close);
  console.log('In position:', snapshot.position_state.in_position);
  console.log('Unrealized PnL:', snapshot.position_state.unrealized_pnl);
};
```

### 7. Error Handling

```typescript
const backtestWithErrorHandling = async () => {
  try {
    const response = await fetch('http://localhost:8000/backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticker: 'INVALID',
        strategy: 'bollinger_bands_strategy'
      })
    });

    if (!response.ok) {
      const error = await response.json();
      if (response.status === 404) {
        console.error('Strategy not found:', error.detail);
      } else if (response.status === 400) {
        console.error('Invalid ticker or data:', error.detail);
      } else if (response.status === 422) {
        console.error('Validation error:', error.detail);
      } else {
        console.error('Server error:', error.detail);
      }
      return;
    }

    const result: BacktestResponse = await response.json();
    console.log('Success:', result);
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

---

## Additional Notes

### Interval Values
Valid intervals: `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1wk`, `1mo`

**Note**: Intraday intervals (1m, 5m, etc.) have limited historical data (usually 30-60 days max from data provider).

### Date Formats
All dates use ISO 8601 format: `YYYY-MM-DD` (e.g., `2024-01-15`)

### Performance Tips
1. Use `columnar_format=true` for chart data (50% smaller payload)
2. Set `include_chart_data=false` when chart isn't needed
3. Market scans take 5-15 minutes - consider caching results
4. Use pagination on `/runs` and `/presets` endpoints

### CORS
The API allows all origins by default. Configure `CORS_ORIGINS` in production.

### Database
- SQLite database at `data/backtest_runs.db`
- Automatic migrations on schema changes
- Run history saved automatically
- Portfolio and presets persistent across sessions

---

**For interactive API documentation, visit:** `http://localhost:8000/docs`
