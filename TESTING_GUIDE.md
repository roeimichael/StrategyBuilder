# Testing & Validation Guide

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
# Make sure you're in the project root
cd StrategyBuilder

# Create/activate virtual environment with Python 3.10
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10.x

# Check key packages
python -c "import pandas; print(f'pandas: {pandas.__version__}')"
python -c "import streamlit; print(f'streamlit: {streamlit.__version__}')"
python -c "import backtrader; print('backtrader: OK')"
```

Expected output:
```
Python 3.10.x
pandas: 2.0.3 (or higher)
streamlit: 1.28.0 (or higher)
backtrader: OK
```

## 🧪 Running Tests

### Quick Test (2-3 minutes)

```bash
# Run the comprehensive test suite
python test_system.py
```

This will test:
- ✅ Basic backtest functionality
- ✅ Multiple strategies
- ✅ Trade tracking
- ✅ Visualization components
- ✅ Different time intervals
- ✅ Error handling

### Manual Testing

#### Test 1: CLI Interface

```bash
# Run interactive CLI
python src/main.py
```

Then test:
1. Enter a ticker: `AAPL`
2. Select interval: `2` (1 day)
3. Use default dates (last 365 days)
4. Select strategy: `1` (Bollinger Bands)
5. Use default cash: `$10,000`
6. Skip advanced parameters: `n`

**Expected Result:**
- Should see configuration summary
- Backtest should run and show results
- Display starting/final values, return %, Sharpe ratio

#### Test 2: Streamlit GUI (Recommended)

```bash
# Launch GUI
streamlit run src/app.py
```

**Basic Test Workflow:**

1. **Stock Selection**
   - Source: "Popular Stocks"
   - Category: "Tech Giants"
   - Select: AAPL

2. **Strategy**
   - Select: "Bollinger Bands"

3. **Dates**
   - Start: 90 days ago
   - End: Today

4. **Settings**
   - Capital: $10,000
   - Position size: 100%

5. **Run**
   - Click "🚀 Run Backtest"
   - Wait for progress bar

**Expected Result:**
- ✅ Green success message
- ✅ Metrics displayed (8 total)
- ✅ Interactive candlestick chart with signals
- ✅ Green triangles (▲) for buy signals
- ✅ Red/green triangles (▼) for sell signals
- ✅ Cumulative P&L chart
- ✅ Return distribution histogram
- ✅ Trade details table
- ✅ Download CSV button

#### Test 3: Multiple Stocks

In the GUI:
1. Select "Popular Stocks" → "Tech Giants"
2. Select multiple: AAPL, MSFT, NVDA
3. Run backtest
4. **Expected**: Tabs at top for each stock
5. Click through tabs to see individual results

#### Test 4: Different Strategies

Test each strategy to ensure they all work:
1. Bollinger Bands ✅
2. TEMA + MACD ✅
3. Alligator ✅
4. ADX Adaptive ✅
5. CMF + ATR + MACD ✅
6. TEMA Crossover ✅

## 🐛 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'backtrader'"

**Solution:**
```bash
pip install backtrader
```

### Issue 2: "'tuple' object has no attribute 'lower'"

**Status:** ✅ **FIXED** in latest version

This was caused by date objects being passed instead of strings. Fixed in `src/core/run_strategy.py`.

### Issue 3: Charts not displaying

**Solution:**
```bash
# Make sure plotly and yfinance are installed
pip install --upgrade plotly yfinance
```

### Issue 4: "No data available for [TICKER]"

**Possible causes:**
- Invalid ticker symbol
- Date range too old (no data exists)
- Internet connection issue

**Solution:**
- Verify ticker is valid
- Try a more recent date range
- Check internet connection

### Issue 5: Streamlit won't start

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Reinstall
pip install --upgrade streamlit
```

### Issue 6: Very slow performance

**Normal behavior:**
- First run: Slower (downloading data)
- Subsequent runs: Faster (data cached)
- Multiple stocks: Takes longer
- Hourly/minute intervals: Slower than daily

**Tips:**
- Use daily interval for faster results
- Test with 1 stock first
- Shorter date ranges run faster

## ✅ Validation Checklist

Before considering the system working, verify:

### Core Functionality
- [ ] Dependencies install without errors
- [ ] Python version is 3.10+
- [ ] CLI interface runs
- [ ] GUI launches in browser
- [ ] Single stock backtest completes
- [ ] Multiple stocks work
- [ ] All 6 strategies run without errors

### Visualization
- [ ] Candlestick chart displays
- [ ] Entry signals show (green ▲)
- [ ] Exit signals show (red/green ▼)
- [ ] Volume bars display
- [ ] Cumulative P&L chart shows
- [ ] Distribution histogram displays
- [ ] Trade table displays
- [ ] CSV download works

### Data Accuracy
- [ ] Metrics make sense (no NaN or infinite values)
- [ ] Trade dates are within test period
- [ ] Entry price < exit price for profitable trades
- [ ] Total trades matches table rows
- [ ] Win rate calculation is correct
- [ ] P&L adds up correctly

### Performance
- [ ] 1-stock backtest completes in < 30 seconds
- [ ] 3-stock backtest completes in < 2 minutes
- [ ] GUI responsive (not freezing)
- [ ] Charts render smoothly

## 📊 Expected Results

### Sample Results (AAPL, 90 days, Bollinger Bands)

Typical output should look like:
```
Starting Value:     $10,000.00
Final Value:        $10,500.00
Total Return:       +5.00%
Sharpe Ratio:       0.85
Max Drawdown:       -8.50%
Total Trades:       12
Win Rate:           58.3%
Avg P&L per Trade:  $41.67
```

**Note:** Actual values will vary based on market conditions and date range.

### What's Normal vs. Warning Signs

**Normal:**
- Some strategies have 0 trades (no signals generated)
- Return can be negative (market conditions)
- Sharpe ratio can be negative (poor risk-adjusted returns)
- Different strategies give very different results

**Warning Signs:**
- ❌ All strategies return errors
- ❌ Charts don't display at all
- ❌ Metrics show NaN or infinity
- ❌ Trade table is always empty
- ❌ System crashes repeatedly

## 🚀 Performance Benchmarks

On a typical system:

| Test | Expected Time |
|------|---------------|
| Single stock, 1 day, 90 days | 5-15 seconds |
| Single stock, 1 hour, 30 days | 10-20 seconds |
| 3 stocks, 1 day, 90 days | 15-45 seconds |
| 10 stocks, 1 day, 90 days | 60-180 seconds |

If significantly slower:
- Check internet speed (data download)
- Try shorter date ranges
- Use daily interval instead of hourly

## 📝 Reporting Issues

If tests fail, please provide:
1. Python version (`python --version`)
2. Installed package versions (`pip list | grep -E "pandas|numpy|streamlit|backtrader"`)
3. Full error message
4. Steps to reproduce
5. Test parameters (ticker, dates, strategy)

## 🎯 Ready to Use

If all tests pass:
- ✅ System is fully functional
- ✅ Ready for production use
- ✅ Can start analyzing strategies
- ✅ Can backtest your ideas

**Next steps:** Try backtesting different strategies on various stocks to find what works best!
