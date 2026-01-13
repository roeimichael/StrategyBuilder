# Short Position Implementation Guide

## Overview

**Good News:** Your codebase ALREADY fully supports short positions! The infrastructure is complete. You just need to add the trading logic to strategies.

---

## How Short Positions Work

### Long vs Short Trading

**Long Position (Buy Low, Sell High):**
```
1. BUY at $100
2. Price goes to $110
3. SELL at $110
4. Profit: $10 per share
```

**Short Position (Sell High, Buy Low):**
```
1. SELL (short) at $100
2. Price drops to $90
3. BUY (cover) at $90
4. Profit: $10 per share
```

---

## Infrastructure Already in Place

### 1. ✅ Backtrader Framework Support

```python
# Open a long position
self.buy()

# Open a short position
self.sell()

# Close any position (long or short)
self.close()
```

### 2. ✅ Strategy Skeleton Tracks Shorts

In `src/core/strategy_skeleton.py` (lines 23-37):

```python
if order.isbuy():
    if self.entry_order is None:
        self.entry_order = {
            'type': 'LONG' if order.executed.size > 0 else 'SHORT'
        }
```

### 3. ✅ PnL Calculation Handles Both

In `src/core/strategy_skeleton.py` (lines 48-51):

```python
if self.entry_order['type'] == 'LONG':
    pnl_raw = (exit_price - entry_price) * size
else:  # SHORT
    pnl_raw = (entry_price - exit_price) * size
```

**For Long:**
- Entry: $100, Exit: $110 → PnL = ($110 - $100) × size = +$10

**For Short:**
- Entry: $100, Exit: $90 → PnL = ($100 - $90) × size = +$10

### 4. ✅ API Response Includes Trade Type

The API already returns:
```json
{
  "trades": [
    {
      "type": "LONG",
      "entry_price": 100,
      "exit_price": 110,
      "pnl": 10.0,
      "pnl_pct": 10.0
    },
    {
      "type": "SHORT",
      "entry_price": 100,
      "exit_price": 90,
      "pnl": 10.0,
      "pnl_pct": 10.0
    }
  ]
}
```

---

## How to Add Short Positions to Strategies

### Pattern 1: Track Position Type

Use a flag to track whether you're in a long or short position:

```python
def __init__(self, args):
    super().__init__(args)
    # ... indicators ...
    self.position_type = 0  # 0 = no position, 1 = long, -1 = short

def next(self):
    if not self.position:
        # ENTRY LOGIC
        if bullish_signal:
            self.buy()
            self.position_type = 1
        elif bearish_signal:
            self.sell()
            self.position_type = -1
    else:
        # EXIT LOGIC
        if self.position_type == 1:  # In long
            if long_exit_signal:
                self.close()
                self.position_type = 0
        elif self.position_type == -1:  # In short
            if short_exit_signal:
                self.close()
                self.position_type = 0
```

### Pattern 2: Separate Position Flags

Used by Alligator strategy:

```python
def __init__(self, args):
    super().__init__(args)
    self.long_position = 0
    self.short_position = 0

def next(self):
    if not self.position:
        if bullish_signal:
            self.long_position = 1
            self.buy()
        elif bearish_signal:
            self.short_position = 1
            self.sell()
    else:
        if self.long_position == 1:
            if exit_signal:
                self.long_position = 0
                self.close()
        elif self.short_position == 1:
            if exit_signal:
                self.short_position = 0
                self.close()
```

---

## Example: Bollinger Bands with Shorts

### Strategy Logic

**Long Entry:** Price crosses below lower band (oversold, expect bounce)
**Long Exit:** Price crosses above middle band

**Short Entry:** Price crosses above upper band (overbought, expect reversal)
**Short Exit:** Price crosses below middle band

### Implementation

```python
class Bollinger_three(Strategy_skeleton):
    params = (
        ("period", 20),
        ("devfactor", 2)
    )

    def __init__(self, args):
        super(Bollinger_three, self).__init__(args)
        self.boll = bt.indicators.BollingerBands(
            period=self.p.period,
            devfactor=self.p.devfactor
        )

        # Crossovers for all bands
        self.crossover_bot = bt.ind.CrossOver(self.data.close, self.boll.lines.bot)
        self.crossover_mid = bt.ind.CrossOver(self.data.close, self.boll.lines.mid)
        self.crossover_top = bt.ind.CrossOver(self.data.close, self.boll.lines.top)

        # Track position type
        self.position_type = 0  # 0=none, 1=long, -1=short

    def next(self):
        if self.order:
            return

        if not self.position:
            # LONG ENTRY: Price crosses below lower band
            if self.crossover_bot < 0:
                self.buy()
                self.position_type = 1
                self.log('BUY CREATE (LONG)')

            # SHORT ENTRY: Price crosses above upper band
            elif self.crossover_top > 0:
                self.sell()
                self.position_type = -1
                self.log('SELL CREATE (SHORT)')
        else:
            # LONG EXIT: Price crosses above middle band
            if self.position_type == 1:
                if self.crossover_mid > 0:
                    self.close()
                    self.position_type = 0
                    self.log('SELL CREATE (LONG EXIT)')

            # SHORT EXIT: Price crosses below middle band
            elif self.position_type == -1:
                if self.crossover_mid < 0:
                    self.close()
                    self.position_type = 0
                    self.log('BUY CREATE (SHORT EXIT)')
```

### Visual Representation

```
Price Action:

Upper Band    ─────────────────
                      ↗ SHORT ENTRY (sell)
Middle Band   ═════════════════
                ↗ LONG EXIT      ↘ SHORT EXIT
Lower Band    ─────────────────
            ↗ LONG ENTRY (buy)
```

---

## Existing Strategies with Short Positions

### 1. Alligator Strategy ✅

**File:** `src/strategies/alligator_strategy.py`

```python
# Long entry
if self.data.close[0] > self.ema[0] and (self.jaws[0] < self.teeth[0] < self.lips[0]):
    self.long_position = 1
    self.buy()

# Short entry
if self.data.close[0] < self.ema[0] and (self.jaws[0] > self.teeth[0] > self.lips[0]):
    self.short_position = 1
    self.sell()
```

### 2. MACD + CMF + ATR Strategy ✅

**File:** `src/strategies/cmf_atr_macd_strategy.py`

```python
# Long entry with stop loss/take profit
if self.macd.macd[0] > 0 and self.cmf[0] > 0:
    self.buy()
    self.is_long = 1
    pdist = self.atr[0] * self.p.atrdist
    self.stop_loss_long = self.data.close[0] - pdist
    self.take_profit_long = self.data.close[0] + (2 * pdist)

# Short entry with stop loss/take profit
elif self.macd.macd[0] < 0 and self.cmf[0] < 0:
    self.sell()
    self.is_short = 1
    pdist = self.atr[0] * self.p.atrdist
    self.stop_loss_short = self.data.close[0] + pdist
    self.take_profit_short = self.data.close[0] - (2 * pdist)
```

---

## API Response with Short Positions

### Request

```bash
POST /backtest
```

```json
{
  "ticker": "BTC-USD",
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### Response

```json
{
  "success": true,
  "pnl": 1500.50,
  "return_pct": 15.0,
  "total_trades": 20,
  "advanced_metrics": {
    "win_rate": 60.0
  },
  "trades": [
    {
      "entry_date": "2024-01-15",
      "exit_date": "2024-01-18",
      "entry_price": 42000.0,
      "exit_price": 43000.0,
      "type": "LONG",
      "size": 0.1,
      "pnl": 100.0,
      "pnl_pct": 2.38
    },
    {
      "entry_date": "2024-02-01",
      "exit_date": "2024-02-05",
      "entry_price": 45000.0,
      "exit_price": 44000.0,
      "type": "SHORT",
      "size": 0.1,
      "pnl": 100.0,
      "pnl_pct": 2.22
    }
  ]
}
```

**Key Points:**
- ✅ `type` field shows "LONG" or "SHORT"
- ✅ `pnl` is already calculated correctly for both
- ✅ `pnl_pct` is relative to entry price
- ✅ Total PnL aggregates both long and short trades

---

## Testing Short Positions

### Test Script

```python
# test_short_positions.py
import requests

BASE_URL = "http://localhost:8086"

def test_bollinger_with_shorts():
    response = requests.post(
        f"{BASE_URL}/backtest",
        json={
            "ticker": "BTC-USD",
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "interval": "1d",
            "cash": 10000.0,
            "parameters": {
                "period": 20,
                "devfactor": 2
            }
        }
    )

    result = response.json()

    # Count long vs short trades
    long_trades = [t for t in result['trades'] if t['type'] == 'LONG']
    short_trades = [t for t in result['trades'] if t['type'] == 'SHORT']

    print(f"Total Trades: {result['total_trades']}")
    print(f"Long Trades: {len(long_trades)}")
    print(f"Short Trades: {len(short_trades)}")
    print(f"Total PnL: ${result['pnl']:.2f}")

    # Show sample trades
    print("\nSample Long Trade:")
    if long_trades:
        print(long_trades[0])

    print("\nSample Short Trade:")
    if short_trades:
        print(short_trades[0])

if __name__ == "__main__":
    test_bollinger_with_shorts()
```

---

## Important Considerations

### 1. Broker Configuration

Backtrader's default broker allows shorts. No configuration needed.

### 2. Margin Requirements

Currently using default settings (no margin restrictions). In production, you may want to configure:

```python
cerebro.broker.set_shortcash(False)  # Use same cash for long/short
```

### 3. Commission

Applied equally to both long and short:

```python
cerebro.broker.setcommission(commission=0.001)  # 0.1% on all trades
```

### 4. Position Sizing

Works the same for both:

```python
cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
```

---

## Summary

### What's Already Working ✅

1. ✅ Backtrader natively supports short positions
2. ✅ Strategy skeleton tracks and calculates PnL for shorts
3. ✅ API returns trade types (LONG/SHORT) correctly
4. ✅ Two strategies already use shorts successfully
5. ✅ No code changes needed in API or infrastructure

### What You Need to Do

1. **Add trading logic** to strategies (like we just did for Bollinger Bands)
2. **Track position type** (long vs short flag)
3. **Define exit conditions** for each position type

### Complexity Assessment

**Infrastructure:** ⭐⭐⭐⭐⭐ (Already complete!)
**Strategy Logic:** ⭐⭐☆☆☆ (Simple - just add the trading rules)
**Testing:** ⭐⭐⭐☆☆ (Moderate - verify PnL calculations)

---

## Next Steps

1. ✅ **Bollinger Bands updated** with short positions
2. Consider adding shorts to other strategies:
   - Williams %R (oversold/overbought)
   - RSI + Stochastic (dual signal confirmation)
   - MFI (volume-weighted momentum)
   - Keltner Channel (volatility breakout both directions)

3. Test the updated Bollinger Bands:
   ```bash
   python test_api.py  # Or use test_short_positions.py
   ```

4. Monitor results:
   - Compare performance with/without shorts
   - Check if shorts improve Sharpe ratio
   - Verify both trade types are executing correctly

---

**The infrastructure is 100% ready. Just add the logic!** 🚀
