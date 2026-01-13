# Architecture Documentation

## Overview

StrategyBuilder is a modular, production-ready backtesting platform built with clean separation of concerns. The architecture follows industry best practices with clear layers: API, Services, Core Engine, and Data Management.

**Core Principles:**
- **Modularity:** Each component has a single responsibility
- **Extensibility:** Easy to add new strategies, indicators, and features
- **Maintainability:** Clean code structure with proper error handling
- **Performance:** Caching, compression, and optimized data structures

---

## Project Structure

```
StrategyBuilder/
├── src/                           # Main application code
│   ├── api/                       # FastAPI layer
│   │   ├── main.py               # API routes and endpoints
│   │   └── models/               # Pydantic models
│   │       ├── requests.py       # Request models
│   │       └── responses.py      # Response models
│   │
│   ├── core/                      # Core backtesting engine
│   │   ├── run_strategy.py       # Main backtest executor
│   │   ├── strategy_skeleton.py  # Base strategy class
│   │   ├── data_manager.py       # Data fetching and caching
│   │   ├── optimizer.py          # Parameter optimization
│   │   └── extractors/           # Data extraction utilities
│   │       ├── chart_data_extractor.py
│   │       ├── ohlc_extractor.py
│   │       ├── indicator_extractor.py
│   │       └── trade_marker_extractor.py
│   │
│   ├── services/                  # Business logic layer
│   │   ├── strategy_service.py   # Strategy discovery and loading
│   │   └── backtest_service.py   # Backtest orchestration
│   │
│   ├── strategies/                # Trading strategy implementations
│   │   ├── williams_r_strategy.py
│   │   ├── bollinger_bands_strategy.py
│   │   ├── rsi_stochastic_strategy.py
│   │   ├── tema_macd_strategy.py
│   │   ├── tema_crossover_strategy.py
│   │   ├── adx_strategy.py
│   │   ├── alligator_strategy.py
│   │   ├── cmf_atr_macd_strategy.py
│   │   ├── cci_atr_strategy.py
│   │   ├── mfi_strategy.py
│   │   ├── keltner_channel_strategy.py
│   │   └── momentum_multi_strategy.py
│   │
│   ├── indicators/                # Custom technical indicators
│   │   ├── cmf_indicator.py      # Chaikin Money Flow
│   │   ├── mfi_indicator.py      # Money Flow Index
│   │   └── obv_indicator.py      # On Balance Volume
│   │
│   ├── config/                    # Configuration files
│   │   ├── backtest_config.py    # Default backtest parameters
│   │   ├── api_config.py         # API configuration
│   │   └── constants.py          # Application constants
│   │
│   ├── utils/                     # Utility modules
│   │   ├── performance_analyzer.py  # Advanced metrics calculation
│   │   └── api_logger.py         # Logging utilities
│   │
│   ├── exceptions/                # Custom exception classes
│   │   ├── base.py
│   │   ├── strategy_errors.py
│   │   └── data_errors.py
│   │
│   └── __init__.py
│
├── data/                          # Data storage
│   └── market_data.db            # SQLite cache for market data
│
├── run_api.py                     # API server launcher
├── test_api.py                    # API testing script
├── test_optimization.py           # Optimization testing script
├── requirements.txt               # Python dependencies
│
└── docs/                          # Documentation (these files)
    ├── API_DOC.md
    ├── STRATEGIES_DOC.md
    ├── BACKTRADER_DOC.md
    └── ARCHITECTURE_DOC.md
```

---

## Architectural Layers

### Layer 1: API (FastAPI)

**Purpose:** HTTP interface for external clients

**Files:** `src/api/main.py`, `src/api/models/`

**Responsibilities:**
- Define REST endpoints
- Validate incoming requests (Pydantic models)
- Handle errors and return proper HTTP responses
- Apply middleware (compression, CORS)
- Route requests to service layer

**Example:**
```python
@app.post("/backtest", response_model=BacktestResponse)
async def backtest(request: BacktestRequest):
    # Validate request
    # Call service layer
    result = backtest_service.run_backtest(
        ticker=request.ticker,
        strategy=request.strategy,
        # ...
    )
    return result
```

**Why FastAPI?**
- Automatic OpenAPI documentation
- Built-in validation with Pydantic
- High performance (async support)
- Type hints for better IDE support

---

### Layer 2: Services

**Purpose:** Business logic orchestration

**Files:** `src/services/strategy_service.py`, `src/services/backtest_service.py`

**Responsibilities:**
- Coordinate between API and core engine
- Load and validate strategies
- Prepare backtest parameters
- Format responses

**Strategy Service:**
```python
class StrategyService:
    def discover_strategies(self):
        """Find all available strategy files"""

    def load_strategy(self, strategy_name):
        """Dynamically load strategy class"""

    def get_strategy_info(self, strategy_name):
        """Get strategy parameters and description"""
```

**Backtest Service:**
```python
class BacktestService:
    def run_backtest(self, ticker, strategy, ...):
        """Orchestrate entire backtest process"""
        # 1. Load strategy
        # 2. Fetch data
        # 3. Run backtest
        # 4. Extract results
        # 5. Calculate metrics
        # 6. Return formatted response
```

---

### Layer 3: Core Engine

**Purpose:** Backtrader integration and execution

**Files:** `src/core/`

#### 3.1 Run Strategy (`run_strategy.py`)

Main backtest executor:

```python
class Run_strategy:
    def run_backtest(self, data, strategy_class, cash, commission, ...):
        # Create Cerebro
        cerebro = bt.Cerebro()

        # Add data feed
        cerebro.adddata(data_feed)

        # Add strategy
        cerebro.addstrategy(strategy_class, **params)

        # Configure broker
        cerebro.broker.setcash(cash)
        cerebro.broker.setcommission(commission)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        # ...

        # Run
        results = cerebro.run()

        # Extract metrics
        return self._extract_results(results)
```

#### 3.2 Strategy Skeleton (`strategy_skeleton.py`)

Base class for all strategies:

```python
class Strategy_skeleton(bt.Strategy):
    def __init__(self):
        self.trades = []
        self.order = None

    def notify_order(self, order):
        """Track order execution"""

    def get_technical_indicators(self):
        """Override in subclass"""
        return {}
```

#### 3.3 Data Manager (`data_manager.py`)

Handles data fetching and caching:

```python
class DataManager:
    def get_data(self, ticker, start, end, interval):
        # Check cache
        cached = self._get_from_cache(ticker, start, end, interval)
        if cached:
            return cached

        # Fetch from Yahoo Finance
        data = yfinance.download(ticker, start, end, interval)

        # Validate
        self._validate_data(data)

        # Cache
        self._save_to_cache(ticker, data, interval)

        return data
```

**Cache Structure (SQLite):**
```sql
CREATE TABLE market_data (
    id INTEGER PRIMARY KEY,
    ticker TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    interval TEXT,
    timestamp TEXT
);

CREATE INDEX idx_ticker_date ON market_data(ticker, date, interval);
```

#### 3.4 Optimizer (`optimizer.py`)

Parameter optimization via grid search:

```python
class StrategyOptimizer:
    def optimize(self, data, strategy_class, param_ranges):
        # Generate combinations (limit to 1000)
        combinations = self._generate_combinations(param_ranges)

        # Use Backtrader optstrategy
        cerebro.optstrategy(strategy_class, **param_ranges)

        # Run all combinations
        results = cerebro.run()

        # Return top 5 by PnL
        return self._rank_results(results)
```

#### 3.5 Chart Data Extractors

**Unified Extractor (`chart_data_extractor.py`):**
```python
class ChartDataExtractor:
    def extract(self, strategy, data, columnar=True):
        # Get OHLC data
        ohlc = OHLCExtractor.extract(data)

        # Get indicators
        indicators = IndicatorExtractor.extract(strategy)

        # Get trade markers
        trades = TradeMarkerExtractor.extract(strategy.trades, data)

        # Merge on timeline
        chart_data = self._merge(ohlc, indicators, trades)

        # Format (row or columnar)
        if columnar:
            return self._to_columnar(chart_data)
        return chart_data
```

---

### Layer 4: Strategies

**Purpose:** Trading logic implementations

**Files:** `src/strategies/*.py`

**Structure:**
```python
class MyStrategy(Strategy_skeleton):
    params = (
        ('period', 14),
        ('threshold', 70),
    )

    def __init__(self):
        super().__init__()
        self.indicator = bt.indicators.RSI(self.data, period=self.params.period)

    def next(self):
        if not self.position:
            if self.indicator[0] < self.params.threshold:
                self.buy()
        else:
            if self.indicator[0] > 100 - self.params.threshold:
                self.sell()

    def get_technical_indicators(self):
        return {'RSI': self.indicator[0]}
```

**Discovery Mechanism:**
- Strategies are auto-discovered from `src/strategies/` directory
- No manual registration required
- Simply drop a new `.py` file with strategy class

---

### Layer 5: Data Models

**Purpose:** Type-safe request/response structures

**Files:** `src/api/models/requests.py`, `src/api/models/responses.py`

**Example:**
```python
class BacktestRequest(BaseModel):
    ticker: str
    strategy: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interval: str = "1d"
    cash: float = 10000.0
    parameters: Optional[Dict] = None
    include_chart_data: bool = False
    columnar_format: bool = True

class BacktestResponse(BaseModel):
    success: bool
    ticker: str
    strategy: str
    pnl: float
    return_pct: float
    sharpe_ratio: Optional[float]
    # ... many more fields
```

---

## Data Flow

### Complete Request Flow

```
1. Client sends POST /backtest
   ↓
2. FastAPI validates request with Pydantic
   ↓
3. API endpoint calls BacktestService.run_backtest()
   ↓
4. BacktestService loads strategy via StrategyService
   ↓
5. BacktestService fetches data via DataManager
   ├─→ Check SQLite cache
   └─→ If miss: fetch from Yahoo Finance, cache, return
   ↓
6. BacktestService calls Run_strategy.run_backtest()
   ↓
7. Run_strategy creates Cerebro instance
   ├─→ Add data feed
   ├─→ Add strategy with parameters
   ├─→ Configure broker
   └─→ Add analyzers
   ↓
8. cerebro.run() executes backtest
   ├─→ Strategy.__init__() runs once
   ├─→ For each bar: Strategy.next() executes
   ├─→ Broker processes orders
   └─→ Analyzers collect metrics
   ↓
9. Run_strategy extracts results
   ├─→ Get analyzer results
   ├─→ Build equity curve
   └─→ Get trade list from strategy
   ↓
10. If include_chart_data:
    ChartDataExtractor.extract()
    ├─→ OHLCExtractor gets price data
    ├─→ IndicatorExtractor gets indicator values
    └─→ TradeMarkerExtractor gets trade markers
    ↓
11. PerformanceAnalyzer calculates advanced metrics
    ├─→ Win rate, profit factor
    ├─→ Sortino ratio, Calmar ratio
    └─→ Trade statistics
    ↓
12. BacktestService formats response
    ↓
13. FastAPI serializes to JSON
    ↓
14. GZip middleware compresses response
    ↓
15. Client receives response
```

---

## Key Design Patterns

### 1. Strategy Pattern

**Usage:** Different trading strategies

**Implementation:**
- `Strategy_skeleton` defines interface
- Concrete strategies implement `next()` and `get_technical_indicators()`
- Client can switch strategies without changing code

### 2. Template Method Pattern

**Usage:** `Strategy_skeleton` base class

**Implementation:**
```python
class Strategy_skeleton:
    def notify_order(self):  # Template method
        # Common logic for all strategies
        # Calls hooks that subclasses can override
```

### 3. Factory Pattern

**Usage:** Strategy loading

**Implementation:**
```python
class StrategyService:
    def load_strategy(self, strategy_name):
        # Dynamically import and return strategy class
        module = importlib.import_module(f'src.strategies.{strategy_name}')
        return getattr(module, 'StrategyClass')
```

### 4. Facade Pattern

**Usage:** `BacktestService` simplifies complex subsystems

**Implementation:**
```python
class BacktestService:
    def run_backtest(self, ...):
        # Hides complexity of:
        # - Data loading
        # - Strategy loading
        # - Backtest execution
        # - Result extraction
        # - Metric calculation
```

### 5. Repository Pattern

**Usage:** `DataManager` abstracts data storage

**Implementation:**
```python
class DataManager:
    def get_data(self):
        # Client doesn't know if data comes from cache or API
```

---

## Configuration Management

### Backtest Config (`src/config/backtest_config.py`)

```python
class BacktestConfig:
    DEFAULT_CASH = 10000.0
    DEFAULT_COMMISSION = 0.001  # 0.1%
    DEFAULT_POSITION_SIZE = 0.95  # 95% of capital
    DEFAULT_INTERVAL = "1d"
    DEFAULT_BACKTEST_PERIOD_DAYS = 365

    # MACD defaults
    MACD_FAST_PERIOD = 12
    MACD_SLOW_PERIOD = 26
    MACD_SIGNAL_PERIOD = 9

    # ATR defaults
    ATR_PERIOD = 14
    ATR_DISTANCE = 2.0
```

### API Config (`src/config/api_config.py`)

```python
class APIConfig:
    HOST = "0.0.0.0"
    PORT = 8086
    LOG_LEVEL = "info"
    ENABLE_COMPRESSION = True
```

---

## Error Handling

### Exception Hierarchy

```python
# Base exception
class StrategyBuilderException(Exception):
    pass

# Strategy errors
class StrategyNotFoundError(StrategyBuilderException):
    pass

class StrategyLoadError(StrategyBuilderException):
    pass

# Data errors
class DataFetchError(StrategyBuilderException):
    pass

class DataValidationError(StrategyBuilderException):
    pass
```

### Error Flow

```python
# In service layer
try:
    result = run_backtest(...)
except StrategyNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except DataFetchError as e:
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Performance Optimizations

### 1. Data Caching

**SQLite Cache:**
- Stores market data locally
- Indexed by ticker, date, interval
- Reduces API calls to Yahoo Finance
- ~50ms cache hit vs ~2s fresh download

### 2. Response Compression

**GZip Middleware:**
```python
app.add_middleware(GZipMiddleware, minimum_size=1000)
```
- Compresses responses > 1KB
- ~70% size reduction for chart data

### 3. Columnar Data Format

**Traditional (row format):**
```json
[{"date": "2024-01-01", "open": 100}, ...]
```

**Optimized (columnar format):**
```json
{"date": [...], "open": [...]}
```
- ~30% smaller
- Faster serialization
- Better for charting libraries

### 4. Selective Chart Data

**Default:** No chart data (~1KB response)
**Optional:** Include chart data (~500KB response)

Clients only request chart data when needed.

---

## Testing Strategy

### Unit Tests

Not currently implemented, but recommended structure:

```python
tests/
├── unit/
│   ├── test_data_manager.py
│   ├── test_strategy_service.py
│   └── test_performance_analyzer.py
├── integration/
│   ├── test_backtest_flow.py
│   └── test_api_endpoints.py
└── strategies/
    ├── test_williams_r.py
    └── test_bollinger_bands.py
```

### Current Testing

**Manual API Testing:**
```python
python test_api.py          # Test all endpoints
python test_optimization.py  # Test optimization
```

**Strategy Testing:**
- Run backtest on known data
- Verify expected number of trades
- Check performance metrics

---

## Deployment Considerations

### 1. Environment Variables

Recommended `.env` file:
```bash
API_HOST=0.0.0.0
API_PORT=8086
DB_PATH=./data/market_data.db
LOG_LEVEL=info
CACHE_TTL_DAYS=30
```

### 2. Docker Deployment

Example `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY run_api.py .

EXPOSE 8086
CMD ["python", "run_api.py"]
```

### 3. Production Checklist

- [ ] Add authentication/API keys
- [ ] Implement rate limiting
- [ ] Set up logging (ELK, CloudWatch)
- [ ] Add monitoring (Prometheus, Grafana)
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Add health checks
- [ ] Configure reverse proxy (nginx)
- [ ] Enable HTTPS

---

## Security Considerations

### 1. Input Validation

All inputs validated with Pydantic models:
- Ticker format
- Date ranges
- Parameter types

### 2. SQL Injection Prevention

Using parameterized queries:
```python
cursor.execute(
    "SELECT * FROM market_data WHERE ticker=? AND date=?",
    (ticker, date)
)
```

### 3. Rate Limiting

Not implemented. Recommended:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/backtest")
@limiter.limit("10/minute")
async def backtest(...):
    ...
```

### 4. Authentication

Not implemented. Recommended:
- API key authentication
- JWT tokens
- OAuth2

---

## Monitoring & Observability

### Logging

**Current:** Basic console logging

**Recommended:**
```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

### Metrics to Track

- Request latency
- Backtest execution time
- Cache hit rate
- Error rates
- Active strategies
- Data fetch failures

### Health Checks

```python
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": check_db_connection(),
        "cache_size": get_cache_size(),
        "uptime": get_uptime()
    }
```

---

## Future Enhancements

### 1. WebSocket Support

Real-time backtest progress:
```python
@app.websocket("/ws/backtest")
async def backtest_ws(websocket: WebSocket):
    # Stream progress updates
```

### 2. Multi-Asset Backtesting

Test strategies across portfolios:
```python
tickers = ["AAPL", "TSLA", "GOOGL"]
# Run backtest on all
```

### 3. Live Trading Integration

Connect to brokers (Alpaca, Interactive Brokers):
```python
# Execute strategy in real-time
```

### 4. Machine Learning Integration

Optimize strategies with ML:
```python
# Use scikit-learn for parameter optimization
```

### 5. Custom Metrics

Allow users to define custom performance metrics:
```python
class CustomAnalyzer(bt.Analyzer):
    # User-defined metric calculation
```

---

## Development Workflow

### Adding a New Strategy

1. Create `src/strategies/my_strategy.py`
2. Extend `Strategy_skeleton`
3. Implement `next()` and `get_technical_indicators()`
4. Test with `test_api.py`
5. No restart needed - auto-discovered!

### Adding a New Indicator

1. Create `src/indicators/my_indicator.py`
2. Extend `bt.Indicator`
3. Define `lines` and `params`
4. Implement calculation in `__init__()` or `next()`
5. Use in strategies

### Adding a New Endpoint

1. Define Pydantic models in `src/api/models/`
2. Add route in `src/api/main.py`
3. Implement business logic in service layer
4. Test with `curl` or `test_api.py`

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| API | FastAPI 0.104.1 | REST API framework |
| Engine | Backtrader 1.9.76.123 | Backtesting engine |
| Data | yfinance 0.2.37 | Market data fetching |
| Cache | SQLite 3 | Local data storage |
| Validation | Pydantic 2.5.3 | Request/response validation |
| Server | Uvicorn 0.25.0 | ASGI server |
| Data Processing | Pandas 2.1.4, NumPy 1.26.2 | Data manipulation |
| Analysis | SciPy 1.11.4 | Statistical calculations |

---

## Conclusion

StrategyBuilder is architected for:
- **Ease of use:** Simple API, auto-discovery
- **Extensibility:** Add strategies without core changes
- **Performance:** Caching, compression, optimization
- **Maintainability:** Clean separation, proper error handling
- **Production-ready:** Robust design, scalable architecture

The modular design allows developers to focus on strategy logic while the framework handles data management, execution, and result analysis.
