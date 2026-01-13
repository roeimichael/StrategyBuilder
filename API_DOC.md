# API Documentation

## Overview

StrategyBuilder provides a REST API for backtesting trading strategies built on Backtrader. The API is built with FastAPI and provides endpoints for strategy execution, market data fetching, and strategy discovery.

**Base URL:** `http://localhost:8086`

**Tech Stack:** FastAPI + Uvicorn

---

## Quick Start

```bash
# Start the API server
python run_api.py

# Test the API
python test_api.py
```

---

## API Endpoints

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "StrategyBuilder API",
  "version": "1.0",
  "endpoints": [...]
}
```

---

### 2. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 3. List All Strategies

**GET** `/strategies`

Get all available trading strategies.

**Response:**
```json
{
  "strategies": [
    {
      "name": "williams_r_strategy",
      "description": "Williams %R Oscillator Strategy",
      "parameters": {...}
    },
    ...
  ]
}
```

---

### 4. Get Strategy Details

**GET** `/strategies/{strategy_name}`

Get detailed information about a specific strategy.

**Path Parameters:**
- `strategy_name` (string, required): Name of the strategy module (e.g., "williams_r_strategy")

**Response:**
```json
{
  "name": "williams_r_strategy",
  "description": "Williams %R Oscillator Strategy",
  "parameters": {
    "period": 14,
    "upper_threshold": -20,
    "lower_threshold": -80
  }
}
```

---

### 5. Execute Backtest

**POST** `/backtest`

Execute a trading strategy backtest with historical data.

**Request Body:**
```json
{
  "ticker": "BTC-USD",
  "strategy": "williams_r_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "parameters": {
    "period": 14,
    "upper_threshold": -20,
    "lower_threshold": -80
  },
  "include_chart_data": true,
  "columnar_format": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticker` | string | Yes | - | Stock/crypto ticker (e.g., "AAPL", "BTC-USD") |
| `strategy` | string | Yes | - | Strategy module name without .py extension |
| `start_date` | string | No | 1 year ago | Backtest start date (YYYY-MM-DD) |
| `end_date` | string | No | today | Backtest end date (YYYY-MM-DD) |
| `interval` | string | No | "1d" | Data interval: "1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo" |
| `cash` | float | No | 10000.0 | Initial capital |
| `parameters` | object | No | strategy defaults | Strategy-specific parameters |
| `include_chart_data` | boolean | No | false | Include OHLC + indicators + trades for charting |
| `columnar_format` | boolean | No | true | Use columnar format for chart data (recommended) |

**Response:**

Basic response (without chart data):
```json
{
  "success": true,
  "ticker": "BTC-USD",
  "strategy": "williams_r_strategy",
  "start_value": 10000.0,
  "end_value": 11500.0,
  "pnl": 1500.0,
  "return_pct": 15.0,
  "sharpe_ratio": 1.25,
  "max_drawdown": 8.5,
  "max_drawdown_pct": 8.5,
  "total_trades": 15,
  "winning_trades": 9,
  "losing_trades": 6,
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "parameters_used": {...},
  "advanced_metrics": {
    "win_rate": 60.0,
    "profit_factor": 1.8,
    "payoff_ratio": 1.5,
    "calmar_ratio": 1.76,
    "sortino_ratio": 1.45,
    "max_consecutive_wins": 4,
    "max_consecutive_losses": 3,
    "avg_win": 250.0,
    "avg_loss": -166.67,
    "largest_win": 450.0,
    "largest_loss": -300.0,
    "avg_trade_duration": 5.2,
    "total_fees": 15.0,
    "expectancy": 100.0
  }
}
```

With chart data (columnar format):
```json
{
  ...all above fields...,
  "chart_data": {
    "date": ["2024-01-01", "2024-01-02", ...],
    "open": [42000.0, 42500.0, ...],
    "high": [43000.0, 43200.0, ...],
    "low": [41500.0, 42000.0, ...],
    "close": [42500.0, 43000.0, ...],
    "volume": [1000000.0, 1200000.0, ...],
    "indicators": {
      "Williams_R": [-50.0, -45.0, ...],
      "SMA_20": [42100.0, 42150.0, ...]
    },
    "trade_markers": [
      [],
      [{"type": "buy", "price": 42500.0, "size": 0.235}],
      ...
    ]
  }
}
```

**Error Response:**
```json
{
  "detail": "Strategy not found: invalid_strategy"
}
```

---

### 6. Fetch Market Data

**POST** `/market-data`

Fetch historical market data from Yahoo Finance (with SQLite caching).

**Request Body:**
```json
{
  "ticker": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d"
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "data": [
    {
      "date": "2024-01-01",
      "open": 185.0,
      "high": 187.5,
      "low": 184.0,
      "close": 186.5,
      "volume": 50000000
    },
    ...
  ],
  "from_cache": false
}
```

---

### 7. Get Default Parameters

**GET** `/parameters/default`

Get default backtest configuration parameters.

**Response:**
```json
{
  "cash": 10000.0,
  "commission": 0.001,
  "position_size": 0.95,
  "interval": "1d",
  "backtest_period_days": 365
}
```

---

## Response Metrics Explained

### Basic Metrics

- **start_value**: Initial portfolio value
- **end_value**: Final portfolio value
- **pnl**: Profit and Loss (end_value - start_value)
- **return_pct**: Return percentage ((end_value - start_value) / start_value * 100)
- **sharpe_ratio**: Risk-adjusted return (higher is better, >1 is good)
- **max_drawdown**: Maximum peak-to-trough decline in portfolio value
- **max_drawdown_pct**: Maximum drawdown as percentage
- **total_trades**: Number of completed trades
- **winning_trades**: Number of profitable trades
- **losing_trades**: Number of losing trades

### Advanced Metrics

- **win_rate**: Percentage of winning trades
- **profit_factor**: Gross profit / Gross loss (>1 means profitable, >2 is excellent)
- **payoff_ratio**: Average win / Average loss (>1 means wins are larger than losses)
- **calmar_ratio**: Annual return / Max drawdown (higher is better)
- **sortino_ratio**: Like Sharpe but only considers downside volatility
- **max_consecutive_wins/losses**: Longest winning/losing streak
- **avg_win/loss**: Average profit/loss per winning/losing trade
- **largest_win/loss**: Biggest single win/loss
- **avg_trade_duration**: Average time in position (in bars)
- **total_fees**: Total commission fees paid
- **expectancy**: Expected value per trade (average PnL per trade)

---

## Chart Data Format

### Columnar Format (Recommended)

**Pros:** More compact, efficient for frontend charting libraries

```json
{
  "date": [...],          // Array of date strings
  "open": [...],          // Array of open prices
  "high": [...],          // Array of high prices
  "low": [...],           // Array of low prices
  "close": [...],         // Array of close prices
  "volume": [...],        // Array of volumes
  "indicators": {
    "indicator_name": [...] // Arrays of indicator values
  },
  "trade_markers": [...]  // Array of arrays (trades per bar)
}
```

### Row Format (Alternative)

**Pros:** Easier to iterate, each bar is self-contained

```json
[
  {
    "date": "2024-01-01",
    "open": 42000.0,
    "high": 43000.0,
    "low": 41500.0,
    "close": 42500.0,
    "volume": 1000000.0,
    "indicators": {
      "Williams_R": -50.0,
      "SMA_20": 42100.0
    },
    "trade_markers": [
      {"type": "buy", "price": 42500.0, "size": 0.235}
    ]
  },
  ...
]
```

---

## Trade Marker Format

Each trade marker contains:

```json
{
  "type": "buy",           // "buy" or "sell"
  "price": 42500.0,        // Execution price
  "size": 0.235,           // Position size
  "value": 10000.0,        // Total trade value
  "commission": 10.0,      // Commission paid
  "pnl": 500.0             // Profit/loss (for sell orders)
}
```

---

## Example Usage

### Basic Backtest
```bash
curl -X POST http://localhost:8086/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "strategy": "williams_r_strategy",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

### Backtest with Custom Parameters
```bash
curl -X POST http://localhost:8086/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC-USD",
    "strategy": "rsi_stochastic_strategy",
    "interval": "1h",
    "cash": 50000.0,
    "parameters": {
      "rsi_period": 10,
      "rsi_upper": 75,
      "rsi_lower": 25
    }
  }'
```

### Backtest with Chart Data
```bash
curl -X POST http://localhost:8086/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA",
    "strategy": "bollinger_bands_strategy",
    "include_chart_data": true,
    "columnar_format": true
  }'
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (strategy doesn't exist) |
| 500 | Internal Server Error (backtest failed) |

---

## Performance Notes

- **Response size without chart data:** ~1-2 KB
- **Response size with chart data (1 year, daily):** ~500 KB - 1 MB
- **Response compression:** GZip enabled by default
- **Data caching:** Market data is cached in SQLite for faster subsequent requests
- **Recommended:** Use columnar format for chart data (more compact)

---

## Rate Limits

Currently no rate limits implemented. The API can handle concurrent requests, but backtests are CPU-intensive operations.

---

## Testing

Use the provided test script:

```bash
# Run comprehensive API tests
python test_api.py

# Test optimization endpoint
python test_optimization.py
```
