# Trading Strategies Guide

Complete guide to all 12 trading strategies available in StrategyBuilder.

---

## Strategy Categories

### 📊 Mean Reversion Strategies
Strategies that buy when prices are "oversold" and sell when "overbought"

### 📈 Trend Following Strategies
Strategies that follow the direction of the market trend

### 💥 Breakout Strategies
Strategies that enter when price breaks through key levels

### 🔀 Multi-Indicator Strategies
Strategies combining multiple technical indicators

---

## All Strategies

### 1. Bollinger Bands (Mean Reversion) 📊

**Description:** Classic mean reversion using Bollinger Bands

**How it works:**
- Entry: Price touches lower band (oversold)
- Exit: Price crosses above middle band

**Parameters:**
- `period` (20): Moving average period
- `devfactor` (2): Standard deviation multiplier

**Best for:** Range-bound markets, stocks that tend to revert to mean

**Grid Search Tip:** Try periods [10, 15, 20, 25, 30] and devfactor [1.5, 2.0, 2.5, 3.0]

---

### 2. TEMA + MACD (Trend Following) 📈

**Description:** Triple EMA crossover with MACD confirmation

**How it works:**
- Entry: TEMA crossover with MACD confirmation
- Exit: Reverse crossover

**Parameters:**
- `macd1` (12): MACD fast period
- `macd2` (26): MACD slow period
- `macdsig` (9): MACD signal period

**Best for:** Trending markets, capturing longer moves

---

### 3. Alligator (Trend Following) 📈

**Description:** Bill Williams Alligator indicator using 3 moving averages

**How it works:**
- Entry: When alligator "wakes up" (MAs diverge)
- Exit: When alligator "sleeps" (MAs converge)

**Parameters:** Fixed periods

**Best for:** Strong trending markets

---

### 4. ADX Adaptive (Multi-Indicator) 🔀

**Description:** Adaptive strategy that switches between trend and range modes

**How it works:**
- Uses ADX to detect trending vs ranging markets
- Trending: MA crossover strategy
- Ranging: Bollinger Band mean reversion

**Parameters:**
- `atrperiod` (14): ATR period
- `atrdist` (2.0): ATR distance multiplier

**Best for:** Markets with changing conditions

---

### 5. CMF + ATR + MACD (Multi-Indicator) 🔀

**Description:** Combines volume (CMF), volatility (ATR), and momentum (MACD)

**How it works:**
- Entry: All three indicators align
- Exit: Any indicator reverses

**Parameters:** MACD and ATR periods

**Best for:** High-conviction trades with multiple confirmations

---

### 6. TEMA Crossover (Trend Following) 📈

**Description:** TEMA 20/60 crossover with volume filter

**How it works:**
- Entry: Fast TEMA crosses above slow TEMA
- Exit: Fast TEMA crosses below slow TEMA

**Parameters:** Fixed periods (20, 60)

**Best for:** Medium-term trends

---

### 7. RSI + Stochastic (Mean Reversion) 📊 ⭐ NEW

**Description:** Dual oscillator oversold/overbought strategy

**How it works:**
- Entry: **Both** RSI < 30 AND Stochastic < 20 (oversold)
- Exit: **Either** RSI > 70 OR Stochastic > 80 (overbought)

**Parameters:**
- `rsi_period` (14): RSI period
- `rsi_oversold` (30): RSI oversold level
- `rsi_overbought` (70): RSI overbought level
- `stoch_period` (14): Stochastic period
- `stoch_oversold` (20): Stochastic oversold level
- `stoch_overbought` (80): Stochastic overbought level

**Best for:** Range-bound stocks, requires strong confirmation

**Why it's good:** Combining two oscillators reduces false signals

---

### 8. Williams %R (Mean Reversion) 📊 ⭐ NEW

**Description:** Mean reversion using Williams %R momentum indicator

**How it works:**
- Entry: Williams %R < -80 (oversold)
- Exit: Williams %R > -20 (overbought)

**Parameters:**
- `period` (14): Lookback period
- `oversold` (-80): Oversold threshold
- `overbought` (-20): Overbought threshold

**Best for:** Short-term mean reversion, fast-moving stocks

**Why it's good:** More sensitive than RSI, catches quick reversals

---

### 9. MFI - Money Flow Index (Mean Reversion) 📊 ⭐ NEW

**Description:** Volume-weighted RSI for price/volume divergence detection

**How it works:**
- Entry: MFI < 20 (strong selling pressure with volume)
- Exit: MFI > 80 (strong buying pressure with volume)

**Parameters:**
- `period` (14): MFI calculation period
- `oversold` (20): Oversold threshold
- `overbought` (80): Overbought threshold

**Best for:** Stocks with significant volume, detecting capitulation

**Why it's good:** Incorporates volume, more reliable than price-only indicators

---

### 10. CCI + ATR (Breakout) 💥 ⭐ NEW

**Description:** Volatility breakout using CCI (Commodity Channel Index) and ATR

**How it works:**
- Entry: CCI crosses above -100 (trend reversal) AND ATR rising (volatility)
- Exit: CCI crosses below +100 (trend weakening)

**Parameters:**
- `cci_period` (20): CCI calculation period
- `cci_entry` (-100): Entry trigger level
- `cci_exit` (+100): Exit trigger level
- `atr_period` (14): ATR period

**Best for:** Catching breakouts with increasing volatility

**Why it's good:** ATR filter ensures you only trade when volatility is expanding

---

### 11. Momentum Multi (Multi-Indicator) 🔀 ⭐ NEW

**Description:** Multi-indicator momentum combining ROC + RSI + OBV

**How it works:**
- Entry: ROC > 2% (momentum) AND RSI 40-60 (neutral) AND OBV rising (volume)
- Exit: ROC < 0 (momentum fades) OR RSI > 70 (overbought)

**Parameters:**
- `roc_period` (12): Rate of Change period
- `roc_threshold` (2.0): Minimum ROC % for entry
- `rsi_period` (14): RSI period
- `rsi_min` (40): Minimum RSI for entry
- `rsi_max` (60): Maximum RSI for entry
- `rsi_exit` (70): RSI exit threshold

**Best for:** Strong momentum moves, catching trends early

**Why it's good:** Multiple confirmations (price momentum, not overbought, volume support)

---

### 12. Keltner Channel (Breakout) 💥 ⭐ NEW

**Description:** Dynamic channel breakout using EMA and ATR

**How it works:**
- Entry: Price breaks above upper Keltner Channel (EMA + ATR*multiplier)
- Exit: Price crosses back below middle line (EMA)

**Parameters:**
- `ema_period` (20): EMA period for middle line
- `atr_period` (10): ATR period for channel width
- `atr_multiplier` (2.0): ATR multiplier for band distance

**Best for:** Trending breakouts, riding strong moves

**Why it's good:** Dynamic channels adapt to volatility

---

## Strategy Selection Guide

### For Different Market Conditions

**Trending Markets:**
- TEMA + MACD
- Alligator
- TEMA Crossover
- Keltner Channel

**Range-Bound Markets:**
- Bollinger Bands
- RSI + Stochastic
- Williams %R
- MFI (Money Flow)

**Volatile Markets:**
- CCI + ATR
- Keltner Channel
- ADX Adaptive

**Uncertain Markets (need confirmation):**
- RSI + Stochastic (requires both)
- CMF + ATR + MACD (requires all three)
- Momentum Multi (requires all three)

### For Different Trading Styles

**Day Trading (quick in/out):**
- Williams %R
- RSI + Stochastic
- MFI (Money Flow)

**Swing Trading (multi-day holds):**
- Bollinger Bands
- TEMA + MACD
- Keltner Channel

**Position Trading (weeks to months):**
- Alligator
- TEMA Crossover
- ADX Adaptive

### For Different Risk Levels

**Conservative (high confirmation):**
- RSI + Stochastic (requires both oversold)
- CMF + ATR + MACD (requires all three)
- Momentum Multi (requires all three)

**Moderate:**
- Bollinger Bands
- MFI (Money Flow)
- CCI + ATR

**Aggressive (fast signals):**
- Williams %R
- Keltner Channel
- Momentum Multi

---

## Using Strategies in StrategyBuilder

### 1. Backtest Tab
- Select any strategy from dropdown
- Configure parameters if available
- Run backtest to see performance

### 2. Grid Search Tab
- Select strategy to optimize
- Define parameter ranges
- Find optimal settings automatically

### 3. Live Trading Tab
- Add successful backtests to monitoring
- Get daily signals for your strategies

---

## Grid Search Recommendations

### Bollinger Bands
```
period: [10, 15, 20, 25, 30]
devfactor: [1.5, 2.0, 2.5, 3.0]
→ 20 combinations
```

### RSI + Stochastic
```
rsi_oversold: [25, 30, 35]
stoch_oversold: [15, 20, 25]
→ 9 combinations
```

### Williams %R
```
period: [10, 14, 20]
oversold: [-85, -80, -75]
→ 9 combinations
```

### MFI (Money Flow)
```
period: [10, 14, 20]
oversold: [15, 20, 25]
→ 9 combinations
```

### CCI + ATR
```
cci_period: [15, 20, 25]
atr_period: [10, 14, 20]
→ 9 combinations
```

### Keltner Channel
```
ema_period: [15, 20, 25]
atr_multiplier: [1.5, 2.0, 2.5, 3.0]
→ 12 combinations
```

---

## Tips for Success

### 1. Test Before You Trade
- Always backtest on historical data first
- Test on different time periods
- Test on different stocks

### 2. Use Grid Search
- Find optimal parameters for each stock
- Don't assume default settings are best
- Each stock behaves differently

### 3. Combine with Risk Management
- These strategies show when to enter/exit
- YOU must decide position size
- YOU must set stop losses
- Never risk more than 1-2% per trade

### 4. Monitor Performance
- Add successful configs to live monitoring
- Review signals regularly
- Adjust parameters as market conditions change

### 5. Diversify Strategies
- Don't rely on one strategy
- Different strategies work in different conditions
- Monitor multiple strategies on multiple stocks

---

## Common Questions

**Q: Which strategy is best?**
A: There's no "best" strategy. Different strategies work better in different market conditions. Use Grid Search to find what works best for each stock.

**Q: Can I use multiple strategies on the same stock?**
A: Yes! Add the same stock multiple times with different strategies. This gives you multiple perspectives.

**Q: Why do parameters matter so much?**
A: Parameters determine when the strategy triggers. A Bollinger Band with period=10 is very different from period=30.

**Q: Should I use the new strategies or stick with the original ones?**
A: Try both! The new strategies offer different approaches. RSI + Stochastic is great for range-bound markets, while Keltner Channel excels at breakouts.

**Q: How often should I adjust my strategies?**
A: Re-run backtests quarterly or when market conditions change significantly. Grid search when you notice performance degrading.

---

## Next Steps

1. **Try them all** - Run quick backtests on each strategy
2. **Grid search the top 3** - Optimize parameters
3. **Add to monitoring** - Track the best configs
4. **Review weekly** - Check signal performance
5. **Adjust as needed** - Markets change, strategies adapt

Happy Trading! 📈
