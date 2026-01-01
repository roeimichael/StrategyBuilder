# StrategyBuilder

A clean, modular FastAPI backend for algorithmic trading strategy backtesting using Backtrader.

## Overview

StrategyBuilder provides a RESTful API for backtesting trading strategies on historical market data. Built with FastAPI and Backtrader, it offers a simple yet powerful platform for testing and analyzing trading algorithms.

## Features

-  **RESTful API** - FastAPI-powered backend with automatic documentation
-  **Multiple Strategies** - 12+ pre-built trading strategies included
-  **Market Data** - Real-time data fetching via Yahoo Finance
-  **Performance Metrics** - Comprehensive analytics including Sharpe ratio, max drawdown, and more
-  **Modular Design** - Easy to add custom strategies and indicators
-  **Auto Documentation** - Interactive API docs via Swagger UI

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
│       └── performance_analyzer.py  # Advanced metrics calculation
├── requirements.txt
└── README.md
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd StrategyBuilder

# Install dependencies
pip install -r requirements.txt
```

### Running the API

```bash
# Start the FastAPI server
cd src
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
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

## Usage Examples

### List Available Strategies

```bash
curl http://localhost:8000/strategies
```

### Run a Backtest

```bash
curl -X POST "http://localhost:8000/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "strategy": "bollinger_bands_strategy",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "interval": "1h",
    "cash": 10000
  }'
```

### Get Market Data

```bash
curl -X POST "http://localhost:8000/market-data" \
  -H "Content-Type": application/json" \
  -d '{
    "ticker": "TSLA",
    "period": "1mo",
    "interval": "1d"
  }'
```

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
  "ticker": "AAPL",
  "strategy": "bollinger_bands_strategy",
  "start_value": 10000.0,
  "end_value": 11250.0,
  "pnl": 1250.0,
  "return_pct": 12.5,
  "sharpe_ratio": 1.45,
  "max_drawdown": -5.2,
  "total_trades": 15,
  "interval": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "advanced_metrics": {
    "win_rate": 60.0,
    "profit_factor": 1.8,
    ...
  }
}
```

## Adding Custom Strategies

Create a new strategy by extending `Strategy_skeleton`:

```python
# src/strategies/my_strategy.py

from core.strategy_skeleton import Strategy_skeleton
import backtrader as bt

class MyStrategy(Strategy_skeleton):
    """My custom trading strategy"""

    params = (
        ("period", 20),
        ("threshold", 0.02),
    )

    def __init__(self, args):
        super(MyStrategy, self).__init__(args)
        self.sma = bt.indicators.SMA(period=self.p.period)

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
    "macd1": 12,
    "macd2": 26,
    "macdsig": 9,
    "atrperiod": 14,
    "atrdist": 2.0,
    "order_pct": 1.0
}
```

### CORS Settings

For production, update CORS in `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    ...
)
```

## Performance Metrics

Each backtest returns:
- **ROI** - Return on Investment percentage
- **Sharpe Ratio** - Risk-adjusted return
- **Max Drawdown** - Maximum peak-to-trough decline
- **Total Trades** - Number of trades executed
- **Win Rate** - Percentage of profitable trades
- **Profit Factor** - Gross profit / Gross loss
- **Average Trade P&L** - Mean profit/loss per trade

## Frontend Integration

### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'AAPL',
    strategy: 'bollinger_bands_strategy',
    interval: '1h',
    cash: 10000
  })
});

const result = await response.json();
console.log(`ROI: ${result.return_pct}%`);
```

### Python Example

```python
import requests

response = requests.post('http://localhost:8000/backtest', json={
    'ticker': 'AAPL',
    'strategy': 'bollinger_bands_strategy',
    'interval': '1h',
    'cash': 10000
})

result = response.json()
print(f"ROI: {result['return_pct']}%")
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Disclaimer

This software is for educational and research purposes only. Do not use for live trading without thorough testing and understanding of the risks involved. Past performance does not guarantee future results.
