# Backtrader Integration Documentation

## Overview

StrategyBuilder is built on [Backtrader](https://www.backtrader.com/), a feature-rich Python library for backtesting trading strategies. This document explains how Backtrader is integrated into the project and how to leverage its features.

**Backtrader Version:** 1.9.76.123

---

## Architecture Overview

```
User Request
    ↓
FastAPI Endpoint
    ↓
BacktestService
    ↓
Run_strategy ← Core Backtrader Integration
    ├─→ DataManager (Fetch/Cache Market Data)
    ├─→ Cerebro Engine (Backtrader's main class)
    │   ├─→ Data Feed (PandasData)
    │   ├─→ Strategy (User's strategy class)
    │   ├─→ Broker (Cash, Commission, Position Sizing)
    │   └─→ Analyzers (Performance Metrics)
    ├─→ ChartDataExtractor (Extract OHLC + Indicators + Trades)
    └─→ PerformanceAnalyzer (Calculate Metrics)
    ↓
API Response
```

---

## Core Components

### 1. Cerebro Engine

**File:** `src/core/run_strategy.py`

Cerebro is Backtrader's main orchestration class. We configure it with:

```python
cerebro = bt.Cerebro()

# Add data feed
cerebro.adddata(data_feed)

# Add strategy with parameters
cerebro.addstrategy(strategy_class, **strategy_params)

# Configure broker
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)  # 0.1%

# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

# Run backtest
results = cerebro.run()
```

---

### 2. Data Feeds

**File:** `src/core/data_manager.py`

We use Backtrader's `PandasData` feed to load Yahoo Finance data:

```python
import backtrader as bt

data_feed = bt.feeds.PandasData(
    dataname=dataframe,
    datetime=None,  # Use index as datetime
    open='Open',
    high='High',
    low='Low',
    close='Close',
    volume='Volume',
    openinterest=-1
)
```

**Data Flow:**
1. User requests backtest with ticker and date range
2. `DataManager` checks SQLite cache
3. If not cached, fetches from Yahoo Finance via `yfinance`
4. Validates OHLCV data integrity
5. Caches in SQLite for future requests
6. Converts to pandas DataFrame
7. Creates Backtrader PandasData feed

**Supported Intervals:**
- `1m`, `5m`, `15m`, `30m` - Intraday (short timeframes)
- `1h` - Hourly
- `1d` - Daily (default)
- `1wk` - Weekly
- `1mo` - Monthly

---

### 3. Strategy Skeleton

**File:** `src/core/strategy_skeleton.py`

All strategies inherit from `Strategy_skeleton`, which wraps Backtrader's `Strategy` class:

```python
import backtrader as bt

class Strategy_skeleton(bt.Strategy):
    def __init__(self):
        self.trades = []  # Track all trades
        self.order = None  # Current order

    def notify_order(self, order):
        """Called when order status changes"""
        if order.status in [order.Completed]:
            if order.isbuy():
                # Record buy
                self.trades.append({
                    'type': 'buy',
                    'date': self.data.datetime.date(0),
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.value,
                    'commission': order.executed.comm
                })
            elif order.issell():
                # Record sell with PnL
                self.trades.append({
                    'type': 'sell',
                    'date': self.data.datetime.date(0),
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.value,
                    'commission': order.executed.comm,
                    'pnl': order.executed.pnl
                })

    def buy(self):
        """Execute buy order"""
        self.order = super().buy()

    def sell(self):
        """Execute sell order"""
        self.order = super().sell()

    def get_technical_indicators(self):
        """Override this to return indicator values"""
        return {}
```

**Key Methods:**
- `__init__()`: Initialize indicators
- `next()`: Called on every bar (implement trading logic here)
- `notify_order()`: Called when order executes (tracks trades)
- `get_technical_indicators()`: Returns current indicator values for charting

---

### 4. Broker Configuration

**File:** `src/config/backtest_config.py`

The broker simulates order execution:

```python
# Initial capital
cerebro.broker.setcash(10000.0)

# Commission (0.1% per trade)
cerebro.broker.setcommission(commission=0.001)

# Position sizing (95% of available cash)
position_value = cerebro.broker.getvalue() * 0.95
size = position_value / data.close[0]
```

**Order Types Supported:**
- Market orders (default)
- Limit orders
- Stop orders
- Stop-limit orders

**Current Implementation:**
- Uses market orders only
- Position sizing: 95% of available capital
- Single position at a time (no pyramiding)
- No short selling (long-only strategies)

---

### 5. Analyzers

Backtrader analyzers calculate performance metrics during the backtest.

**Registered Analyzers:**

#### SharpeRatio
```python
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe',
                   timeframe=bt.TimeFrame.Days,
                   riskfreerate=0.0)
```
Measures risk-adjusted returns.

#### Returns
```python
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns',
                   timeframe=bt.TimeFrame.Days)
```
Tracks portfolio returns over time (used for equity curve).

#### TradeAnalyzer
```python
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
```
Provides detailed trade statistics:
- Total trades
- Winning/losing trades
- Win rate
- Average win/loss
- Longest winning/losing streak

#### DrawDown
```python
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
```
Calculates maximum drawdown and drawdown periods.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Makes Request                      │
│   POST /backtest {ticker, strategy, start_date, end_date}   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     DataManager.get_data()                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Check SQLite cache                                  │ │
│  │ 2. If not cached: yfinance.download()                 │ │
│  │ 3. Validate OHLCV data                                │ │
│  │ 4. Cache in SQLite                                     │ │
│  │ 5. Return pandas DataFrame                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Run_strategy.run_backtest()                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Create Cerebro instance                            │ │
│  │ 2. Create PandasData feed from DataFrame              │ │
│  │ 3. Add data feed to Cerebro                           │ │
│  │ 4. Load strategy class                                │ │
│  │ 5. Add strategy with parameters                       │ │
│  │ 6. Configure broker (cash, commission)               │ │
│  │ 7. Add analyzers (Sharpe, Returns, Trades, DrawDown) │ │
│  │ 8. cerebro.run() ─────────────────────┐              │ │
│  └────────────────────────────────────────┼──────────────┘ │
└───────────────────────────────────────────┼────────────────┘
                                            │
                      ┌─────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Backtrader Execution Loop                       │
│  For each bar in data feed:                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Strategy.__init__() runs once                      │ │
│  │    - Initialize indicators                            │ │
│  │                                                        │ │
│  │ 2. For each bar: Strategy.next()                     │ │
│  │    - Read indicator values                            │ │
│  │    - Check trading conditions                         │ │
│  │    - Execute buy/sell orders                          │ │
│  │                                                        │ │
│  │ 3. Broker processes orders                            │ │
│  │    - Calculate position size                          │ │
│  │    - Apply commission                                 │ │
│  │    - Update portfolio value                           │ │
│  │                                                        │ │
│  │ 4. Strategy.notify_order() called                     │ │
│  │    - Record trade details                             │ │
│  │    - Track entry/exit prices                          │ │
│  │                                                        │ │
│  │ 5. Analyzers collect data                             │ │
│  │    - Update metrics on each bar                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Results Extraction                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. Extract analyzer results                           │ │
│  │    - Sharpe ratio                                     │ │
│  │    - Returns (equity curve)                           │ │
│  │    - Trade statistics                                 │ │
│  │    - Drawdown metrics                                 │ │
│  │                                                        │ │
│  │ 2. ChartDataExtractor (if requested)                  │ │
│  │    - OHLCExtractor: Get candlestick data             │ │
│  │    - IndicatorExtractor: Get indicator values         │ │
│  │    - TradeMarkerExtractor: Get entry/exit markers     │ │
│  │                                                        │ │
│  │ 3. PerformanceAnalyzer                                │ │
│  │    - Calculate advanced metrics                       │ │
│  │    - Win rate, profit factor, Sortino, Calmar        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Response                            │
│  {                                                          │
│    "success": true,                                         │
│    "pnl": 1500.0,                                           │
│    "sharpe_ratio": 1.25,                                    │
│    "total_trades": 15,                                      │
│    "advanced_metrics": {...},                              │
│    "chart_data": {...}  // if requested                    │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Indicators

Backtrader includes 100+ built-in indicators. Here are the commonly used ones:

### Built-in Indicators

```python
import backtrader.indicators as btind

# Moving Averages
sma = btind.SMA(data.close, period=20)
ema = btind.EMA(data.close, period=20)
dema = btind.DEMA(data.close, period=20)
tema = btind.TEMA(data.close, period=20)

# Oscillators
rsi = btind.RSI(data.close, period=14)
stoch = btind.Stochastic(data, period=14)
williams = btind.WilliamsR(data, period=14)
cci = btind.CCI(data, period=20)

# Volatility
bbands = btind.BollingerBands(data.close, period=20, devfactor=2.0)
atr = btind.ATR(data, period=14)
keltner = btind.KeltnerChannel(data, period=20)

# Momentum
macd = btind.MACD(data.close, period_me1=12, period_me2=26, period_signal=9)
momentum = btind.Momentum(data.close, period=14)
roc = btind.ROC(data.close, period=12)

# Trend
adx = btind.ADX(data, period=14)

# Volume
obv = btind.OBV(data)  # Note: We have a custom version too
```

### Custom Indicators

We've created 3 custom indicators (see `src/indicators/`):

```python
from src.indicators.cmf_indicator import CMF_Indicator
from src.indicators.mfi_indicator import MFI_Indicator
from src.indicators.obv_indicator import OBV_Indicator

# In strategy __init__()
self.cmf = CMF_Indicator(self.data, period=20)
self.mfi = MFI_Indicator(self.data, period=14)
self.obv = OBV_Indicator(self.data)
```

### Creating Custom Indicators

Example custom indicator structure:

```python
import backtrader as bt

class MyIndicator(bt.Indicator):
    lines = ('my_line',)  # Output lines
    params = (('period', 14),)  # Parameters

    def __init__(self):
        # Indicator calculation
        self.lines.my_line = bt.indicators.SMA(self.data.close, period=self.params.period)

    # Alternative: Override next() for bar-by-bar calculation
    def next(self):
        # Calculate indicator value for current bar
        self.lines.my_line[0] = self.data.close[0] / self.data.close[-self.params.period]
```

---

## Order Management

### Order Types

**Market Order (Current Implementation):**
```python
self.buy()   # Buy at next open
self.sell()  # Sell at next open
```

**Limit Order (Available but not used):**
```python
self.buy(exectype=bt.Order.Limit, price=100.0)
self.sell(exectype=bt.Order.Limit, price=110.0)
```

**Stop Order:**
```python
self.buy(exectype=bt.Order.Stop, price=105.0)
self.sell(exectype=bt.Order.Stop, price=95.0)
```

### Position Sizing

**Current Implementation (95% of capital):**
```python
# In run_strategy.py
position_value = cerebro.broker.getvalue() * 0.95
size = position_value / data.close[0]
cerebro.buy(size=size)
```

**Alternative: Fixed Size:**
```python
self.buy(size=100)  # Buy 100 shares
```

**Alternative: Percentage:**
```python
# Buy using 50% of portfolio
size = (self.broker.getvalue() * 0.5) / self.data.close[0]
self.buy(size=size)
```

---

## Optimization

**File:** `src/core/optimizer.py`

Backtrader supports parameter optimization via `optstrategy()`:

```python
# Instead of addstrategy, use optstrategy
cerebro.optstrategy(
    strategy_class,
    period=range(10, 30, 5),  # Test periods: 10, 15, 20, 25
    threshold=range(20, 50, 10)  # Test thresholds: 20, 30, 40
)

# This will run: 4 periods * 3 thresholds = 12 backtests
results = cerebro.run()
```

**Our Implementation:**
- Grid search over parameter ranges
- Limits to 1000 combinations max
- Returns top 5 by PnL
- See `test_optimization.py` for usage

---

## Performance Considerations

### Data Loading

**Cached (SQLite):**
- ~50ms for 1 year of daily data
- ~200ms for 1 year of hourly data

**Fresh Download (Yahoo Finance):**
- ~1-3 seconds for daily data
- ~3-5 seconds for intraday data

### Backtest Execution

**Daily Data (1 year):**
- Simple strategy: ~100-200ms
- Complex strategy: ~300-500ms

**Hourly Data (1 year):**
- Simple strategy: ~500ms-1s
- Complex strategy: ~1-2s

**Optimization (100 combinations):**
- ~10-30 seconds depending on complexity

---

## Limitations & Considerations

### 1. Look-Ahead Bias

Backtrader prevents look-ahead bias by:
- Orders execute at next bar's open
- Indicators use historical data only
- `[0]` accesses current bar, `[-1]` accesses previous bar

### 2. Slippage

Not currently implemented. All orders execute at exact prices. Consider adding:
```python
cerebro.broker.set_slippage_perc(0.001)  # 0.1% slippage
```

### 3. Market Hours

Not enforced. All bars are tradeable. For realistic intraday backtests, filter by market hours.

### 4. Dividends & Splits

Yahoo Finance data is adjusted for splits but not dividends. Consider using adjusted close prices.

### 5. Multiple Positions

Current implementation: one position at a time. To enable multiple:
```python
# Remove position check in strategy
if not self.position:  # Remove this
    self.buy()
```

---

## Extending Backtrader

### Add Custom Analyzers

```python
class MyAnalyzer(bt.Analyzer):
    def __init__(self):
        self.my_metric = 0

    def notify_trade(self, trade):
        if trade.isclosed:
            self.my_metric += trade.pnl

    def get_analysis(self):
        return {'my_metric': self.my_metric}

# Add to cerebro
cerebro.addanalyzer(MyAnalyzer, _name='my_analyzer')
```

### Add Observers

Observers track data during backtest (useful for plotting):

```python
cerebro.addobserver(bt.observers.Broker)  # Track cash and value
cerebro.addobserver(bt.observers.Trades)  # Mark trades on chart
```

### Add Commission Schemes

```python
# Percentage-based (current)
cerebro.broker.setcommission(commission=0.001)

# Fixed per share
cerebro.broker.setcommission(commission=0.01, commtype=bt.CommInfoBase.COMM_FIXED)

# Custom commission scheme
class MyCommission(bt.CommInfoBase):
    def _getcommission(self, size, price, pseudoexec):
        # Custom logic
        return abs(size) * 0.01
```

---

## Debugging Tips

### 1. Print Current Values

```python
def next(self):
    print(f'Date: {self.data.datetime.date(0)}')
    print(f'Close: {self.data.close[0]}')
    print(f'Indicator: {self.my_indicator[0]}')
    print(f'Position: {self.position.size}')
```

### 2. Check Indicator Values

```python
def next(self):
    indicators = self.get_technical_indicators()
    print(indicators)
```

### 3. Log Orders

```python
def notify_order(self, order):
    if order.status == order.Completed:
        print(f'ORDER EXECUTED: {order.isbuy() and "BUY" or "SELL"} '
              f'Price: {order.executed.price:.2f}')
```

### 4. Validate Data

```python
# Check for NaN values
if len(self.data) < self.params.period:
    return

# Check indicator readiness
if self.my_indicator[0] != self.my_indicator[0]:  # NaN check
    return
```

---

## Resources

- **Backtrader Documentation:** https://www.backtrader.com/docu/
- **Backtrader Community:** https://community.backtrader.com/
- **Built-in Indicators:** https://www.backtrader.com/docu/indautoref/
- **Strategy Examples:** Check `src/strategies/` in this project

---

## Next Steps

1. **Read Backtrader docs:** Understand core concepts
2. **Explore built-in indicators:** See what's available
3. **Study strategy_skeleton.py:** Understand the base class
4. **Create custom strategies:** Use the template in STRATEGIES_DOC.md
5. **Test thoroughly:** Use different tickers and time periods
