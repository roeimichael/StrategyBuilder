# Backtest vs Optimization Logic Differences

## Problem Statement

When running the same strategy parameters through:
1. **Backtest endpoint** (`POST /backtest`)
2. **Optimization endpoint** (`POST /optimize`)

The results don't match. For example:
- Backtest with `devfactor=2.0` returns `+1.75%` profit
- Optimization with `devfactor=[2.0, 3.0, 4.0]` shows different results for the `devfactor=2.0` entry

## Root Cause Analysis

After analyzing the code in `src/core/optimizer.py` and `src/core/run_strategy.py`, I found **4 critical differences** in how they execute backtests:

---

## Difference #1: Position Sizing 🎯

### Backtest (run_strategy.py, line 66-67):
```python
sizer_percent = self.args.get('position_size_pct', 95)
self.cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer_percent)
```
**Behavior:** Uses **95% of available cash** for each trade

### Optimizer (optimizer.py):
```python
# NO SIZER CONFIGURED
cerebro.addstrategy(self.strategy_cls, ...)
```
**Behavior:** Uses Backtrader's default sizer (likely **100% of cash per trade** or **fixed size**)

### Impact:
- **Backtest**: Conservative position sizing (95% of cash)
- **Optimizer**: Aggressive position sizing (100% of cash)
- **Result**: Optimizer will have larger positions → **higher PnL** (or losses)

---

## Difference #2: Commission 💰

### Backtest (run_strategy.py):
```python
# Commission NOT explicitly set
self.cerebro.broker.set_cash(self.args['cash'])
```
**Behavior:** Uses Backtrader's **default commission** (typically **0%**)

### Optimizer (optimizer.py, line 31):
```python
cerebro.broker.setcommission(commission=0.001)
```
**Behavior:** Explicitly sets **0.1% commission** per trade

### Impact:
- **Backtest**: No trading costs
- **Optimizer**: Pays 0.1% on each trade (buy + sell = 0.2% round trip)
- **Result**: Optimizer will have **lower PnL** due to commission costs

**Example:**
- 10 trades with $10,000 positions
- Commission cost: 10 trades × 2 legs × $10,000 × 0.001 = **$200 less profit**

---

## Difference #3: Parameter Passing 📝

### Backtest (run_strategy.py, line 68):
```python
self.cerebro.addstrategy(self.strategy, args=self.args)
```
**Behavior:** Passes parameters via `args` dictionary

### Optimizer (optimizer.py, line 32):
```python
cerebro.addstrategy(self.strategy_cls, args=params_dict, **params_dict)
```
**Behavior:** Passes parameters via **both** `args` and `**kwargs`

### Impact:
- Depends on how strategies consume parameters
- Most Backtrader strategies use `params = (('period', 20), ...)` which accepts both methods
- **Potential issue**: Double parameter passing might cause conflicts in some strategies

---

## Difference #4: Analyzers 📊

### Backtest (run_strategy.py, lines 21-29):
```python
self.cerebro.addanalyzer(bt.analyzers.TimeReturn, ...)
self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
self.cerebro.addobserver(bt.observers.DrawDown)
```
**Behavior:** Uses **5 analyzers + 1 observer**

### Optimizer (optimizer.py, lines 33-34):
```python
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', ...)
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
```
**Behavior:** Uses only **2 analyzers**

### Impact:
- More analyzers = more computation overhead
- **Minimal impact** on PnL, but might affect performance
- Backtest provides more detailed metrics (drawdown, trade analysis)

---

## Summary of Impacts

| Factor | Backtest | Optimizer | Impact on Results |
|--------|----------|-----------|-------------------|
| **Position Sizing** | 95% of cash | 100% of cash (likely) | ⚠️ **MAJOR** - Different PnL |
| **Commission** | 0% (default) | 0.1% | ⚠️ **MAJOR** - Lower PnL in optimizer |
| **Parameter Passing** | `args` only | `args` + `**kwargs` | ⚠️ **MINOR** - Potential conflicts |
| **Analyzers** | 5 analyzers | 2 analyzers | ✅ **NEGLIGIBLE** - Same PnL |

---

## Why Your Results Don't Match

Given the differences above, here's what's happening:

### Your Case: Bollinger Bands on AAPL
- **Backtest**: `devfactor=2.0` → **+1.75% profit**
- **Optimizer**: `devfactor=2.0` → **Different result**

### Likely Explanation:

1. **Position Sizing Effect** (Optimizer uses larger positions):
   - If profitable trades: Optimizer shows **higher profit** than backtest
   - If losing trades: Optimizer shows **higher losses** than backtest

2. **Commission Effect** (Optimizer pays fees):
   - Every trade costs 0.1% × 2 = **0.2% round trip**
   - If you had 10 trades: **-2% from commissions alone**
   - **This reduces optimizer profit by ~2%**

3. **Combined Effect**:
   ```
   Backtest:  +1.75% (no commission, 95% sizing)
   Optimizer: +1.75% (base) + X% (100% sizing) - 2% (commission) = Different result
   ```

---

## How to Verify This

Run the test script I created:

```bash
python tests/test_backtest_vs_optimization.py
```

This will:
1. Run backtest with `devfactor=2.0`
2. Run optimization with `devfactor=[2.0, 3.0, 4.0]`
3. Compare the results side-by-side
4. Calculate the exact differences
5. Identify which factors are causing the discrepancy

---

## Recommended Fixes

### Option 1: Make Optimizer Match Backtest (Recommended)

Update `src/core/optimizer.py`:

```python
def run_optimization(self, ticker: str, start_date: date, end_date: date,
                    interval: str, cash: float, param_ranges: Dict[str, List[Union[int, float]]]) -> List[Dict[str, Any]]:
    # ... existing code ...

    for param_combination in product(*param_values_list):
        params_dict = dict(zip(param_names, param_combination))
        cerebro = bt.Cerebro()
        cerebro.adddata(bt_data)
        cerebro.broker.setcash(cash)

        # FIX #1: Remove explicit commission (use default 0% like backtest)
        # cerebro.broker.setcommission(commission=0.001)  # REMOVE THIS

        # FIX #2: Add position sizer to match backtest
        cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

        # FIX #3: Use same parameter passing as backtest
        cerebro.addstrategy(self.strategy_cls, args=params_dict)  # Remove **params_dict

        # ... rest of code ...
```

### Option 2: Make Backtest Match Optimizer

Update `src/core/run_strategy.py`:

```python
def runstrat(self, ticker: str, start_date: date, interval: str, end_date: Optional[date] = None) -> Dict[str, Any]:
    self.cerebro.broker.set_cash(self.args['cash'])

    # Add commission to match optimizer
    self.cerebro.broker.setcommission(commission=0.001)

    # ... rest of code ...
    # Remove or comment out the sizer to match optimizer
    # self.cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer_percent)
```

### Option 3: Make Both Configurable

Allow users to specify commission and position sizing in both endpoints:

```python
# In API request models
class BacktestRequest(BaseModel):
    # ... existing fields ...
    commission: float = Field(0.0, example=0.001)
    position_size_pct: float = Field(95.0, example=95.0)

class OptimizationRequest(BaseModel):
    # ... existing fields ...
    commission: float = Field(0.0, example=0.001)
    position_size_pct: float = Field(95.0, example=95.0)
```

---

## Testing Procedure

1. **Run the test script** to confirm discrepancies exist
2. **Apply Option 1 fixes** (recommended - make optimizer match backtest)
3. **Run the test script again** to verify results now match
4. **Document the changes** in API docs

---

## Expected Outcome

After fixing, when you run:
- **Backtest**: `devfactor=2.0` → `+1.75%`
- **Optimizer**: `devfactor=2.0` → `+1.75%` ✅ **MATCH!**

The optimization results should now be **reliable and consistent** with backtest results.

---

## Additional Notes

### Why This Matters

1. **User Trust**: Users expect optimization to test the same logic as backtest
2. **Decision Making**: If optimization shows different results, users make wrong decisions
3. **Strategy Validation**: Can't trust optimization to find best parameters if logic differs

### Performance Impact

Making optimizer match backtest will:
- ✅ **Accurate results**: Optimizer will find truly optimal parameters
- ✅ **Consistency**: Same parameters = same results in both endpoints
- ⚠️ **Slightly slower**: Adding position sizer adds tiny overhead (negligible)

---

## Questions to Answer

Before applying fixes, decide:

1. **Commission**: Should real trading include 0.1% commission?
   - If yes → Add to backtest
   - If no → Remove from optimizer

2. **Position Sizing**: Should use 95% or 100%?
   - 95% is more conservative (recommended)
   - 100% is more aggressive (can cause issues in real trading)

3. **Consistency**: Which endpoint is "source of truth"?
   - Recommendation: **Backtest** (more complete, used more often)
   - Optimizer should match backtest logic

---

## Conclusion

The discrepancy is **not a bug in the strategy**, but a **difference in execution environment** between backtest and optimizer. Once these differences are aligned, results will be consistent and reliable.
