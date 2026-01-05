# StrategyBuilder

A clean, modular FastAPI backend for algorithmic trading strategy backtesting using Backtrader.

## Overview

StrategyBuilder provides a RESTful API for backtesting trading strategies on historical market data. Built with FastAPI and Backtrader, it offers a simple yet powerful platform for testing and analyzing trading algorithms with comprehensive chart data, technical indicators, and trade visualization support.

## Features

- **RESTful API** - FastAPI-powered backend with automatic documentation
- **Multiple Strategies** - 12+ pre-built trading strategies included
- **Market Data** - Real-time data fetching via Yahoo Finance
- **Performance Metrics** - Comprehensive analytics including Sharpe ratio, max drawdown, and more
- **Chart Data** - OHLC data, technical indicators, and trade markers for visualization
- **Trade Tracking** - Automatic position tracking with entry/exit markers
- **Modular Design** - Easy to add custom strategies and indicators
- **Auto Documentation** - Interactive API docs via Swagger UI

## Project Structure

```
StrategyBuilder/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── core/
│   │   ├── run_strategy.py      # Backtest execution engine
│   │   ├── strategy_skeleton.py # Base strategy class
│   │   └── data_manager.py      # Data handling utilities
│   ├── strategies/              # Trading strategy implementations
│   │   ├── bollinger_bands_strategy.py
│   │   ├── tema_macd_strategy.py
│   │   ├── rsi_stochastic_strategy.py
│   │   └── ... (9 more strategies)
│   ├── indicators/              # Custom technical indicators
│   │   ├── cmf_indicator.py
│   │   ├── mfi_indicator.py
│   │   └── obv_indicator.py
│   └── utils/
│       ├── performance_analyzer.py  # Advanced metrics calculation
│       └── api_logger.py            # API logging utilities
├── test_api.py                  # Comprehensive API testing script
├── API_SUMMARY.md               # Complete API documentation
├── requirements.txt
├── run_api.py                   # API server launcher
└── README.md
```

## Quick Start

### Installation

```bash
git clone <repository-url>
cd StrategyBuilder
pip install -r requirements.txt
```

### Running the API

```bash
python run_api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/strategies` | GET | List all available strategies |
| `/strategies/{name}` | GET | Get strategy details |
| `/backtest` | POST | Run a backtest |
| `/market-data` | POST | Fetch market data |
| `/parameters/default` | GET | Get default parameters |

For complete API documentation, see [API_SUMMARY.md](API_SUMMARY.md)

## Testing

Run comprehensive API tests:

```bash
python test_api.py
```

This will test 5 different configurations and save results to `test_results.json`.

## Available Strategies

The platform includes 12 pre-built strategies:

1. **Bollinger Bands** - Mean reversion strategy
2. **TEMA MACD** - Triple EMA with MACD signals
3. **TEMA Crossover** - Dual TEMA crossover
4. **ADX** - Trend strength-based strategy
5. **Alligator** - Bill Williams' Alligator indicator
6. **CMF ATR MACD** - Chaikin Money Flow with ATR and MACD
7. **RSI Stochastic** - RSI and Stochastic oscillator combination
8. **CCI ATR** - Commodity Channel Index with ATR
9. **MFI** - Money Flow Index strategy
10. **Keltner Channel** - Volatility-based channel strategy
11. **Momentum Multi** - Multi-indicator momentum strategy
12. **Williams %R** - Williams %R oscillator strategy

## Backtest Response Format

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

## Chart Data Features

### OHLC Data
Complete historical price data for visualization with open, high, low, close, and volume.

### Technical Indicators
Each strategy exposes its technical indicators for charting. Access indicators via `chart_data.indicators`.

### Trade Markers
Automatic trade tracking with entry and exit markers. Each marker includes:
- **date**: Timestamp of the trade
- **price**: Execution price
- **type**: BUY or SELL
- **action**: OPEN or CLOSE
- **pnl**: Profit/loss (on CLOSE markers)

## Adding Custom Strategies

Create a new strategy by extending `Strategy_skeleton`:

```python
from src.core.strategy_skeleton import Strategy_skeleton
import backtrader as bt

class MyStrategy(Strategy_skeleton):
    params = (
        ("period", 20),
        ("threshold", 0.02),
    )

    def __init__(self, args):
        super(MyStrategy, self).__init__(args)
        self.sma = bt.indicators.SMA(period=self.p.period)

    def get_technical_indicators(self):
        return {
            'SMA': self.sma
        }

    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.close()
```

The strategy will be automatically discovered and available via the API.

## Configuration

### Default Parameters

```python
{
    "cash": 10000,
    "commission": 0.001,
    "position_size_pct": 95.0,
    "macd1": 12,
    "macd2": 26,
    "macdsig": 9,
    "atrperiod": 14,
    "atrdist": 2.0
}
```

### CORS Settings

CORS is configured in `src/config.py` for production use.

## Performance Metrics

Each backtest returns comprehensive metrics:

### Basic Metrics
- **ROI** - Return on Investment percentage
- **Sharpe Ratio** - Risk-adjusted return
- **Max Drawdown** - Maximum peak-to-trough decline
- **Total Trades** - Number of trades executed

### Advanced Metrics
- **Win Rate** - Percentage of profitable trades
- **Profit Factor** - Gross profit / Gross loss
- **Payoff Ratio** - Average win / Average loss
- **Calmar Ratio** - Annual return / Max drawdown
- **Sortino Ratio** - Downside risk-adjusted return
- **Expectancy** - Expected value per trade

## Frontend Integration

### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'BTC-USD',
    strategy: 'williams_r_strategy',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    interval: '1d',
    cash: 10000,
    parameters: {
      period: 14,
      lower_bound: -80,
      upper_bound: -20
    }
  })
});

const result = await response.json();
console.log(`ROI: ${result.return_pct}%`);
console.log(`Trades: ${result.chart_data.trade_markers.length / 2}`);
```

### Python Example

```python
import requests

response = requests.post('http://localhost:8000/backtest', json={
    'ticker': 'BTC-USD',
    'strategy': 'williams_r_strategy',
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'interval': '1d',
    'cash': 10000,
    'parameters': {
        'period': 14,
        'lower_bound': -80,
        'upper_bound': -20
    }
})

result = response.json()
print(f"ROI: {result['return_pct']}%")
print(f"Chart data points: {len(result['chart_data']['ohlc'])}")
print(f"Trade markers: {len(result['chart_data']['trade_markers'])}")
```

## Disclaimer

This software is for educational and research purposes only. Do not use for live trading without thorough testing and understanding of the risks involved. Past performance does not guarantee future results.
