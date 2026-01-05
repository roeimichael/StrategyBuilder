# StrategyBuilder API Documentation

**Version:** 2.0.0
**Base URL:** `http://localhost:8000`
**Format:** JSON

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Performance & Timing](#performance--timing)
7. [Example Workflows](#example-workflows)

---

## Overview

The StrategyBuilder API is a backtesting platform for algorithmic trading strategies. It allows you to:
- Test trading strategies on historical stock data
- Fetch market data for any ticker
- View available strategies and their parameters
- Run backtests with custom parameters

**Key Features:**
- 12 pre-built trading strategies
- Configurable backtesting parameters
- Real-time market data fetching
- Detailed performance metrics

---

## Quick Start

### 1. Check if API is Running

```javascript
fetch('http://localhost:8000/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T12:30:45.123456"
}
```

### 2. List Available Strategies

```javascript
fetch('http://localhost:8000/strategies')
  .then(res => res.json())
  .then(data => console.log(data.strategies));
```

### 3. Run a Simple Backtest

```javascript
fetch('http://localhost:8000/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: "AAPL",
    strategy: "bollinger_bands_strategy",
    start_date: "2023-01-01",
    end_date: "2023-12-31",
    interval: "1d",
    cash: 10000.0
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## API Endpoints

### 1. Root / Welcome

**Endpoint:** `GET /`

**Description:** Get API information and available endpoints

**Request:** No parameters needed

**Response:**
```json
{
  "name": "StrategyBuilder API",
  "version": "2.0.0",
  "status": "running",
  "docs": "/docs",
  "endpoints": {
    "strategies": "/strategies",
    "backtest": "/backtest",
    "market_data": "/market-data",
    "health": "/health"
  }
}
```

---

### 2. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running and responsive

**Request:** No parameters needed

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T12:30:45.123456"
}
```

**Typical Response Time:** < 50ms

---

### 3. List All Strategies

**Endpoint:** `GET /strategies`

**Description:** Get a list of all available trading strategies

**Request:** No parameters needed

**Response:**
```json
{
  "success": true,
  "count": 12,
  "strategies": [
    {
      "module": "bollinger_bands_strategy",
      "class_name": "Bollinger_three",
      "description": "Bollinger Bands mean reversion strategy"
    },
    {
      "module": "adx_strategy",
      "class_name": "adx_strat",
      "description": "ADX adaptive strategy switching between trend following and mean reversion"
    }
    // ... more strategies
  ]
}
```

**Available Strategies:**
1. `bollinger_bands_strategy` - Mean reversion using Bollinger Bands
2. `adx_strategy` - Adaptive trend/mean reversion based on ADX
3. `alligator_strategy` - Long/short positions using Alligator indicator
4. `williams_r_strategy` - Williams %R oscillator mean reversion
5. `mfi_strategy` - Money Flow Index volume-based signals
6. `rsi_stochastic_strategy` - Combined RSI and Stochastic oscillators
7. `cci_atr_strategy` - CCI with ATR volatility breakout
8. `keltner_channel_strategy` - Keltner Channel breakout
9. `tema_crossover_strategy` - TEMA 20/60 crossover with volume
10. `tema_macd_strategy` - Combined TEMA and MACD signals
11. `momentum_multi_strategy` - Multi-indicator momentum (ROC, RSI, OBV)
12. `cmf_atr_macd_strategy` - MACD, CMF, ATR with stop loss/take profit

**Typical Response Time:** < 100ms

---

### 4. Get Strategy Information

**Endpoint:** `GET /strategies/{strategy_name}`

**Description:** Get detailed information about a specific strategy including its parameters

**URL Parameters:**
- `strategy_name` (string, required) - The module name of the strategy

**Example Request:**
```javascript
fetch('http://localhost:8000/strategies/bollinger_bands_strategy')
  .then(res => res.json())
  .then(data => console.log(data));
```

**Response:**
```json
{
  "success": true,
  "strategy": {
    "module": "bollinger_bands_strategy",
    "class_name": "Bollinger_three",
    "description": "Bollinger Bands mean reversion strategy",
    "parameters": {
      "period": 20,
      "devfactor": 2
    }
  }
}
```

**Typical Response Time:** < 100ms

---

### 5. Get Default Parameters

**Endpoint:** `GET /parameters/default`

**Description:** Get the default configuration parameters used across all strategies

**Request:** No parameters needed

**Response:**
```json
{
  "success": true,
  "parameters": {
    "cash": 10000.0,
    "macd1": 12,
    "macd2": 26,
    "macdsig": 9,
    "atrperiod": 14,
    "atrdist": 3.0,
    "order_pct": 0.95,
    "position_size_pct": 95
  }
}
```

**Parameter Descriptions:**
- `cash` - Starting cash for backtest ($)
- `macd1` - MACD fast period
- `macd2` - MACD slow period
- `macdsig` - MACD signal period
- `atrperiod` - ATR calculation period
- `atrdist` - ATR distance multiplier for stops
- `order_pct` - Percentage of cash to use per order (0-1)
- `position_size_pct` - Position size percentage (0-100)

**Typical Response Time:** < 50ms

---

### 6. Run Backtest

**Endpoint:** `POST /backtest`

**Description:** Execute a backtest for a given strategy and ticker

**Request Body:**
```json
{
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "parameters": {
    "position_size_pct": 80,
    "period": 20
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker symbol (e.g., "AAPL", "MSFT") |
| `strategy` | string | Yes | Strategy module name |
| `start_date` | string | No | Start date (YYYY-MM-DD). Defaults to 1 year ago |
| `end_date` | string | No | End date (YYYY-MM-DD). Defaults to today |
| `interval` | string | No | Data interval. Default: "1d" |
| `cash` | number | No | Starting cash. Default: 10000.0 |
| `parameters` | object | No | Custom strategy parameters |

**Valid Intervals:**
- `"1m"` - 1 minute
- `"5m"` - 5 minutes
- `"15m"` - 15 minutes
- `"30m"` - 30 minutes
- `"1h"` - 1 hour
- `"1d"` - 1 day (default)
- `"1wk"` - 1 week
- `"1mo"` - 1 month

**Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_value": 10000.0,
  "end_value": 11250.75,
  "pnl": 1250.75,
  "return_pct": 12.51,
  "sharpe_ratio": 1.45,
  "max_drawdown": 8.32,
  "total_trades": 15,
  "interval": "1d",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "advanced_metrics": {
    "win_rate": 60.0,
    "profit_factor": 2.34,
    "payoff_ratio": 1.8,
    "calmar_ratio": 1.5,
    "sortino_ratio": 1.89,
    "max_consecutive_wins": 4,
    "max_consecutive_losses": 3,
    "avg_win": 150.25,
    "avg_loss": -83.45,
    "largest_win": 320.50,
    "largest_loss": -180.25,
    "expectancy": 83.38
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether backtest completed successfully |
| `ticker` | string | Stock ticker tested |
| `strategy` | string | Strategy name used |
| `start_value` | number | Starting portfolio value ($) |
| `end_value` | number | Ending portfolio value ($) |
| `pnl` | number | Profit/Loss ($) |
| `return_pct` | number | Return percentage |
| `sharpe_ratio` | number/null | Sharpe ratio (risk-adjusted return) |
| `max_drawdown` | number/null | Maximum drawdown percentage |
| `total_trades` | number | Number of trades executed |
| `interval` | string | Data interval used |
| `start_date` | string | Actual start date |
| `end_date` | string | Actual end date |
| `advanced_metrics` | object | Detailed performance metrics |

**Advanced Metrics Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `win_rate` | number | Percentage of winning trades |
| `profit_factor` | number/null | Gross profit / Gross loss |
| `payoff_ratio` | number/null | Avg win / Avg loss |
| `calmar_ratio` | number/null | Annual return / Max drawdown |
| `sortino_ratio` | number/null | Downside risk-adjusted return |
| `max_consecutive_wins` | number | Longest winning streak |
| `max_consecutive_losses` | number | Longest losing streak |
| `avg_win` | number | Average winning trade ($) |
| `avg_loss` | number | Average losing trade ($) |
| `largest_win` | number | Largest winning trade ($) |
| `largest_loss` | number | Largest losing trade ($) |
| `expectancy` | number | Expected value per trade ($) |

**Chart Data Fields:**

The `chart_data` object contains all data needed for frontend charting and visualization:

| Field | Type | Description |
|-------|------|-------------|
| `ohlc` | array | OHLC price data for each bar in the backtest |
| `indicators` | object | Technical indicators used by the strategy |
| `trade_markers` | array | Buy/sell positions with dates, prices, and PnL |

**OHLC Data Structure:**
```javascript
{
  date: "2024-01-01T00:00:00",  // ISO format datetime
  open: 150.25,
  high: 152.10,
  low: 149.80,
  close: 151.50,
  volume: 1000000
}
```

**Indicators Structure:**
The indicators object contains arrays of values for each technical indicator used by the strategy. The keys are indicator names (e.g., `"boll_top"`, `"boll_mid"`, `"boll_bot"` for Bollinger Bands). Each array has the same length as the OHLC data.

```javascript
{
  "boll_top": [152.5, 153.0, 153.2, ...],
  "boll_mid": [150.0, 150.5, 150.8, ...],
  "boll_bot": [147.5, 148.0, 148.4, ...]
}
```

**Trade Markers Structure:**
```javascript
{
  date: "2024-01-05T00:00:00",
  price: 149.80,
  type: "BUY",                  // "BUY" or "SELL"
  action: "OPEN",               // "OPEN" or "CLOSE"
  pnl: 140.0                    // Only present on "CLOSE" actions
}
```

**Typical Response Time:** 2-10 seconds (depends on date range and interval)

---

### 7. Get Market Data

**Endpoint:** `POST /market-data`

**Description:** Fetch historical market data for a ticker

**Request Body:**
```json
{
  "ticker": "AAPL",
  "period": "1mo",
  "interval": "1d"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker symbol |
| `period` | string | No | Time period. Default: "1mo" |
| `interval` | string | No | Data interval. Default: "1d" |

**Valid Periods:**
- `"1d"`, `"5d"`, `"1mo"`, `"3mo"`, `"6mo"`, `"1y"`, `"2y"`, `"5y"`, `"10y"`, `"ytd"`, `"max"`

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
      "Date": "2023-12-01T00:00:00",
      "Open": 189.92,
      "High": 191.08,
      "Low": 189.23,
      "Close": 190.33,
      "Volume": 45123400,
      "Adj Close": 190.33
    }
    // ... more data points
  ],
  "statistics": {
    "mean": 191.45,
    "std": 3.21,
    "min": 185.32,
    "max": 195.89,
    "volume_avg": 48234567
  }
}
```

**Typical Response Time:** 1-3 seconds

---

## Data Models

### BacktestRequest

```typescript
interface BacktestRequest {
  ticker: string;                    // Stock ticker (e.g., "AAPL")
  strategy: string;                  // Strategy module name
  start_date?: string;               // Format: "YYYY-MM-DD"
  end_date?: string;                 // Format: "YYYY-MM-DD"
  interval?: string;                 // "1m"|"5m"|"15m"|"30m"|"1h"|"1d"|"1wk"|"1mo"
  cash?: number;                     // Starting cash (default: 10000.0)
  parameters?: {                     // Custom strategy parameters
    [key: string]: number;
  };
}
```

### BacktestResponse

```typescript
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
  advanced_metrics: AdvancedMetrics;
  chart_data?: ChartData;  // Optional charting data for visualization
}

interface AdvancedMetrics {
  win_rate: number;
  profit_factor: number | null;
  payoff_ratio: number | null;
  calmar_ratio: number | null;
  sortino_ratio: number | null;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
  avg_win: number;
  avg_loss: number;
  largest_win: number;
  largest_loss: number;
  expectancy: number;
}

interface ChartData {
  ohlc: OHLCData[];             // OHLC price data for charting
  indicators: {                 // Technical indicators used by strategy
    [key: string]: (number | null)[];
  };
  trade_markers: TradeMarker[]; // Buy/sell positions
}

interface OHLCData {
  date: string;                 // ISO format date/datetime
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TradeMarker {
  date: string;                 // ISO format date/datetime
  price: number;                // Entry/exit price
  type: "BUY" | "SELL";         // Trade direction
  action: "OPEN" | "CLOSE";     // Opening or closing position
  pnl?: number;                 // Profit/loss (only on CLOSE)
}
```

### MarketDataRequest

```typescript
interface MarketDataRequest {
  ticker: string;
  period?: string;    // "1d"|"5d"|"1mo"|"3mo"|"6mo"|"1y"|"2y"|"5y"|"10y"|"ytd"|"max"
  interval?: string;  // "1m"|"5m"|"15m"|"30m"|"1h"|"1d"|"1wk"|"1mo"
}
```

### StrategyInfo

```typescript
interface StrategyInfo {
  module: string;
  class_name: string;
  description: string;
  parameters?: {
    [key: string]: any;
  };
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameters or missing required fields |
| 404 | Not Found | Strategy or ticker not found |
| 500 | Server Error | Internal processing error |

### Example Error Responses

**Invalid Strategy:**
```json
{
  "detail": "Strategy module 'invalid_strategy' not found"
}
```

**Invalid Ticker:**
```json
{
  "detail": "No data available for INVALID"
}
```

**Missing Required Field:**
```json
{
  "detail": "Field 'ticker' is required"
}
```

---

## Performance & Timing

### Expected Response Times

| Endpoint | Typical Time | Notes |
|----------|-------------|-------|
| `GET /` | < 50ms | Simple metadata |
| `GET /health` | < 50ms | Quick check |
| `GET /strategies` | < 100ms | Lists 12 strategies |
| `GET /strategies/{name}` | < 100ms | Single strategy info |
| `GET /parameters/default` | < 50ms | Simple config |
| `POST /backtest` | 2-10s | **Depends on date range** |
| `POST /market-data` | 1-3s | Depends on period |

### Backtest Timing Guidelines

- **90 days, 1d interval:** ~2-3 seconds
- **1 year, 1d interval:** ~3-5 seconds
- **30 days, 1h interval:** ~5-8 seconds
- **5 days, 5m interval:** ~8-10 seconds

**Tip:** For better UX, show a loading indicator during backtests.

---

## Example Workflows

### Workflow 1: Simple Backtest

```javascript
// 1. Check API health
const health = await fetch('http://localhost:8000/health')
  .then(res => res.json());

// 2. Get available strategies
const strategies = await fetch('http://localhost:8000/strategies')
  .then(res => res.json());

// 3. Run backtest
const backtest = await fetch('http://localhost:8000/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: "AAPL",
    strategy: "bollinger_bands_strategy",
    start_date: "2023-01-01",
    end_date: "2023-12-31",
    interval: "1d",
    cash: 10000.0
  })
}).then(res => res.json());

console.log(`Return: ${backtest.return_pct}%`);
console.log(`Win Rate: ${backtest.advanced_metrics.win_rate}%`);
```

### Workflow 2: Strategy Comparison

```javascript
const tickers = ["AAPL", "MSFT", "GOOGL"];
const strategies = ["bollinger_bands_strategy", "rsi_stochastic_strategy"];

for (const ticker of tickers) {
  for (const strategy of strategies) {
    const result = await fetch('http://localhost:8000/backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticker,
        strategy,
        start_date: "2023-01-01",
        end_date: "2023-12-31",
        cash: 10000.0
      })
    }).then(res => res.json());

    console.log(`${ticker} + ${strategy}: ${result.return_pct}%`);
  }
}
```

### Workflow 3: Parameter Optimization

```javascript
const periods = [10, 20, 30, 40, 50];
const results = [];

for (const period of periods) {
  const result = await fetch('http://localhost:8000/backtest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: "AAPL",
      strategy: "bollinger_bands_strategy",
      start_date: "2023-01-01",
      end_date: "2023-12-31",
      cash: 10000.0,
      parameters: {
        period: period,
        devfactor: 2
      }
    })
  }).then(res => res.json());

  results.push({
    period,
    return: result.return_pct,
    sharpe: result.sharpe_ratio
  });
}

// Find best period
const best = results.reduce((a, b) =>
  a.sharpe > b.sharpe ? a : b
);

console.log(`Best period: ${best.period} (Sharpe: ${best.sharpe})`);
```

---

## React Example Component

```jsx
import React, { useState } from 'react';

function BacktestRunner() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runBacktest = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker: "AAPL",
          strategy: "bollinger_bands_strategy",
          start_date: "2023-01-01",
          end_date: "2023-12-31",
          cash: 10000.0
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Backtest failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={runBacktest} disabled={loading}>
        {loading ? 'Running...' : 'Run Backtest'}
      </button>

      {result && (
        <div>
          <h3>Results</h3>
          <p>Return: {result.return_pct.toFixed(2)}%</p>
          <p>Sharpe Ratio: {result.sharpe_ratio?.toFixed(2)}</p>
          <p>Win Rate: {result.advanced_metrics.win_rate.toFixed(2)}%</p>
          <p>Total Trades: {result.total_trades}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Chart Data Visualization Example

The `chart_data` field in backtest responses provides everything needed to create interactive charts with indicators and trade markers.

### Using Chart Data with Recharts

```jsx
import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceDot } from 'recharts';

function BacktestChart() {
  const [chartData, setChartData] = useState(null);

  const runBacktest = async () => {
    const response = await fetch('http://localhost:8000/backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticker: "AAPL",
        strategy: "bollinger_bands_strategy",
        start_date: "2024-01-01",
        cash: 10000.0
      })
    });
    const data = await response.json();
    setChartData(data.chart_data);
  };

  // Combine OHLC data with indicators for charting
  const prepareChartData = () => {
    if (!chartData) return [];

    return chartData.ohlc.map((bar, index) => {
      const point = {
        date: bar.date,
        close: bar.close,
        open: bar.open,
        high: bar.high,
        low: bar.low
      };

      // Add all indicators
      Object.keys(chartData.indicators).forEach(key => {
        point[key] = chartData.indicators[key][index];
      });

      return point;
    });
  };

  // Render trade markers as arrows
  const renderTradeMarkers = () => {
    if (!chartData) return null;

    return chartData.trade_markers.map((marker, idx) => {
      const color = marker.action === 'OPEN'
        ? (marker.type === 'BUY' ? '#00ff00' : '#ff0000')
        : (marker.type === 'SELL' ? '#00ff00' : '#ff0000');

      return (
        <ReferenceDot
          key={idx}
          x={marker.date}
          y={marker.price}
          r={5}
          fill={color}
          stroke={color}
          label={marker.action === 'OPEN' ? '▼' : '▲'}
        />
      );
    });
  };

  const data = prepareChartData();

  return (
    <div>
      <button onClick={runBacktest}>Run Backtest</button>

      {chartData && (
        <LineChart width={1200} height={600} data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />

          {/* Price line */}
          <Line type="monotone" dataKey="close" stroke="#8884d8" name="Close Price" />

          {/* Render all indicators dynamically */}
          {Object.keys(chartData.indicators).map((key, idx) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={`hsl(${idx * 60}, 70%, 50%)`}
              name={key}
              strokeWidth={1}
            />
          ))}

          {/* Trade markers */}
          {renderTradeMarkers()}
        </LineChart>
      )}
    </div>
  );
}
```

### Chart Data Structure Example

For a Bollinger Bands strategy, the chart_data would look like:

```javascript
{
  "chart_data": {
    "ohlc": [
      {
        "date": "2024-01-02T00:00:00",
        "open": 185.36,
        "high": 186.89,
        "low": 184.95,
        "close": 185.64,
        "volume": 58414460
      },
      // ... more bars
    ],
    "indicators": {
      "boll_top": [187.23, 187.45, 187.89, ...],
      "boll_mid": [185.50, 185.60, 185.75, ...],
      "boll_bot": [183.77, 183.75, 183.61, ...]
    },
    "trade_markers": [
      {
        "date": "2024-01-05T00:00:00",
        "price": 183.92,
        "type": "BUY",
        "action": "OPEN"
      },
      {
        "date": "2024-01-10T00:00:00",
        "price": 186.15,
        "type": "SELL",
        "action": "CLOSE",
        "pnl": 223.0
      }
    ]
  }
}
```

### Key Points for Charting

1. **OHLC and Indicators Alignment**: The indicator arrays have the same length as the OHLC data array, so you can combine them by index.

2. **Dynamic Indicators**: Different strategies use different indicators. The indicator keys will vary (e.g., Bollinger Bands has `boll_top`, `boll_mid`, `boll_bot`, while RSI strategy has `rsi`).

3. **Trade Markers**:
   - `OPEN` actions show where positions were entered
   - `CLOSE` actions show where positions were exited and include PnL
   - Use different colors/arrows for BUY vs SELL

4. **Date Format**: All dates are in ISO format and can be used directly in most charting libraries.

---

## Need Help?

- **Interactive API Docs:** Visit `http://localhost:8000/docs` for Swagger UI
- **Check Logs:** Error details are logged to `logs/api_errors.log`
- **Test Script:** Run `python test_api_capture.py` to see example requests/responses

---

**Last Updated:** 2026-01-04
**API Version:** 2.0.0
