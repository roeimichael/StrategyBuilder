# Trading Strategies Documentation

## Overview

StrategyBuilder includes 12 pre-built trading strategies, all built on the Backtrader framework. Each strategy extends the `Strategy_skeleton` base class and implements specific trading logic using technical indicators.

---

## Strategy Architecture

All strategies follow this structure:

```python
class MyStrategy(Strategy_skeleton):
    params = (
        ('param1', default_value),
        ('param2', default_value),
    )

    def __init__(self):
        # Initialize indicators

    def next(self):
        # Trading logic executed on each bar

    def get_technical_indicators(self):
        # Return dict of current indicator values
```

---

## Available Strategies

### 1. Williams %R Strategy

**File:** `williams_r_strategy.py`

**Description:** Oscillator-based mean reversion strategy using Williams %R indicator.

**How it works:**
- Buys when Williams %R crosses above lower threshold (oversold)
- Sells when Williams %R crosses below upper threshold (overbought)

**Parameters:**
```python
{
  "period": 14,              # Williams %R lookback period
  "upper_threshold": -20,    # Overbought level (exit signal)
  "lower_threshold": -80     # Oversold level (entry signal)
}
```

**Indicators Used:**
- Williams %R

---

### 2. Bollinger Bands Strategy

**File:** `bollinger_bands_strategy.py`

**Description:** Mean reversion strategy based on Bollinger Bands crossovers.

**How it works:**
- Buys when price crosses above lower band (oversold)
- Sells when price crosses above upper band (overbought)

**Parameters:**
```python
{
  "period": 20,           # Moving average period
  "devfactor": 2.0        # Standard deviation multiplier
}
```

**Indicators Used:**
- Bollinger Bands (Upper, Middle, Lower)

---

### 3. RSI + Stochastic Strategy

**File:** `rsi_stochastic_strategy.py`

**Description:** Combines RSI and Stochastic oscillators for confirmation.

**How it works:**
- Buys when both RSI < lower threshold AND Stochastic %K < lower threshold
- Sells when both RSI > upper threshold AND Stochastic %K > upper threshold

**Parameters:**
```python
{
  "rsi_period": 14,
  "rsi_upper": 70,
  "rsi_lower": 30,
  "stoch_period_k": 14,
  "stoch_period_d": 3,
  "stoch_upper": 80,
  "stoch_lower": 20
}
```

**Indicators Used:**
- RSI (Relative Strength Index)
- Stochastic Oscillator (%K, %D)

---

### 4. TEMA + MACD Strategy

**File:** `tema_macd_strategy.py`

**Description:** Triple Exponential Moving Average with MACD confirmation.

**How it works:**
- Buys when MACD crosses above signal line AND price > TEMA
- Sells when MACD crosses below signal line

**Parameters:**
```python
{
  "tema_period": 10,
  "macd_period_me1": 12,     # Fast EMA period
  "macd_period_me2": 26,     # Slow EMA period
  "macd_period_signal": 9    # Signal line period
}
```

**Indicators Used:**
- TEMA (Triple Exponential Moving Average)
- MACD (Line, Signal, Histogram)

---

### 5. TEMA Crossover Strategy

**File:** `tema_crossover_strategy.py`

**Description:** Dual TEMA moving average crossover system.

**How it works:**
- Buys when fast TEMA crosses above slow TEMA
- Sells when fast TEMA crosses below slow TEMA

**Parameters:**
```python
{
  "fast_period": 10,
  "slow_period": 30
}
```

**Indicators Used:**
- TEMA Fast
- TEMA Slow

---

### 6. ADX Strategy

**File:** `adx_strategy.py`

**Description:** Trend strength strategy using Average Directional Index.

**How it works:**
- Buys when ADX > threshold AND +DI > -DI (strong uptrend)
- Sells when ADX > threshold AND -DI > +DI (strong downtrend)

**Parameters:**
```python
{
  "period": 14,
  "adx_threshold": 25    # Minimum ADX for trend strength
}
```

**Indicators Used:**
- ADX (Average Directional Index)
- +DI (Plus Directional Indicator)
- -DI (Minus Directional Indicator)

---

### 7. Alligator Strategy

**File:** `alligator_strategy.py`

**Description:** Bill Williams' Alligator indicator strategy.

**How it works:**
- Buys when price > Jaw AND Lips > Teeth > Jaw (alligator is "opening")
- Sells when price < Jaw (alligator is "closing")

**Parameters:**
```python
{
  "jaw_period": 13,       # Blue line (slowest)
  "jaw_offset": 8,
  "teeth_period": 8,      # Red line (medium)
  "teeth_offset": 5,
  "lips_period": 5,       # Green line (fastest)
  "lips_offset": 3
}
```

**Indicators Used:**
- Alligator Jaw (Blue line)
- Alligator Teeth (Red line)
- Alligator Lips (Green line)

---

### 8. CMF + ATR + MACD Strategy

**File:** `cmf_atr_macd_strategy.py`

**Description:** Multi-indicator strategy combining volume flow, volatility, and momentum.

**How it works:**
- Buys when CMF > threshold AND price > lower ATR band AND MACD > signal
- Sells when CMF < -threshold

**Parameters:**
```python
{
  "cmf_period": 20,
  "cmf_threshold": 0.05,
  "atr_period": 14,
  "atr_distance": 2.0,
  "macd_period_me1": 12,
  "macd_period_me2": 26,
  "macd_period_signal": 9
}
```

**Indicators Used:**
- CMF (Chaikin Money Flow) - custom indicator
- ATR (Average True Range)
- MACD

---

### 9. CCI + ATR Strategy

**File:** `cci_atr_strategy.py`

**Description:** Commodity Channel Index with ATR-based dynamic levels.

**How it works:**
- Buys when CCI crosses above lower level (oversold)
- Sells when CCI crosses below upper level (overbought)
- ATR bands provide dynamic support/resistance

**Parameters:**
```python
{
  "cci_period": 20,
  "cci_upper": 100,
  "cci_lower": -100,
  "atr_period": 14,
  "atr_distance": 2.0
}
```

**Indicators Used:**
- CCI (Commodity Channel Index)
- ATR bands (Upper, Lower)

---

### 10. MFI Strategy

**File:** `mfi_strategy.py`

**Description:** Money Flow Index oscillator strategy (volume-weighted RSI).

**How it works:**
- Buys when MFI crosses above lower threshold (oversold)
- Sells when MFI crosses below upper threshold (overbought)

**Parameters:**
```python
{
  "period": 14,
  "upper_threshold": 80,
  "lower_threshold": 20
}
```

**Indicators Used:**
- MFI (Money Flow Index) - custom indicator

---

### 11. Keltner Channel Strategy

**File:** `keltner_channel_strategy.py`

**Description:** Volatility-based channel breakout strategy.

**How it works:**
- Buys when price crosses above upper channel (breakout)
- Sells when price crosses below lower channel (breakdown)

**Parameters:**
```python
{
  "ema_period": 20,
  "atr_period": 14,
  "atr_multiplier": 2.0
}
```

**Indicators Used:**
- Keltner Channel (Upper, Middle, Lower)
- Based on EMA and ATR

---

### 12. Momentum Multi Strategy

**File:** `momentum_multi_strategy.py`

**Description:** Multi-indicator momentum combination strategy.

**How it works:**
- Combines multiple momentum indicators for confirmation
- Buys when majority of indicators signal bullish momentum
- Sells when momentum weakens

**Parameters:**
```python
{
  "rsi_period": 14,
  "macd_period_me1": 12,
  "macd_period_me2": 26,
  "macd_period_signal": 9,
  "ema_period": 20
}
```

**Indicators Used:**
- RSI
- MACD
- EMA

---

## Technical Indicators Reference

### Indicator Naming Conventions

**Single-Line Indicators:**
- `RSI` - Relative Strength Index
- `Williams_R` - Williams %R
- `MFI` - Money Flow Index
- `CCI` - Commodity Channel Index
- `ADX` - Average Directional Index
- `CMF` - Chaikin Money Flow
- `ATR` - Average True Range

**Multi-Line Indicators:**
- `SMA_{period}` - Simple Moving Average
- `EMA_{period}` - Exponential Moving Average
- `TEMA_{period}` - Triple Exponential Moving Average
- `Bollinger_Upper`, `Bollinger_Middle`, `Bollinger_Lower`
- `MACD`, `MACD_Signal`, `MACD_Histogram`
- `Stochastic_K`, `Stochastic_D`
- `Keltner_Upper`, `Keltner_Middle`, `Keltner_Lower`
- `Alligator_Jaw`, `Alligator_Teeth`, `Alligator_Lips`
- `ATR_Upper`, `ATR_Lower` (when used as bands)

---

## Custom Indicators

The project includes 3 custom Backtrader indicators:

### 1. Chaikin Money Flow (CMF)

**File:** `indicators/cmf_indicator.py`

Measures buying and selling pressure over a period based on volume and price location.

**Formula:**
```
CMF = Sum(Money Flow Volume) / Sum(Volume)
Money Flow Volume = ((Close - Low) - (High - Close)) / (High - Low) * Volume
```

**Usage:**
```python
self.cmf = CMF_Indicator(self.data, period=20)
```

---

### 2. Money Flow Index (MFI)

**File:** `indicators/mfi_indicator.py`

Volume-weighted version of RSI that measures buying/selling pressure.

**Formula:**
```
Typical Price = (High + Low + Close) / 3
Money Flow = Typical Price * Volume
Money Ratio = Positive Money Flow / Negative Money Flow
MFI = 100 - (100 / (1 + Money Ratio))
```

**Usage:**
```python
self.mfi = MFI_Indicator(self.data, period=14)
```

---

### 3. On Balance Volume (OBV)

**File:** `indicators/obv_indicator.py`

Cumulative volume indicator that tracks volume flow.

**Formula:**
```
If Close > Previous Close: OBV = Previous OBV + Volume
If Close < Previous Close: OBV = Previous OBV - Volume
If Close = Previous Close: OBV = Previous OBV
```

**Usage:**
```python
self.obv = OBV_Indicator(self.data)
```

---

## Creating a New Strategy

To create a new trading strategy:

### 1. Create Strategy File

Create a new file in `src/strategies/` (e.g., `my_strategy.py`):

```python
from src.core.strategy_skeleton import Strategy_skeleton
import backtrader as bt

class MyStrategy(Strategy_skeleton):
    params = (
        ('my_param', 20),
    )

    def __init__(self):
        super().__init__()
        # Initialize your indicators
        self.my_indicator = bt.indicators.SMA(self.data.close, period=self.params.my_param)

    def next(self):
        # Check if we have an open position
        if not self.position:
            # Entry logic
            if self.data.close[0] > self.my_indicator[0]:
                self.buy()
        else:
            # Exit logic
            if self.data.close[0] < self.my_indicator[0]:
                self.sell()

    def get_technical_indicators(self):
        """Return current indicator values for charting"""
        return {
            'SMA_20': self.my_indicator[0]
        }
```

### 2. Strategy Will Be Auto-Discovered

The `StrategyService` automatically discovers all strategies in the `src/strategies/` directory. No registration required!

### 3. Test Your Strategy

```bash
curl -X POST http://localhost:8086/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "strategy": "my_strategy",
    "parameters": {
      "my_param": 30
    }
  }'
```

---

## Strategy Best Practices

### 1. Always Call super().__init__()

```python
def __init__(self):
    super().__init__()  # Required for trade tracking
    # Your initialization code
```

### 2. Implement get_technical_indicators()

This method is required for chart data extraction:

```python
def get_technical_indicators(self):
    return {
        'Indicator_Name': self.indicator[0],
        'Another_Indicator': self.another[0]
    }
```

### 3. Use Descriptive Parameter Names

```python
params = (
    ('period', 14),              # Good
    ('rsi_upper_threshold', 70), # Better
    ('p', 14),                   # Bad
)
```

### 4. Handle Edge Cases

```python
def next(self):
    # Check if we have enough data
    if len(self.data) < self.params.period:
        return

    # Your trading logic
```

### 5. Document Your Strategy

Add a docstring explaining the strategy logic:

```python
class MyStrategy(Strategy_skeleton):
    """
    My Custom Strategy

    Entry: When condition A and condition B
    Exit: When condition C

    Parameters:
    - param1: Description of param1
    - param2: Description of param2
    """
```

---

## Strategy Testing Tips

### Test with Different Time Intervals

```python
intervals = ["1d", "1h", "15m"]
for interval in intervals:
    # Run backtest with each interval
```

### Test with Different Tickers

```python
tickers = ["AAPL", "TSLA", "BTC-USD", "ETH-USD"]
for ticker in tickers:
    # Run backtest with each ticker
```

### Optimize Parameters

Use the optimization endpoint to find best parameters:

```python
# See test_optimization.py for examples
```

### Analyze Advanced Metrics

Don't just look at PnL - check:
- Win rate (aim for >50%)
- Profit factor (aim for >1.5)
- Sharpe ratio (aim for >1.0)
- Max drawdown (keep low)

---

## Common Pitfalls

### 1. Look-Ahead Bias

**Bad:**
```python
if self.data.close[1] > self.data.close[0]:  # Looking into the future!
    self.buy()
```

**Good:**
```python
if self.data.close[0] > self.data.close[-1]:  # Using past data
    self.buy()
```

### 2. Over-Optimization

Testing 100 parameter combinations and picking the best will likely lead to overfitting. Use:
- Out-of-sample testing
- Walk-forward analysis
- Cross-validation

### 3. Ignoring Commission

Always account for trading fees:
```python
# Commission is set at 0.1% by default in BacktestConfig
```

### 4. Position Sizing

The system uses 95% of available capital by default. Consider:
- Risk management
- Multiple positions
- Reserve cash for drawdowns

---

## Strategy Performance Comparison

Use the test script to compare strategies:

```python
strategies = [
    "williams_r_strategy",
    "rsi_stochastic_strategy",
    "bollinger_bands_strategy"
]

results = {}
for strategy in strategies:
    result = backtest(ticker="AAPL", strategy=strategy)
    results[strategy] = result['return_pct']

# Compare results
```

---

## Next Steps

1. **Understand the base class:** Read `src/core/strategy_skeleton.py`
2. **Study existing strategies:** Look at simple ones first (williams_r, bollinger_bands)
3. **Create your strategy:** Follow the template above
4. **Test thoroughly:** Use different tickers, intervals, and time periods
5. **Optimize carefully:** Avoid overfitting
6. **Deploy:** Use the API to run your strategy in production
