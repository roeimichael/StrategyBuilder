# API Summary

Base URL: `http://localhost:8000`

## Endpoints

### 1. Root
**GET** `/`

**Description**: API information and available endpoints

**Response**:
```json
{
  "name": "StrategyBuilder API",
  "version": "1.0.0",
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

### 2. Health Check
**GET** `/health`

**Description**: API health status

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-05T12:00:00.000000"
}
```

### 3. List Strategies
**GET** `/strategies`

**Description**: Get all available trading strategies

**Response**:
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

### 4. Get Strategy Info
**GET** `/strategies/{strategy_name}`

**Description**: Get detailed information about a specific strategy

**Parameters**:
- `strategy_name` (path): Strategy module name

**Response**:
```json
{
  "success": true,
  "strategy": {
    "module": "bollinger_bands_strategy",
    "class_name": "Bollinger_three",
    "description": "",
    "parameters": {
      "period": 20,
      "devfactor": 2.0
    }
  }
}
```

### 5. Get Default Parameters
**GET** `/parameters/default`

**Description**: Get default backtest parameters

**Response**:
```json
{
  "success": true,
  "parameters": {
    "cash": 10000.0,
    "commission": 0.001,
    "position_size_pct": 95.0
  }
}
```

### 6. Run Backtest
**POST** `/backtest`

**Description**: Execute a strategy backtest

**Request Body**:
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
    "lower_bound": -80,
    "upper_bound": -20
  },
  "include_chart_data": false,
  "columnar_format": true
}
```

**Request Parameters**:
- `ticker` (string, required): Stock/crypto ticker symbol (e.g., "AAPL", "BTC-USD")
- `strategy` (string, required): Strategy module name
- `start_date` (string, optional): Backtest start date in "YYYY-MM-DD" format
- `end_date` (string, optional): Backtest end date in "YYYY-MM-DD" format
- `interval` (string, optional): Data interval (default: "1h")
- `cash` (float, optional): Initial capital (default: 10000.0)
- `parameters` (object, optional): Strategy-specific parameters
- `include_chart_data` (boolean, optional): Include chart data in response (default: false)
- `columnar_format` (boolean, optional): Use columnar format for chart data (default: true)

**⚠️ Performance Note**:
- Without chart data: Response ~1KB
- With chart data (row format): Response ~1-2MB (10,000+ lines)
- With chart data (columnar format): Response ~500KB-1MB
- **Recommendation**: Set `include_chart_data: false` for performance testing and only request chart data when needed for visualization

**Response (without chart data)**:
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
  "total_trades": 15,
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "advanced_metrics": {
    "win_rate": 60.0,
    "profit_factor": 1.8,
    "payoff_ratio": 1.5,
    "calmar_ratio": 1.76,
    "sortino_ratio": 1.45,
    "max_consecutive_wins": 5,
    "max_consecutive_losses": 3,
    "avg_win": 150.0,
    "avg_loss": 100.0,
    "largest_win": 300.0,
    "largest_loss": 250.0,
    "avg_trade_duration": null,
    "recovery_periods": [],
    "expectancy": 50.0
  },
  "chart_data": null
}
```

## Chart Data Formats

### Row Format (columnar_format: false)
**Use case**: When you need to iterate through data points sequentially

```json
"chart_data": [
  {
    "date": "2024-01-01T00:00:00",
    "open": 42000.0,
    "high": 43000.0,
    "low": 41500.0,
    "close": 42500.0,
    "volume": 1000000.0,
    "indicators": {
      "Williams_R": -50.0,
      "SMA_20": 42100.0
    },
    "trade_markers": []
  },
  {
    "date": "2024-01-02T00:00:00",
    "open": 42500.0,
    "high": 43200.0,
    "low": 42300.0,
    "close": 43000.0,
    "volume": 1200000.0,
    "indicators": {
      "Williams_R": -45.0,
      "SMA_20": 42150.0
    },
    "trade_markers": [
      {
        "type": "BUY",
        "action": "OPEN",
        "price": 42500.0,
        "pnl": null
      }
    ]
  }
]
```

### Columnar Format (columnar_format: true) - **Recommended**
**Use case**: For charting libraries (Chart.js, Plotly, TradingView) and better compression

```json
"chart_data": {
  "date": ["2024-01-01T00:00:00", "2024-01-02T00:00:00", "2024-01-03T00:00:00"],
  "open": [42000.0, 42500.0, 43000.0],
  "high": [43000.0, 43200.0, 43500.0],
  "low": [41500.0, 42300.0, 42800.0],
  "close": [42500.0, 43000.0, 43200.0],
  "volume": [1000000.0, 1200000.0, 1100000.0],
  "indicators": {
    "Williams_R": [-50.0, -45.0, -30.0],
    "SMA_20": [42100.0, 42150.0, 42200.0]
  },
  "trade_markers": [
    [],
    [{"type": "BUY", "action": "OPEN", "price": 42500.0, "pnl": null}],
    [{"type": "SELL", "action": "CLOSE", "price": 43200.0, "pnl": 68.0}]
  ]
}
```

### 7. Get Market Data
**POST** `/market-data`

**Description**: Fetch historical market data for a ticker

**Request Body**:
```json
{
  "ticker": "BTC-USD",
  "period": "1mo",
  "interval": "1d"
}
```

**Response**:
```json
{
  "success": true,
  "ticker": "BTC-USD",
  "period": "1mo",
  "interval": "1d",
  "data_points": 30,
  "data": [
    {
      "Date": "2024-01-01T00:00:00",
      "Open": 42000.0,
      "High": 43000.0,
      "Low": 41500.0,
      "Close": 42500.0,
      "Volume": 1000000.0
    }
  ],
  "statistics": {
    "mean": 42500.0,
    "std": 1200.5,
    "min": 40000.0,
    "max": 45000.0,
    "volume_avg": 950000.0
  }
}
```

## Indicator Naming Conventions

All indicators in the `chart_data.indicators` object follow these naming patterns:

### Single-Line Indicators
Simple indicators return a single value and are named by their acronym or full name:

- `RSI` - Relative Strength Index
- `Williams_R` - Williams %R
- `MFI` - Money Flow Index
- `CCI` - Commodity Channel Index
- `ADX` - Average Directional Index
- `CMF` - Chaikin Money Flow

### Multi-Line Indicators
Indicators with multiple lines use suffix patterns:

**Moving Averages:**
- `SMA_<period>` - Simple Moving Average (e.g., `SMA_20`, `SMA_50`)
- `EMA_<period>` - Exponential Moving Average (e.g., `EMA_12`, `EMA_26`)
- `TEMA_<period>` - Triple Exponential Moving Average (e.g., `TEMA_10`)

**Bollinger Bands:**
- `Bollinger_Upper` - Upper band
- `Bollinger_Middle` - Middle band (SMA)
- `Bollinger_Lower` - Lower band

**MACD:**
- `MACD` - MACD line
- `MACD_Signal` - Signal line
- `MACD_Histogram` - Histogram

**Stochastic:**
- `Stochastic_K` - %K line (fast)
- `Stochastic_D` - %D line (slow)

**Keltner Channels:**
- `Keltner_Upper` - Upper channel
- `Keltner_Middle` - Middle line (EMA)
- `Keltner_Lower` - Lower channel

**Alligator:**
- `Alligator_Jaw` - Jaw line (blue, slowest)
- `Alligator_Teeth` - Teeth line (red, medium)
- `Alligator_Lips` - Lips line (green, fastest)

### ATR (Average True Range)
- `ATR` - Average True Range value

## Strategy Parameter Naming Conventions

Parameters passed in the `parameters` object follow strategy-specific naming:

### Common Parameters (All Strategies)
- `cash` - Initial capital (default: 10000.0)
- `commission` - Commission per trade (default: 0.001)
- `position_size_pct` - Position size as percentage (default: 95.0)

### Strategy-Specific Parameters

**RSI-based strategies:**
- `period` - RSI period (default: 14)
- `lower_bound` - Oversold threshold (default: 30)
- `upper_bound` - Overbought threshold (default: 70)

**MACD-based strategies:**
- `macd1` - Fast period (default: 12)
- `macd2` - Slow period (default: 26)
- `macdsig` - Signal period (default: 9)

**Bollinger Bands strategies:**
- `period` - Period for middle band SMA (default: 20)
- `devfactor` - Standard deviation multiplier (default: 2.0)

**Williams %R strategies:**
- `period` - Lookback period (default: 14)
- `lower_bound` - Oversold level (default: -80)
- `upper_bound` - Overbought level (default: -20)

**ATR-based strategies:**
- `atrperiod` - ATR calculation period (default: 14)
- `atrdist` - ATR distance multiplier (default: 2.0)

**Stochastic strategies:**
- `period` - %K period (default: 14)
- `period_dfast` - %K smoothing (default: 3)
- `period_dslow` - %D period (default: 3)
- `lower_bound` - Oversold threshold (default: 20)
- `upper_bound` - Overbought threshold (default: 80)

**ADX strategies:**
- `period` - ADX period (default: 14)
- `threshold` - Trend strength threshold (default: 25)

**MFI strategies:**
- `period` - MFI period (default: 14)
- `lower_bound` - Oversold threshold (default: 20)
- `upper_bound` - Overbought threshold (default: 80)

**TEMA strategies:**
- `tema_period` - TEMA period (default: 10)
- `signal_period` - Signal line period (default: 5)

**Alligator strategies:**
- `jaw_period` - Jaw period (default: 13)
- `teeth_period` - Teeth period (default: 8)
- `lips_period` - Lips period (default: 5)

**CCI strategies:**
- `period` - CCI period (default: 20)
- `threshold` - Trend strength threshold (default: 100)

**Keltner Channel strategies:**
- `ema_period` - EMA period (default: 20)
- `atr_period` - ATR period (default: 10)
- `atr_multiplier` - ATR multiplier (default: 2.0)

## Frontend Integration Guide

### Using Columnar Format with Chart.js

```javascript
const response = await fetch('/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'BTC-USD',
    strategy: 'williams_r_strategy',
    interval: '1d',
    include_chart_data: true,
    columnar_format: true
  })
});

const data = await response.json();
const chartData = data.chart_data;

// Create OHLC chart
const ohlcChart = {
  labels: chartData.date,
  datasets: [{
    label: 'Close Price',
    data: chartData.close,
    borderColor: 'rgb(75, 192, 192)',
    tension: 0.1
  }]
};

// Add indicators
Object.entries(chartData.indicators).forEach(([name, values]) => {
  ohlcChart.datasets.push({
    label: name,
    data: values,
    borderColor: getColorForIndicator(name),
    tension: 0.1
  });
});
```

### Using Row Format for Data Tables

```javascript
const response = await fetch('/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'AAPL',
    strategy: 'rsi_stochastic_strategy',
    interval: '1h',
    include_chart_data: true,
    columnar_format: false
  })
});

const data = await response.json();

// Display in table
data.chart_data.forEach(point => {
  console.log(`${point.date}: Close=${point.close}, RSI=${point.indicators.RSI}`);
});
```

### Detecting Format Type

```javascript
function isColumnarFormat(chartData) {
  return chartData && !Array.isArray(chartData);
}

function normalizeChartData(chartData) {
  if (isColumnarFormat(chartData)) {
    // Convert columnar to row format if needed
    const length = chartData.date.length;
    const rows = [];
    for (let i = 0; i < length; i++) {
      const row = {
        date: chartData.date[i],
        open: chartData.open[i],
        high: chartData.high[i],
        low: chartData.low[i],
        close: chartData.close[i],
        volume: chartData.volume[i],
        indicators: {},
        trade_markers: chartData.trade_markers[i]
      };
      Object.entries(chartData.indicators).forEach(([key, values]) => {
        row.indicators[key] = values[i];
      });
      rows.push(row);
    }
    return rows;
  }
  return chartData;
}
```

## Available Strategies

1. `adx_strategy` - ADX Strategy
2. `alligator_strategy` - Alligator Strategy
3. `bollinger_bands_strategy` - Bollinger Bands Strategy
4. `cci_atr_strategy` - CCI ATR Strategy
5. `cmf_atr_macd_strategy` - MACD CMF ATR Strategy
6. `keltner_channel_strategy` - Keltner Channel Strategy
7. `mfi_strategy` - MFI Strategy
8. `momentum_multi_strategy` - Momentum Multi Strategy
9. `rsi_stochastic_strategy` - RSI Stochastic Strategy
10. `tema_crossover_strategy` - TEMA Crossover Strategy
11. `tema_macd_strategy` - TEMA MACD Strategy
12. `williams_r_strategy` - Williams R Strategy

## Interval Options

- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `1d` - 1 day
- `1wk` - 1 week
- `1mo` - 1 month

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (strategy or ticker not found)
- `500` - Internal Server Error
