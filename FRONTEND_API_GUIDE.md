# StrategyBuilder API - Frontend Developer Guide

Complete reference for building a frontend application that integrates with the StrategyBuilder backtesting API.

## Table of Contents
1. [Overview](#overview)
2. [Base Configuration](#base-configuration)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Response Timing & Performance](#response-timing--performance)
5. [Error Handling](#error-handling)
6. [Data Types & Structures](#data-types--structures)
7. [Common Use Cases](#common-use-cases)
8. [Best Practices](#best-practices)

---

## Overview

### API Architecture
- **Type**: RESTful JSON API
- **Protocol**: HTTP/HTTPS
- **Data Format**: JSON (request and response)
- **Authentication**: None (add your own if needed)
- **CORS**: Enabled for all origins (configure in production)

### Base Information
- **Default Port**: 8000
- **Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

---

## Base Configuration

### Required Headers
All POST requests must include:
```javascript
{
  "Content-Type": "application/json"
}
```

### Connection Setup

**JavaScript/TypeScript:**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
};
```

**Python:**
```python
import requests

API_BASE_URL = "http://localhost:8000"

def api_get(endpoint):
    response = requests.get(f"{API_BASE_URL}{endpoint}")
    response.raise_for_status()
    return response.json()

def api_post(endpoint, data):
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json=data
    )
    response.raise_for_status()
    return response.json()
```

---

## API Endpoints Reference

### 1. GET / (Root)

**Purpose**: Get API information and available endpoints

**Request:**
```
GET /
```

**Response Time**: < 50ms

**Response Structure:**
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

**Use Case**: Display API version in UI footer, verify connection

---

### 2. GET /health

**Purpose**: Check if API is responsive

**Request:**
```
GET /health
```

**Response Time**: < 50ms

**Response Structure:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Use Case**:
- Connection status indicator
- Periodic health checks (every 30-60 seconds)
- Before running expensive operations

**Frontend Implementation:**
```javascript
// Health check with indicator
async function checkHealth() {
  try {
    const response = await apiClient.get('/health');
    if (response.status === 'healthy') {
      showGreenDot(); // Connected
      return true;
    }
  } catch (error) {
    showRedDot(); // Disconnected
    return false;
  }
}

// Run every 30 seconds
setInterval(checkHealth, 30000);
```

---

### 3. GET /strategies

**Purpose**: List all available trading strategies

**Request:**
```
GET /strategies
```

**Response Time**: 100-300ms (first call), < 50ms (cached)

**Response Structure:**
```json
{
  "success": true,
  "count": 12,
  "strategies": [
    {
      "module": "bollinger_bands_strategy",
      "class_name": "Bollinger_three",
      "description": ""
    },
    {
      "module": "tema_macd_strategy",
      "class_name": "TEMA_MACD",
      "description": ""
    }
  ]
}
```

**Field Descriptions:**
- `success`: Always true if request succeeded
- `count`: Total number of strategies available
- `strategies`: Array of strategy objects
  - `module`: Use this value for backtest requests
  - `class_name`: Display name for UI
  - `description`: Usually empty (documentation removed)

**Use Case**: Populate strategy dropdown/selector

**Frontend Implementation:**
```javascript
async function loadStrategies() {
  const data = await apiClient.get('/strategies');

  // Create dropdown options
  const options = data.strategies.map(strategy => ({
    value: strategy.module,
    label: strategy.class_name || strategy.module,
    description: strategy.description
  }));

  return options;
}

// Example UI rendering
<select id="strategy-selector">
  {options.map(opt => (
    <option value={opt.value}>{opt.label}</option>
  ))}
</select>
```

---

### 4. GET /strategies/{strategy_name}

**Purpose**: Get detailed information about a specific strategy

**Request:**
```
GET /strategies/bollinger_bands_strategy
```

**Response Time**: 50-150ms

**Response Structure:**
```json
{
  "success": true,
  "strategy": {
    "module": "bollinger_bands_strategy",
    "class_name": "Bollinger_three",
    "description": "",
    "parameters": {
      "period": 20,
      "devfactor": 2
    }
  }
}
```

**Field Descriptions:**
- `parameters`: Strategy-specific parameters with default values
  - Each strategy has different parameters
  - These can be overridden in backtest requests

**Use Case**:
- Show strategy details panel
- Display configurable parameters
- Advanced settings UI

**Frontend Implementation:**
```javascript
async function showStrategyDetails(strategyName) {
  const data = await apiClient.get(`/strategies/${strategyName}`);

  const strategy = data.strategy;

  // Display parameters as editable fields
  const paramInputs = Object.entries(strategy.parameters).map(([key, value]) => ({
    name: key,
    defaultValue: value,
    type: typeof value === 'number' ? 'number' : 'text'
  }));

  return {
    name: strategy.class_name,
    params: paramInputs
  };
}
```

---

### 5. GET /parameters/default

**Purpose**: Get default backtesting parameters

**Request:**
```
GET /parameters/default
```

**Response Time**: < 50ms

**Response Structure:**
```json
{
  "success": true,
  "parameters": {
    "cash": 10000,
    "macd1": 12,
    "macd2": 26,
    "macdsig": 9,
    "atrperiod": 14,
    "atrdist": 2.0,
    "order_pct": 1.0
  }
}
```

**Field Descriptions:**
- `cash`: Initial capital in USD
- `macd1`: MACD fast period
- `macd2`: MACD slow period
- `macdsig`: MACD signal period
- `atrperiod`: ATR indicator period
- `atrdist`: ATR distance multiplier
- `order_pct`: Order size as percentage of available cash (0.0-1.0)

**Use Case**:
- Initialize form defaults
- Reset to defaults button
- Advanced settings panel

---

### 6. POST /backtest

**Purpose**: Execute a trading strategy backtest

**Request:**
```
POST /backtest
Content-Type: application/json

{
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "interval": "1d",
  "cash": 10000.0,
  "parameters": {
    "period": 20,
    "devfactor": 2.5
  }
}
```

**Request Fields (All Required Except Noted):**

| Field | Type | Required | Description | Valid Values |
|-------|------|----------|-------------|--------------|
| ticker | string | Yes | Stock/crypto ticker symbol | Any valid ticker (AAPL, TSLA, BTC-USD) |
| strategy | string | Yes | Strategy module name | From GET /strategies |
| start_date | string | No | Backtest start date | YYYY-MM-DD format, defaults to 1 year ago |
| end_date | string | No | Backtest end date | YYYY-MM-DD format, defaults to today |
| interval | string | No | Data interval | 1m, 5m, 15m, 30m, 1h, 1d (default), 1wk, 1mo |
| cash | number | No | Initial capital | Any positive number, default 10000 |
| parameters | object | No | Strategy-specific params | Key-value pairs, see strategy info |

**Response Time**:
- **1 day interval**: 2-8 seconds for 1 year of data
- **1 hour interval**: 5-15 seconds for 1 year of data
- **1 minute interval**: 15-60 seconds for 1 month of data

**IMPORTANT TIMING NOTES:**
- First request for a ticker: Slower (downloads data)
- Subsequent requests: Faster (may use cached data)
- More data points = longer processing time
- Show loading indicator for 5+ seconds

**Response Structure:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_value": 10000.0,
  "end_value": 11234.56,
  "pnl": 1234.56,
  "return_pct": 12.35,
  "sharpe_ratio": 1.45,
  "max_drawdown": -5.23,
  "total_trades": 15,
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "advanced_metrics": {
    "win_rate": 60.0,
    "avg_win": 150.25,
    "avg_loss": -75.50,
    "profit_factor": 1.89,
    "total_wins": 9,
    "total_losses": 6
  }
}
```

**Response Fields:**

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| success | boolean | Request status | Always true on success |
| ticker | string | Ticker symbol used | Echo of request |
| strategy | string | Strategy used | Echo of request |
| start_value | number | Starting capital | Same as cash input |
| end_value | number | Final portfolio value | Includes cash + positions |
| pnl | number | Profit/Loss in dollars | end_value - start_value |
| return_pct | number | Return percentage | Can be negative |
| sharpe_ratio | number or null | Risk-adjusted return | null if insufficient data |
| max_drawdown | number or null | Maximum decline % | Always negative or 0 |
| total_trades | number | Number of trades executed | Can be 0 |
| interval | string | Data interval used | Echo of request |
| start_date | string | Actual start date | May differ from request |
| end_date | string | Actual end date | "today" if not specified |
| advanced_metrics | object or null | Detailed metrics | null if no trades |

**Advanced Metrics Fields:**

| Field | Type | Description |
|-------|------|-------------|
| win_rate | number | Percentage of winning trades (0-100) |
| avg_win | number | Average winning trade profit |
| avg_loss | number | Average losing trade loss (negative) |
| profit_factor | number | Gross profit / Gross loss |
| total_wins | number | Count of winning trades |
| total_losses | number | Count of losing trades |

**Frontend Implementation:**
```javascript
async function runBacktest(formData) {
  // Show loading spinner
  setLoading(true);
  setProgress(0);

  // Simulate progress for UX (actual request doesn't support progress)
  const progressInterval = setInterval(() => {
    setProgress(prev => Math.min(prev + 10, 90));
  }, 500);

  try {
    const result = await apiClient.post('/backtest', {
      ticker: formData.ticker.toUpperCase(),
      strategy: formData.strategy,
      start_date: formData.startDate,
      end_date: formData.endDate,
      interval: formData.interval || '1d',
      cash: parseFloat(formData.cash) || 10000,
      parameters: formData.advancedParams || {}
    });

    clearInterval(progressInterval);
    setProgress(100);

    // Process results
    return {
      profit: result.pnl,
      profitPercent: result.return_pct,
      sharpe: result.sharpe_ratio,
      maxDrawdown: result.max_drawdown,
      trades: result.total_trades,
      winRate: result.advanced_metrics?.win_rate || 0,
      profitable: result.return_pct > 0
    };

  } catch (error) {
    clearInterval(progressInterval);
    throw error;
  } finally {
    setLoading(false);
  }
}

// Display results
function displayResults(results) {
  const color = results.profitable ? 'green' : 'red';

  return (
    <div className="results">
      <h2 style={{color}}>
        {results.profitable ? '📈' : '📉'}
        {results.profitPercent.toFixed(2)}%
      </h2>
      <div className="metrics">
        <Metric label="Profit/Loss" value={`$${results.profit.toFixed(2)}`} />
        <Metric label="Sharpe Ratio" value={results.sharpe?.toFixed(2) || 'N/A'} />
        <Metric label="Max Drawdown" value={`${results.maxDrawdown?.toFixed(2)}%`} />
        <Metric label="Total Trades" value={results.trades} />
        <Metric label="Win Rate" value={`${results.winRate.toFixed(1)}%`} />
      </div>
    </div>
  );
}
```

---

### 7. POST /market-data

**Purpose**: Fetch historical market data for a ticker

**Request:**
```
POST /market-data
Content-Type: application/json

{
  "ticker": "MSFT",
  "period": "1mo",
  "interval": "1d"
}
```

**Request Fields:**

| Field | Type | Required | Description | Valid Values |
|-------|------|----------|-------------|--------------|
| ticker | string | Yes | Stock/crypto symbol | Any valid ticker |
| period | string | No | Time period | 1d, 5d, 1mo (default), 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max |
| interval | string | No | Data interval | 1m, 5m, 15m, 30m, 1h, 1d (default), 1wk, 1mo |

**Response Time**: 1-5 seconds (depends on period/interval)

**Response Structure:**
```json
{
  "success": true,
  "ticker": "MSFT",
  "period": "1mo",
  "interval": "1d",
  "data_points": 22,
  "data": [
    {
      "Date": "2024-01-02T00:00:00",
      "Open": 376.52,
      "High": 380.23,
      "Low": 375.91,
      "Close": 378.45,
      "Volume": 18500000
    },
    {
      "Date": "2024-01-03T00:00:00",
      "Open": 378.50,
      "High": 382.10,
      "Low": 377.88,
      "Close": 381.92,
      "Volume": 20100000
    }
  ],
  "statistics": {
    "mean": 379.25,
    "std": 2.35,
    "min": 375.91,
    "max": 385.67,
    "volume_avg": 19500000
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Request status |
| ticker | string | Ticker symbol |
| period | string | Time period requested |
| interval | string | Data interval |
| data_points | number | Number of data points returned |
| data | array | OHLCV data array |
| statistics | object | Statistical summary |

**Data Array Fields:**

| Field | Type | Description |
|-------|------|-------------|
| Date | string | ISO 8601 timestamp |
| Open | number | Opening price |
| High | number | Highest price |
| Low | number | Lowest price |
| Close | number | Closing price |
| Volume | number | Trading volume |

**Frontend Implementation:**
```javascript
async function loadChartData(ticker, period = '1mo') {
  const data = await apiClient.post('/market-data', {
    ticker: ticker.toUpperCase(),
    period: period,
    interval: period.includes('d') && parseInt(period) <= 5 ? '1h' : '1d'
  });

  // Format for charting library (e.g., Chart.js)
  const chartData = {
    labels: data.data.map(d => new Date(d.Date).toLocaleDateString()),
    datasets: [{
      label: ticker,
      data: data.data.map(d => d.Close),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };

  return {
    chartData,
    stats: data.statistics,
    dataPoints: data.data_points
  };
}

// Display chart
import { Line } from 'react-chartjs-2';

function PriceChart({ ticker }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    loadChartData(ticker).then(setData);
  }, [ticker]);

  if (!data) return <Spinner />;

  return (
    <div>
      <Line data={data.chartData} />
      <div className="stats">
        <p>Average: ${data.stats.mean.toFixed(2)}</p>
        <p>Range: ${data.stats.min.toFixed(2)} - ${data.stats.max.toFixed(2)}</p>
      </div>
    </div>
  );
}
```

---

## Response Timing & Performance

### Expected Response Times

| Endpoint | Typical Response | Max Response | Notes |
|----------|------------------|--------------|-------|
| GET / | 20-50ms | 100ms | Instant |
| GET /health | 20-50ms | 100ms | Instant |
| GET /strategies | 50-200ms | 500ms | First call slower |
| GET /strategies/{name} | 50-150ms | 300ms | |
| GET /parameters/default | 20-50ms | 100ms | Instant |
| POST /backtest (1d, 1y) | 2-8s | 15s | Variable |
| POST /backtest (1h, 1y) | 5-15s | 30s | Variable |
| POST /backtest (1m, 1mo) | 10-30s | 60s | Slow |
| POST /market-data (1mo) | 1-3s | 10s | Variable |
| POST /market-data (1y) | 2-5s | 15s | Variable |

### Performance Considerations

**1. Loading States**
```javascript
// Always show loading for operations > 1 second
if (endpoint === '/backtest' || endpoint === '/market-data') {
  showLoadingSpinner();
  showEstimatedTime(); // "This may take 5-10 seconds"
}
```

**2. Timeout Configuration**
```javascript
const TIMEOUTS = {
  default: 5000,        // 5 seconds
  backtest: 60000,      // 60 seconds
  marketData: 15000     // 15 seconds
};

fetch(url, {
  signal: AbortSignal.timeout(TIMEOUTS.backtest)
});
```

**3. Request Debouncing**
```javascript
// Prevent duplicate backtest requests
const debouncedBacktest = debounce(runBacktest, 1000);
```

**4. Caching Strategy**
```javascript
// Cache market data for 5 minutes
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000;

async function getCachedMarketData(ticker, period) {
  const key = `${ticker}-${period}`;
  const cached = cache.get(key);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const data = await apiClient.post('/market-data', { ticker, period });
  cache.set(key, { data, timestamp: Date.now() });
  return data;
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Strategy not found, invalid endpoint |
| 500 | Server Error | Internal server error, data fetch failed |

### Error Response Format

All errors return JSON:
```json
{
  "detail": "Strategy module 'invalid_strategy' not found: No module named 'strategies.invalid_strategy'"
}
```

### Common Errors

**1. Invalid Strategy**
```json
// Request
POST /backtest
{"ticker": "AAPL", "strategy": "nonexistent", "interval": "1d", "cash": 10000}

// Response: 400 or 404
{"detail": "Strategy module 'nonexistent' not found: ..."}
```

**2. Invalid Ticker**
```json
// Request
POST /market-data
{"ticker": "INVALID123", "period": "1mo", "interval": "1d"}

// Response: 500
{"detail": "Failed to fetch market data: No data found for INVALID123"}
```

**3. No Data Available**
```json
// Response: 500
{"detail": "No data available for XYZ"}
```

**4. Invalid Date Format**
```json
// Request
POST /backtest
{"ticker": "AAPL", "strategy": "bollinger_bands_strategy", "start_date": "invalid-date"}

// Response: 400 or 500
{"detail": "time data 'invalid-date' does not match format '%Y-%m-%d'"}
```

### Frontend Error Handling

```javascript
async function safeApiCall(apiFunction, errorContext) {
  try {
    return await apiFunction();
  } catch (error) {
    // Network error
    if (error instanceof TypeError) {
      return {
        error: true,
        message: 'Cannot connect to API. Please check if the server is running.',
        type: 'network'
      };
    }

    // HTTP error
    if (error.message.includes('HTTP')) {
      const status = parseInt(error.message.match(/\d+/)[0]);

      if (status === 404) {
        return {
          error: true,
          message: 'Strategy not found. Please select a valid strategy.',
          type: 'not_found'
        };
      }

      if (status === 400) {
        return {
          error: true,
          message: 'Invalid request. Please check your inputs.',
          type: 'validation'
        };
      }

      if (status >= 500) {
        return {
          error: true,
          message: 'Server error. The ticker may be invalid or data unavailable.',
          type: 'server'
        };
      }
    }

    // Unknown error
    return {
      error: true,
      message: `Error in ${errorContext}: ${error.message}`,
      type: 'unknown'
    };
  }
}

// Usage
const result = await safeApiCall(
  () => apiClient.post('/backtest', backtestData),
  'backtest execution'
);

if (result.error) {
  showErrorNotification(result.message, result.type);
} else {
  displayResults(result);
}
```

---

## Data Types & Structures

### TypeScript Definitions

```typescript
// API Configuration
interface ApiConfig {
  baseUrl: string;
  timeout: number;
  headers: Record<string, string>;
}

// Strategy Info
interface Strategy {
  module: string;
  class_name: string;
  description: string;
}

interface StrategyDetail extends Strategy {
  parameters: Record<string, number | string>;
}

interface StrategiesResponse {
  success: boolean;
  count: number;
  strategies: Strategy[];
}

// Backtest Request
interface BacktestRequest {
  ticker: string;
  strategy: string;
  start_date?: string;  // YYYY-MM-DD
  end_date?: string;    // YYYY-MM-DD
  interval?: '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1wk' | '1mo';
  cash?: number;
  parameters?: Record<string, number | string>;
}

// Backtest Response
interface AdvancedMetrics {
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  profit_factor: number;
  total_wins: number;
  total_losses: number;
}

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
  advanced_metrics: AdvancedMetrics | null;
}

// Market Data Request
interface MarketDataRequest {
  ticker: string;
  period?: '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y' | '10y' | 'ytd' | 'max';
  interval?: '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1wk' | '1mo';
}

// Market Data Response
interface OHLCVData {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
}

interface Statistics {
  mean: number | null;
  std: number | null;
  min: number | null;
  max: number | null;
  volume_avg: number | null;
}

interface MarketDataResponse {
  success: boolean;
  ticker: string;
  period: string;
  interval: string;
  data_points: number;
  data: OHLCVData[];
  statistics: Statistics;
}

// Health Check
interface HealthResponse {
  status: string;
  timestamp: string;
}

// Default Parameters
interface DefaultParametersResponse {
  success: boolean;
  parameters: {
    cash: number;
    macd1: number;
    macd2: number;
    macdsig: number;
    atrperiod: number;
    atrdist: number;
    order_pct: number;
  };
}
```

---

## Common Use Cases

### Use Case 1: Basic Backtest Workflow

```javascript
// 1. Load available strategies
const strategies = await apiClient.get('/strategies');

// 2. User selects strategy
const selectedStrategy = 'bollinger_bands_strategy';

// 3. Get strategy details (optional)
const details = await apiClient.get(`/strategies/${selectedStrategy}`);

// 4. User fills form
const formData = {
  ticker: 'AAPL',
  strategy: selectedStrategy,
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  interval: '1d',
  cash: 10000
};

// 5. Run backtest
const results = await apiClient.post('/backtest', formData);

// 6. Display results
displayResults(results);
```

### Use Case 2: Strategy Comparison

```javascript
async function compareStrategies(ticker, strategies) {
  const results = [];

  for (const strategy of strategies) {
    const result = await apiClient.post('/backtest', {
      ticker,
      strategy,
      interval: '1d',
      cash: 10000
    });

    results.push({
      strategy: result.strategy,
      return: result.return_pct,
      sharpe: result.sharpe_ratio,
      trades: result.total_trades
    });
  }

  // Sort by return percentage
  results.sort((a, b) => b.return - a.return);

  return results;
}

// Usage
const comparison = await compareStrategies('AAPL', [
  'bollinger_bands_strategy',
  'tema_macd_strategy',
  'rsi_stochastic_strategy'
]);

// Display comparison table
<table>
  {comparison.map(r => (
    <tr key={r.strategy}>
      <td>{r.strategy}</td>
      <td>{r.return.toFixed(2)}%</td>
      <td>{r.sharpe?.toFixed(2) || 'N/A'}</td>
      <td>{r.trades}</td>
    </tr>
  ))}
</table>
```

### Use Case 3: Live Price Monitor

```javascript
function useLivePrice(ticker, updateInterval = 60000) {
  const [price, setPrice] = useState(null);
  const [change, setChange] = useState(0);

  useEffect(() => {
    async function fetchPrice() {
      const data = await apiClient.post('/market-data', {
        ticker,
        period: '1d',
        interval: '1m'
      });

      if (data.data.length > 0) {
        const latest = data.data[data.data.length - 1];
        const previous = data.data[data.data.length - 2];

        setPrice(latest.Close);
        setChange(((latest.Close - previous.Close) / previous.Close) * 100);
      }
    }

    fetchPrice();
    const interval = setInterval(fetchPrice, updateInterval);

    return () => clearInterval(interval);
  }, [ticker, updateInterval]);

  return { price, change };
}

// Usage
function PriceWidget({ ticker }) {
  const { price, change } = useLivePrice(ticker);

  return (
    <div className={change >= 0 ? 'positive' : 'negative'}>
      <h3>{ticker}</h3>
      <p>${price?.toFixed(2)}</p>
      <p>{change >= 0 ? '▲' : '▼'} {Math.abs(change).toFixed(2)}%</p>
    </div>
  );
}
```

---

## Best Practices

### 1. Request Optimization

**DO:**
- Cache strategy list (rarely changes)
- Debounce user inputs before API calls
- Show loading states for operations > 1s
- Use appropriate timeouts (60s for backtests)
- Batch similar requests when possible

**DON'T:**
- Make backtest requests on every keystroke
- Request market data more than once per minute
- Run multiple backtests simultaneously
- Ignore timeout errors

### 2. User Experience

**Loading States:**
```javascript
// Good: Informative loading state
<div className="loading">
  <Spinner />
  <p>Running backtest... This may take up to 15 seconds</p>
  <ProgressBar value={progress} />
</div>

// Bad: Generic loading
<Spinner />
```

**Error Messages:**
```javascript
// Good: Actionable error message
"The ticker 'XYZ' was not found. Please verify the symbol and try again."

// Bad: Technical error
"HTTP 500: Internal Server Error"
```

### 3. Data Validation

**Before Sending Requests:**
```javascript
function validateBacktestForm(data) {
  const errors = [];

  // Ticker validation
  if (!data.ticker || data.ticker.length === 0) {
    errors.push('Ticker is required');
  }
  if (data.ticker.length > 10) {
    errors.push('Invalid ticker format');
  }

  // Date validation
  if (data.start_date && data.end_date) {
    const start = new Date(data.start_date);
    const end = new Date(data.end_date);

    if (start >= end) {
      errors.push('Start date must be before end date');
    }

    if (start > new Date()) {
      errors.push('Start date cannot be in the future');
    }
  }

  // Cash validation
  if (data.cash <= 0) {
    errors.push('Cash must be positive');
  }
  if (data.cash > 1000000000) {
    errors.push('Cash amount too large');
  }

  return errors;
}
```

### 4. State Management

```javascript
// React example with proper state management
function BacktestPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [strategies, setStrategies] = useState([]);

  useEffect(() => {
    // Load strategies once on mount
    apiClient.get('/strategies')
      .then(data => setStrategies(data.strategies))
      .catch(err => console.error('Failed to load strategies:', err));
  }, []);

  async function handleSubmit(formData) {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const result = await apiClient.post('/backtest', formData);
      setResults(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <BacktestForm
        strategies={strategies}
        onSubmit={handleSubmit}
        loading={loading}
      />
      {error && <ErrorMessage message={error} />}
      {results && <ResultsDisplay results={results} />}
    </div>
  );
}
```

### 5. Mobile Considerations

- Use responsive design for result tables
- Show abbreviated metrics on small screens
- Implement pull-to-refresh for market data
- Add touch-friendly buttons and controls
- Consider offline mode with cached data

### 6. Security Considerations

**Current State:**
- No authentication (add if needed)
- CORS allows all origins (restrict in production)
- No rate limiting (consider adding)

**Recommendations:**
```javascript
// Add API key if implementing authentication
const apiClient = {
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.REACT_APP_API_KEY
  }
};

// Implement rate limiting on frontend
const rateLimiter = new Map();

function checkRateLimit(endpoint, limit = 10, window = 60000) {
  const key = endpoint;
  const now = Date.now();
  const requests = rateLimiter.get(key) || [];

  // Remove old requests outside window
  const recent = requests.filter(time => now - time < window);

  if (recent.length >= limit) {
    throw new Error('Rate limit exceeded. Please wait before trying again.');
  }

  recent.push(now);
  rateLimiter.set(key, recent);
}
```

---

## Testing Your Integration

Run the provided test script to verify API functionality:

```bash
# Start the API server first
cd src
python -m uvicorn api.main:app --reload

# In another terminal, run tests
python test_api.py

# Or specify custom URL
python test_api.py http://your-api-url:8000
```

The test script will:
1. Check all endpoints
2. Validate response formats
3. Test error handling
4. Measure response times
5. Generate a detailed report (`test_results.json`)

---

## Appendix: Complete Example Application

```javascript
// Complete React example
import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [strategies, setStrategies] = useState([]);
  const [formData, setFormData] = useState({
    ticker: 'AAPL',
    strategy: '',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    interval: '1d',
    cash: 10000
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/strategies`)
      .then(res => res.json())
      .then(data => {
        setStrategies(data.strategies);
        if (data.strategies.length > 0) {
          setFormData(prev => ({ ...prev, strategy: data.strategies[0].module }));
        }
      });
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>StrategyBuilder Backtester</h1>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Ticker (e.g., AAPL)"
          value={formData.ticker}
          onChange={e => setFormData({ ...formData, ticker: e.target.value })}
        />

        <select
          value={formData.strategy}
          onChange={e => setFormData({ ...formData, strategy: e.target.value })}
        >
          {strategies.map(s => (
            <option key={s.module} value={s.module}>
              {s.class_name || s.module}
            </option>
          ))}
        </select>

        <input
          type="date"
          value={formData.start_date}
          onChange={e => setFormData({ ...formData, start_date: e.target.value })}
        />

        <input
          type="date"
          value={formData.end_date}
          onChange={e => setFormData({ ...formData, end_date: e.target.value })}
        />

        <button type="submit" disabled={loading}>
          {loading ? 'Running...' : 'Run Backtest'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {results && (
        <div className="results">
          <h2>Results for {results.ticker}</h2>
          <div className="metric">
            <strong>Return:</strong> {results.return_pct.toFixed(2)}%
          </div>
          <div className="metric">
            <strong>Profit/Loss:</strong> ${results.pnl.toFixed(2)}
          </div>
          <div className="metric">
            <strong>Sharpe Ratio:</strong> {results.sharpe_ratio?.toFixed(2) || 'N/A'}
          </div>
          <div className="metric">
            <strong>Max Drawdown:</strong> {results.max_drawdown?.toFixed(2)}%
          </div>
          <div className="metric">
            <strong>Trades:</strong> {results.total_trades}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
```

---

## Support & Questions

If you encounter issues or have questions:

1. Check the interactive API docs at `/docs`
2. Run the test script to verify API functionality
3. Review this guide for proper request formats
4. Check error messages in API responses
5. Ensure the API server is running on the correct port

For development:
- API runs on port 8000 by default
- Enable auto-reload with `--reload` flag
- View logs in the terminal where uvicorn is running
- Use `/docs` for testing individual endpoints
