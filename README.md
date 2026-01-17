# StrategyBuilder

Clean, modular FastAPI backend for algorithmic trading strategy backtesting using Backtrader framework.

## Overview

StrategyBuilder provides RESTful API for backtesting trading strategies on historical market data with comprehensive performance analytics, optimization capabilities, and real-time monitoring features.

## Features

- **REST API**: FastAPI backend with automatic OpenAPI documentation
- **12+ Trading Strategies**: Pre-built strategies with both long and short position support
- **Strategy Optimization**: Grid search parameter optimization across multiple combinations
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, Calmar ratio, Sortino ratio, drawdown analysis
- **Preset Management**: Save, retrieve, and execute strategy configurations
- **Run History**: Persistent backtest storage with replay capabilities
- **Live Snapshots**: Near-real-time strategy state without full backtest execution
- **Watchlist Monitoring**: Automated strategy execution scheduling for surveillance
- **Chart Data Export**: Unified timeline format with OHLC, indicators, and trade markers
- **Custom Indicators**: OBV, MFI, CMF technical indicators
- **Modular Architecture**: Clean separation of API, services, core engine, and data layers

## Project Structure

```
StrategyBuilder/
├── src/
│   ├── api/                      # FastAPI application layer
│   │   ├── main.py              # REST endpoints and middleware
│   │   └── models/              # Request/response schemas
│   ├── core/                    # Backtesting engine
│   │   ├── run_strategy.py      # Strategy execution orchestration
│   │   ├── optimizer.py         # Parameter optimization engine
│   │   ├── data_manager.py      # Market data fetching and processing
│   │   ├── strategy_skeleton.py # Base strategy class
│   │   └── extractors/          # Chart data extraction utilities
│   ├── services/                # Business logic layer
│   │   ├── strategy_service.py  # Strategy loading and metadata
│   │   └── backtest_service.py  # Backtest orchestration and snapshot generation
│   ├── data/                    # Data persistence layer
│   │   ├── run_repository.py    # Strategy execution history
│   │   ├── preset_repository.py # Configuration templates
│   │   └── watchlist_repository.py # Automated monitoring entries
│   ├── strategies/              # Trading strategy implementations (12 strategies)
│   ├── indicators/              # Custom technical indicators (OBV, MFI, CMF)
│   ├── config/                  # Configuration management
│   ├── utils/                   # Logging and performance analysis utilities
│   └── exceptions/              # Exception hierarchy
├── tests/                       # Comprehensive test suite
│   ├── test_backtest.py         # API endpoint integration tests
│   ├── test_optimization.py     # Parameter optimization tests
│   ├── test_presets.py          # Preset CRUD tests
│   ├── test_snapshot.py         # Live snapshot tests
│   ├── test_strategies.py       # Strategy loading and execution tests
│   ├── test_indicators.py       # Indicator accuracy validation
│   ├── test_imports.py          # Module import verification
│   ├── test_everything.py       # Master test runner
│   └── strategies/              # Strategy correctness tests with controlled data
├── docs/                        # Structural documentation
│   ├── API_doc.md              # API layer architecture
│   ├── Core_doc.md             # Backtesting engine architecture
│   ├── config_doc.md           # Configuration system
│   ├── data_doc.md             # Data persistence layer
│   ├── utils_doc.md            # Utilities and logging
│   └── tests_doc.md            # Test suite structure
├── requirements.txt
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
python -m src.api.main
```

API available at:
- **API**: http://localhost:8086
- **Interactive Docs**: http://localhost:8086/docs
- **ReDoc**: http://localhost:8086/redoc

## API Endpoints

### Core Backtesting

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/strategies` | GET | List all available strategies |
| `/strategies/{name}` | GET | Get strategy details with optimizable parameters |
| `/backtest` | POST | Execute strategy backtest |
| `/optimize` | POST | Grid search parameter optimization |

### Run Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/runs` | GET | List saved backtest runs with pagination |
| `/runs/{id}` | GET | Retrieve specific run details |
| `/runs/{id}/replay` | POST | Re-execute saved run with optional overrides |
| `/runs/{id}` | DELETE | Delete saved run |

### Preset Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/presets` | GET | List strategy presets with filtering |
| `/presets` | POST | Create new preset configuration |
| `/presets/{id}` | GET | Retrieve preset details |
| `/presets/{id}` | DELETE | Delete preset |
| `/presets/{id}/backtest` | POST | Execute backtest from preset |

### Live Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/snapshot` | POST | Get near-real-time strategy state |

### Watchlist Monitoring

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/watchlist` | GET | List monitoring entries |
| `/watchlist` | POST | Create monitoring entry |
| `/watchlist/{id}` | GET | Retrieve entry details |
| `/watchlist/{id}` | PATCH | Update entry settings |
| `/watchlist/{id}` | DELETE | Delete entry |

## Available Strategies

12 pre-built strategies with parameter optimization support:

1. **Bollinger Bands** - Mean reversion with upper/lower band crossovers (supports shorts)
2. **Williams %R** - Oscillator-based oversold/overbought strategy (supports shorts)
3. **TEMA MACD** - Triple EMA with MACD confirmation signals
4. **TEMA Crossover** - Dual TEMA period crossover system
5. **ADX** - Trend strength and directional movement strategy
6. **Alligator** - Bill Williams' multi-EMA alignment system
7. **CMF ATR MACD** - Chaikin Money Flow with volatility and momentum filters
8. **RSI Stochastic** - Dual oscillator mean reversion strategy
9. **CCI ATR** - Commodity Channel Index with ATR-based exits
10. **MFI** - Money Flow Index volume-weighted oscillator
11. **Keltner Channel** - Volatility-based channel breakout strategy
12. **Momentum Multi** - Multi-indicator momentum confirmation system

All strategies support configurable parameters. Subset supports short positions (noted in strategy metadata).

## Example Usage

### Basic Backtest

```python
import requests

response = requests.post('http://localhost:8086/backtest', json={
    'ticker': 'AAPL',
    'strategy': 'bollinger_bands_strategy',
    'start_date': '2024-01-01',
    'end_date': '2024-06-30',
    'interval': '1d',
    'cash': 10000.0,
    'parameters': {
        'period': 20,
        'devfactor': 2.0
    },
    'include_chart_data': True
})

result = response.json()
print(f"PnL: ${result['pnl']:.2f}")
print(f"Return: {result['return_pct']:.2f}%")
print(f"Sharpe: {result['sharpe_ratio']}")
print(f"Total Trades: {result['total_trades']}")
```

### Parameter Optimization

```python
response = requests.post('http://localhost:8086/optimize', json={
    'ticker': 'BTC-USD',
    'strategy': 'bollinger_bands_strategy',
    'start_date': '2024-01-01',
    'end_date': '2024-06-30',
    'interval': '1d',
    'cash': 10000.0,
    'optimization_params': {
        'period': [15, 20, 25],
        'devfactor': [1.5, 2.0, 2.5]
    }
})

result = response.json()
print(f"Total Combinations Tested: {result['total_combinations']}")
for i, res in enumerate(result['top_results'][:3], 1):
    print(f"{i}. Params: {res['parameters']}, Return: {res['return_pct']:.2f}%")
```

### Save and Replay Run

```python
# Create preset
preset_response = requests.post('http://localhost:8086/presets', json={
    'name': 'BTC Bollinger 1D',
    'ticker': 'BTC-USD',
    'strategy': 'bollinger_bands_strategy',
    'parameters': {'period': 20, 'devfactor': 2.0},
    'interval': '1d',
    'notes': 'Optimized for volatile markets'
})

preset_id = preset_response.json()['id']

# Execute from preset
backtest_response = requests.post(
    f'http://localhost:8086/presets/{preset_id}/backtest',
    params={'start_date': '2024-01-01', 'end_date': '2024-06-30', 'cash': 10000}
)

print(f"Executed preset with PnL: ${backtest_response.json()['pnl']:.2f}")
```

### Live Snapshot

```python
response = requests.post('http://localhost:8086/snapshot', json={
    'ticker': 'AAPL',
    'strategy': 'rsi_stochastic_strategy',
    'interval': '1d',
    'lookback_bars': 200,
    'parameters': {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70
    }
})

snapshot = response.json()
print(f"Last Close: ${snapshot['last_bar']['close']:.2f}")
print(f"RSI: {snapshot['indicators'].get('RSI', 'N/A')}")
print(f"In Position: {snapshot['position_state']['in_position']}")
```

## Response Format

### Backtest Response

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
  "max_drawdown": 6.2,
  "total_trades": 12,
  "winning_trades": 8,
  "losing_trades": 4,
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-06-30",
  "advanced_metrics": {
    "win_rate": 66.67,
    "profit_factor": 2.1,
    "payoff_ratio": 1.6,
    "calmar_ratio": 2.02,
    "sortino_ratio": 1.75,
    "max_consecutive_wins": 4,
    "max_consecutive_losses": 2,
    "avg_win": 200.0,
    "avg_loss": 125.0,
    "largest_win": 350.0,
    "largest_loss": 200.0,
    "expectancy": 104.17
  },
  "chart_data": [...]
}
```

Chart data provides unified timeline with OHLC, indicators, and trade markers aligned by timestamp for easy frontend visualization.

## Testing

Execute test suite:

```bash
# Run all tests
python tests/test_everything.py

# Individual test suites
python tests/test_backtest.py
python tests/test_optimization.py
python tests/test_presets.py
python tests/test_snapshot.py
python tests/test_strategies.py
python tests/test_indicators.py
python tests/test_imports.py

# Strategy correctness tests
python tests/strategies/test_bollinger_bands_strategy.py
python tests/strategies/test_williams_r_strategy.py
```

## Documentation

Comprehensive structural documentation available in `docs/` directory:

- **API_doc.md**: FastAPI endpoint layer, request/response models, middleware
- **Core_doc.md**: Backtesting engine, strategy execution, optimization, chart extraction
- **data_doc.md**: SQLite repositories, database schemas, CRUD operations
- **config_doc.md**: Configuration management, constants, default parameters
- **utils_doc.md**: Logging infrastructure, performance metrics calculator
- **tests_doc.md**: Test suite organization, execution methodology, coverage

Each document provides structural overview focusing on architecture, components, and integration points without implementation details.

## Adding Custom Strategies

Create new strategy by extending `Strategy_skeleton`:

```python
from src.core.strategy_skeleton import Strategy_skeleton
import backtrader as bt

class MyStrategy(Strategy_skeleton):
    params = (
        ('period', 20),
        ('threshold', 0.02),
    )

    def __init__(self, args):
        super(MyStrategy, self).__init__(args)
        self.sma = bt.indicators.SMA(period=self.p.period)

    def get_technical_indicators(self):
        return {'SMA': self.sma}

    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0] * (1 + self.p.threshold):
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.close()
```

Strategy automatically discovered on API restart. Add optimizable parameters in `src/core/strategy_optimization_config.py` for grid search support.

## Performance Metrics

### Basic Metrics
- **PnL**: Absolute profit/loss in cash
- **Return %**: Percentage return on initial capital
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Max Drawdown**: Maximum peak-to-trough decline percentage
- **Total Trades**: Number of completed round-trip trades

### Advanced Metrics
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit divided by gross loss
- **Payoff Ratio**: Average win divided by average loss
- **Calmar Ratio**: Annualized return divided by max drawdown
- **Sortino Ratio**: Return divided by downside deviation (penalizes only negative volatility)
- **Expectancy**: Expected value per trade (statistical edge)
- **Max Consecutive Wins/Losses**: Longest winning/losing streaks
- **Average Win/Loss**: Mean profit/loss per winning/losing trade
- **Largest Win/Loss**: Single trade extremes

All metrics calculated via `PerformanceAnalyzer` utility class with equity curve analysis.

## Architecture

**Layered Architecture:**

1. **API Layer** (`src/api`): FastAPI endpoints, request validation, response formatting
2. **Service Layer** (`src/services`): Business logic, orchestration, strategy metadata
3. **Core Layer** (`src/core`): Backtrader integration, execution engine, optimization, data extraction
4. **Data Layer** (`src/data`): SQLite persistence, repository pattern, CRUD operations
5. **Support Layers**:
   - Config: Centralized configuration and constants
   - Utils: Logging, performance analysis
   - Exceptions: Custom exception hierarchy
   - Indicators: Custom Backtrader indicators
   - Strategies: Trading algorithm implementations

**Data Flow:**
API Request → Service Orchestration → Core Execution → Data Persistence → API Response

**Testing Strategy:**
- Unit tests: Import validation, indicator accuracy
- Integration tests: API endpoints, database operations
- Behavioral tests: Strategy correctness with controlled price data
- End-to-end tests: Full workflow validation

## Database Schema

SQLite database (`data/strategy_runs.db`) with three tables:

- **strategy_runs**: Backtest execution history with performance metrics
- **strategy_presets**: Reusable strategy configurations
- **watchlist_entries**: Automated monitoring schedule with foreign keys to presets/runs

Foreign key constraints enforce referential integrity. All timestamps stored in ISO 8601 format.

## Configuration

Default settings in `src/config/backtest_config.py`:

```python
DEFAULT_CASH = 10000.0
DEFAULT_COMMISSION = 0.001
DEFAULT_POSITION_SIZE_PCT = 95.0
DEFAULT_INTERVAL = "1d"
DEFAULT_BACKTEST_PERIOD_YEARS = 1
```

API configuration in `src/config/api_config.py`:

```python
API_HOST = "0.0.0.0"
API_PORT = 8086
CORS_ALLOW_ORIGINS = ["*"]  # Restrict in production
```

## Dependencies

### Core
- fastapi - REST API framework
- uvicorn - ASGI server
- backtrader - Backtesting engine
- yfinance - Market data provider
- pandas - Data manipulation
- numpy - Numerical operations

### Additional
- pydantic - Data validation
- python-dateutil - Date parsing
- requests - HTTP client (tests)

See `requirements.txt` for complete list with versions.

## Logging

Structured logging via `src/utils/api_logger.py`:

- **File**: `logs/api_errors.log`
- **Console**: Stdout for development visibility
- **Level**: INFO for normal operations, ERROR for failures
- **Decorator**: `@log_errors` provides automatic error tracking with full context

Client errors (400-499) logged at INFO level. Server errors (500+) logged at ERROR level with complete traceback.

## Disclaimer

Educational and research purposes only. Not intended for live trading without extensive testing, risk assessment, and regulatory compliance. Past performance does not guarantee future results. Use at your own risk.

## License

[Specify license here]

## Contributing

[Specify contribution guidelines here]
