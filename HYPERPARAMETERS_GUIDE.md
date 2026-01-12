# Trading Strategy Hyperparameters Guide

## Overview

This guide explains the different types of hyperparameters used in trading strategies, what they mean, and how adjusting them affects strategy performance.

---

## Table of Contents

1. [Period Parameters](#period-parameters)
2. [Oversold/Overbought Thresholds](#oversoldoverbought-thresholds)
3. [Multipliers and Factors](#multipliers-and-factors)
4. [Entry/Exit Thresholds](#entryexit-thresholds)
5. [Moving Average Periods](#moving-average-periods)
6. [Volatility Parameters](#volatility-parameters)

---

## 1. Period Parameters

**What it is:** The number of bars (candles) to look back when calculating an indicator.

**Common names:**
- `period`
- `lookback`
- `window`

**How it works:**
- **Short periods (5-10)**: More sensitive, reacts quickly to price changes, generates more signals (more trades)
- **Medium periods (14-20)**: Balanced, standard for most indicators
- **Long periods (30-50)**: Less sensitive, smoother, generates fewer signals (fewer trades)

**Examples:**

### RSI Period = 14 (Standard)
```
Price: $100 → $110 → $105
RSI(14): 45 → 65 → 55
Signal: Moderate movement
```

### RSI Period = 7 (Fast)
```
Price: $100 → $110 → $105
RSI(7): 40 → 75 → 45
Signal: More volatile, quicker to trigger
```

### RSI Period = 28 (Slow)
```
Price: $100 → $110 → $105
RSI(28): 48 → 58 → 52
Signal: Smoother, slower to react
```

**When to optimize:**
- ✅ Different timeframes (1h vs 1d) often need different periods
- ✅ Different market conditions (trending vs ranging)
- ✅ Different volatility levels (crypto vs stocks)

---

## 2. Oversold/Overbought Thresholds

**What it is:** Levels that indicate when an asset has moved "too far" in one direction.

**Common indicators:**
- **RSI**: 0-100 scale
- **Stochastic**: 0-100 scale
- **Williams %R**: -100 to 0 scale (negative)
- **MFI**: 0-100 scale

### Oversold Threshold

**Definition:** Price has fallen too much, too fast → Potential BUY signal

**How it works:**
- Indicator drops **below** the oversold level
- Suggests selling pressure is exhausted
- Buyers may step in soon
- **Lower threshold = more conservative** (fewer, stronger signals)
- **Higher threshold = more aggressive** (more signals, more trades)

**RSI Example:**

| Threshold | Conservative ← → Aggressive |
|-----------|----------------------------|
| Oversold = 20 | Very oversold, strong buy signal |
| Oversold = 30 | Standard oversold (most common) |
| Oversold = 40 | Slightly oversold, more signals |

```
RSI drops to 25:
- If threshold = 20: ✅ BUY signal triggered (below 20)
- If threshold = 30: ✅ BUY signal triggered (below 30)
- If threshold = 40: ❌ No signal (above 40)
```

### Overbought Threshold

**Definition:** Price has risen too much, too fast → Potential SELL signal

**How it works:**
- Indicator rises **above** the overbought level
- Suggests buying pressure is exhausted
- Sellers may step in soon
- **Higher threshold = more conservative** (fewer, stronger signals)
- **Lower threshold = more aggressive** (more signals, more trades)

**RSI Example:**

| Threshold | Aggressive ← → Conservative |
|-----------|----------------------------|
| Overbought = 60 | Mildly overbought, more signals |
| Overbought = 70 | Standard overbought (most common) |
| Overbought = 80 | Very overbought, strong sell signal |

```
RSI rises to 75:
- If threshold = 60: ✅ SELL signal (above 60)
- If threshold = 70: ✅ SELL signal (above 70)
- If threshold = 80: ❌ No signal (below 80)
```

### Williams %R (Negative Scale)

**Special case:** Uses -100 to 0 scale (all negative)

| Threshold | Meaning |
|-----------|---------|
| Oversold = -80 | When W%R < -80 (closer to -100) = oversold → BUY |
| Overbought = -20 | When W%R > -20 (closer to 0) = overbought → SELL |

```
More conservative: -90/-10 (fewer signals)
Standard: -80/-20
More aggressive: -70/-30 (more signals)
```

---

## 3. Multipliers and Factors

**What it is:** A number that scales or multiplies another value, typically for bands or channels.

**Common names:**
- `devfactor` (standard deviation factor)
- `atr_multiplier` (ATR multiplier)
- `multiplier`

### Standard Deviation Factor (Bollinger Bands)

**How it works:**
- Bollinger Bands = MA ± (Standard Deviation × Factor)
- **Factor = 1.5**: Tighter bands, more signals (price crosses bands more often)
- **Factor = 2.0**: Standard bands (most common)
- **Factor = 2.5**: Wider bands, fewer signals (price crosses bands less often)

**Visual:**
```
Price: ========= (fluctuates around MA)

Factor 1.5 (Tight):
Upper: ─────────  ←─ 1.5 std devs above
MA:    ═════════
Lower: ─────────  ←─ 1.5 std devs below
Result: Price crosses bands frequently

Factor 2.0 (Standard):
Upper: ─────────  ←─ 2.0 std devs above
MA:    ═════════
Lower: ─────────  ←─ 2.0 std devs below
Result: Balanced signals

Factor 2.5 (Wide):
Upper: ─────────  ←─ 2.5 std devs above
MA:    ═════════
Lower: ─────────  ←─ 2.5 std devs below
Result: Price rarely crosses bands
```

**When to use:**
- **Low volatility** (stocks): Use smaller multipliers (1.5-2.0)
- **High volatility** (crypto): Use larger multipliers (2.0-3.0)

### ATR Multiplier (Stop Loss / Channel Width)

**How it works:**
- Stop Loss = Entry Price ± (ATR × Multiplier)
- **Multiplier = 1.0**: Tight stops, exit quickly
- **Multiplier = 2.0**: Standard stops
- **Multiplier = 3.0**: Loose stops, give trades more room

**Example:**
```
Entry Price: $100
ATR (volatility): $2

Multiplier = 1.5:
Stop Loss = $100 - ($2 × 1.5) = $97
Risk: $3 per share (tight)

Multiplier = 2.0:
Stop Loss = $100 - ($2 × 2.0) = $96
Risk: $4 per share (standard)

Multiplier = 3.0:
Stop Loss = $100 - ($2 × 3.0) = $94
Risk: $6 per share (loose, more room)
```

---

## 4. Entry/Exit Thresholds

**What it is:** Specific levels an indicator must cross to trigger a trade signal.

**Common indicators:**
- **CCI** (Commodity Channel Index)
- **ROC** (Rate of Change)

### CCI Entry/Exit Thresholds

**Scale:** Typically -200 to +200 (but can go beyond)

**How it works:**
- **Entry threshold** (negative): When CCI crosses above this level → BUY
- **Exit threshold** (positive): When CCI crosses below this level → SELL

**Example:**
```
CCI Entry = -100:
- CCI moves from -120 to -90
- Crosses above -100
- ✅ BUY signal triggered

CCI Exit = +100:
- CCI moves from +110 to +90
- Crosses below +100
- ✅ SELL signal triggered
```

**Adjusting thresholds:**

| Conservative | Standard | Aggressive |
|-------------|----------|-----------|
| Entry: -150 | Entry: -100 | Entry: -50 |
| Exit: +150 | Exit: +100 | Exit: +50 |
| Fewer trades | Balanced | More trades |

---

## 5. Moving Average Periods

**What it is:** The number of bars used to calculate an average price.

**Types:**
- **SMA** (Simple Moving Average)
- **EMA** (Exponential Moving Average)
- **TEMA** (Triple Exponential Moving Average)

### Fast vs Slow MA

**Fast MA (short period):**
- **Period: 5-20**
- Follows price closely
- Reacts quickly to changes
- More whipsaws (false signals)

**Slow MA (long period):**
- **Period: 50-200**
- Smooths out noise
- Reacts slowly to changes
- Confirms long-term trend

### Crossover Strategies

**Example: MA Crossover**
```
Fast MA (20) crosses above Slow MA (50) = BUY signal
Fast MA (20) crosses below Slow MA (50) = SELL signal
```

**Common pairs:**
| Fast | Slow | Use Case |
|------|------|----------|
| 10 | 30 | Scalping, intraday |
| 20 | 50 | Swing trading |
| 50 | 200 | Long-term investing (Golden Cross) |

**Optimization:**
- **Closer together** (20/30): More signals, more whipsaws
- **Further apart** (20/50): Fewer signals, more reliable
- **Very far** (50/200): Very few signals, strong trends only

---

## 6. Volatility Parameters

**What it is:** Parameters that measure or adapt to price volatility.

### ATR Period

**What it is:** Average True Range - measures how much an asset moves on average

**How it works:**
- **Short period (7-10)**: Reacts quickly to volatility changes
- **Standard period (14)**: Most common
- **Long period (20-30)**: Smooths out short-term volatility spikes

**Example:**
```
Stock with recent volatility spike:

ATR(7): $5.00  ← Quickly captures spike
ATR(14): $4.20 ← Moderate response
ATR(21): $3.50 ← Slower, smoothed

If using for stop loss:
- ATR(7) × 2 = $10 stop (tighter)
- ATR(14) × 2 = $8.40 stop (standard)
- ATR(21) × 2 = $7 stop (looser)
```

---

## Optimization Strategy Guide

### When to Use Shorter Periods

✅ **Day trading / Scalping**
✅ **High volatility markets** (crypto)
✅ **Mean reversion strategies**
✅ **Want more trading opportunities**

### When to Use Longer Periods

✅ **Swing trading / Position trading**
✅ **Low volatility markets** (bonds, forex)
✅ **Trend following strategies**
✅ **Want fewer, higher-quality signals**

### When to Use Conservative Thresholds

✅ **Choppy/ranging markets**
✅ **High transaction costs**
✅ **Lower risk tolerance**
✅ **Want to avoid false signals**

### When to Use Aggressive Thresholds

✅ **Strong trending markets**
✅ **Low transaction costs**
✅ **Higher risk tolerance**
✅ **Want to catch moves early**

---

## Real-World Optimization Examples

### Example 1: BTC in Bull Market (Trending)

**Problem:** Missing early entries in strong uptrends

**Solution:**
```
RSI Oversold: 30 → 40 (catch rebounds earlier)
RSI Overbought: 70 → 75 (stay in trend longer)
Period: 14 → 10 (faster reaction)
```

### Example 2: Stocks in Ranging Market (Choppy)

**Problem:** Too many false breakouts

**Solution:**
```
Bollinger devfactor: 2.0 → 2.5 (wider bands)
CCI entry: -100 → -150 (more extreme)
Period: 14 → 20 (smoother)
```

### Example 3: High Frequency Trading (Scalping)

**Problem:** Need many quick trades

**Solution:**
```
All periods: Reduce by 30-50%
MA: 50/200 → 10/30
RSI: 14 → 7
Thresholds: More aggressive (50/50 instead of 30/70)
```

---

## Quick Reference Table

| Parameter Type | Lower Value Effect | Higher Value Effect |
|---------------|-------------------|---------------------|
| **Period** | More signals, faster, noisier | Fewer signals, slower, smoother |
| **Oversold Threshold** | Fewer buy signals, stronger | More buy signals, weaker |
| **Overbought Threshold** | More sell signals, weaker | Fewer sell signals, stronger |
| **Multiplier (Bands)** | Tighter bands, more signals | Wider bands, fewer signals |
| **Multiplier (Stops)** | Tighter stops, exit faster | Looser stops, more room |
| **ATR Period** | React quickly to volatility | Smooth volatility changes |

---

## Testing Recommendations

### Start with Standard Values

1. **Test baseline** with default parameters
2. **Identify weakness** (too many/few trades, bad entries, bad exits)
3. **Adjust one parameter** at a time
4. **Compare results** against baseline
5. **Iterate**

### Grid Search Optimization

**Example: Bollinger Bands**
```json
{
  "optimization_params": {
    "period": [15, 20, 25, 30],
    "devfactor": [1.5, 2.0, 2.5]
  }
}
```

**This tests:** 4 × 3 = 12 combinations

**Find the best combination** based on:
- Profit/Loss
- Sharpe Ratio (risk-adjusted returns)
- Max Drawdown (largest loss)
- Number of trades

---

## Common Pitfalls

### ❌ Over-Optimization (Curve Fitting)

**Problem:** Parameters work perfectly on past data but fail in live trading

**Solution:**
- Test on **out-of-sample data**
- Use reasonable ranges (don't test period=3 if it makes no sense)
- **Walk-forward optimization** (test on multiple time periods)

### ❌ Too Many Parameters

**Problem:** Optimizing 10+ parameters = millions of combinations

**Solution:**
- Focus on **2-3 most impactful** parameters first
- Use domain knowledge to narrow ranges
- Keep max 1000 combinations

### ❌ Ignoring Market Regime

**Problem:** Parameters optimized for trending markets fail in ranging markets

**Solution:**
- **Test in different conditions** (bull/bear/sideways)
- Consider **adaptive parameters** that change with volatility
- Use **regime filters** (ADX, volatility measures)

---

## Summary

### Quick Guide to Each Parameter Type

1. **Period Parameters**: Control sensitivity
   - Lower = more sensitive, more trades
   - Higher = less sensitive, fewer trades

2. **Oversold/Overbought**: Control entry/exit timing
   - Extreme values = conservative (fewer signals)
   - Moderate values = aggressive (more signals)

3. **Multipliers**: Control band width or stop distance
   - Lower = tighter, more signals/stops
   - Higher = wider, fewer signals/looser stops

4. **Thresholds**: Control signal triggers
   - Adjust based on indicator range and market volatility

5. **Volatility Parameters**: Adapt to market conditions
   - Shorter = more reactive
   - Longer = more stable

### Optimization Workflow

1. **Understand** what each parameter does
2. **Start** with defaults
3. **Identify** strategy weakness
4. **Optimize** 2-3 key parameters
5. **Validate** on new data
6. **Deploy** and monitor

Happy optimizing! 🚀
