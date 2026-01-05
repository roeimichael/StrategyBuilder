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
  }
}
```

**Response**:
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
  "chart_data": {
    "ohlc": [
      {
        "date": "2024-01-01T00:00:00",
        "open": 42000.0,
        "high": 43000.0,
        "low": 41500.0,
        "close": 42500.0,
        "volume": 1000000.0
      }
    ],
    "indicators": {
      "Williams_R": [-50.0, -45.0, -60.0]
    },
    "trade_markers": [
      {
        "date": "2024-03-15T14:30:00",
        "price": 445.5,
        "type": "BUY",
        "action": "OPEN"
      },
      {
        "date": "2024-03-20T10:15:00",
        "price": 452.3,
        "type": "SELL",
        "action": "CLOSE",
        "pnl": 68.0
      }
    ]
  }
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
