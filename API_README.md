# StrategyBuilder API

FastAPI-based backend for the StrategyBuilder algorithmic trading backtesting platform.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the API

```bash
# Development mode with auto-reload
python api.py

# Or using uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & Info

- `GET /` - API information and available endpoints
- `GET /health` - Health check

### Strategies

- `GET /strategies` - List all available trading strategies
- `GET /strategies/{strategy_name}` - Get detailed info about a specific strategy

### Backtesting

- `POST /backtest` - Run a backtest for a single asset
- `POST /backtest/pair` - Run a pair trading backtest

### Market Data

- `POST /data/market` - Fetch historical market data
- `GET /data/ticker/{ticker}/info` - Get ticker information

### Parameters

- `GET /parameters/default` - Get default strategy parameters

## Example Usage

### Run a Backtest

```bash
curl -X POST "http://localhost:8000/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "strategy_name": "Bollinger_three",
    "interval": "1h",
    "parameters": {
      "cash": 10000,
      "order_pct": 1.0
    }
  }'
```

### List Available Strategies

```bash
curl http://localhost:8000/strategies
```

### Get Market Data

```bash
curl -X POST "http://localhost:8000/data/market" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "period": "1mo",
    "interval": "1d"
  }'
```

## Available Strategies

The API automatically discovers strategies from:
- Root directory Python files
- `strategies/` directory

Current strategies include:
- Bollinger_three
- TEMA_MACD_NEW
- Alligator_strategy
- ADX_strategy
- CMF_ATR_MACD_strategy
- pair_trading_strategy
- And more...

## Request/Response Examples

### Backtest Request

```json
{
  "ticker": "TSLA",
  "strategy_name": "TEMA_MACD_NEW",
  "start_date": "2023-01-01",
  "interval": "1h",
  "parameters": {
    "cash": 10000,
    "macd1": 12,
    "macd2": 26,
    "macdsig": 9
  }
}
```

### Backtest Response

```json
{
  "success": true,
  "ticker": "TSLA",
  "strategy": "TEMA_MACD_NEW",
  "start_value": 10000.0,
  "end_value": 10500.0,
  "roi_percent": 5.0,
  "total_return_percent": 5.0,
  "sharpe_ratio": 1.23,
  "max_drawdown": -2.5,
  "trades": 15,
  "output": "..."
}
```

## Configuration

### CORS

The API is configured to allow all origins by default. For production, update the CORS settings in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development

### Project Structure

```
StrategyBuilder/
├── api.py                    # FastAPI application
├── run_strategy.py          # Single asset backtest runner
├── run_strategy_2.py        # Pair trading backtest runner
├── strategy_skeleton.py     # Base strategy class
├── parameters.py            # Default parameters
├── strategies/              # Strategy implementations
│   ├── ADX_strategy.py
│   ├── CMF_ATR_MACD_strategy.py
│   ├── TEMA_MACD_strategy.py
│   └── ...
└── requirements.txt         # Python dependencies
```

### Adding New Strategies

1. Create a new strategy class that inherits from `Strategy_skeleton` or `bt.Strategy`
2. Place it in the `strategies/` directory or root directory
3. The API will automatically discover and expose it

## Frontend Integration

Connect your frontend by making HTTP requests to the API endpoints. Example using JavaScript:

```javascript
// Run a backtest
const response = await fetch('http://localhost:8000/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'AAPL',
    strategy_name: 'Bollinger_three',
    interval: '1h'
  })
});

const result = await response.json();
console.log(result);
```

## Notes

- The API runs on port 8000 by default
- All timestamps are in ISO format
- Market data is fetched from Yahoo Finance via yfinance
- Backtest results include portfolio value, ROI, Sharpe ratio, and max drawdown
