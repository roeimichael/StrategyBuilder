# Bug Fix: yfinance 0.2.31+ MultiIndex Columns

## Problem Summary

When running backtests, you encountered this error:
```
AttributeError: 'tuple' object has no attribute 'lower'
```

### Root Cause

**yfinance 0.2.31+** changed how it returns data. Instead of returning DataFrames with simple column names like:
```python
['Open', 'High', 'Low', 'Close', 'Volume']
```

It now returns DataFrames with **MultiIndex columns** (tuples) like:
```python
[('Open', 'AAPL'), ('High', 'AAPL'), ('Low', 'AAPL'), ...]
```

**backtrader** (the backtesting engine) expects simple string column names and tries to call `.lower()` on them:
```python
colnames = [x.lower() for x in dataframe.columns.values]
```

This fails because `.lower()` doesn't exist on tuples, causing the error.

## The Fix

Modified `src/core/run_strategy.py` (lines 47-55) to flatten MultiIndex columns before passing data to backtrader:

```python
# Fix for yfinance 0.2.31+ which returns MultiIndex columns
# Flatten MultiIndex columns to simple string names for backtrader compatibility
import pandas as pd
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# Ensure all column names are strings (handle any remaining tuples)
if len(data.columns) > 0 and isinstance(data.columns[0], tuple):
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
```

This converts:
- `('Open', 'AAPL')` → `'Open'`
- `('High', 'AAPL')` → `'High'`
- etc.

## Installation Instructions

### Option 1: Clean Install (Recommended for Windows)

```bash
# Delete old virtual environment
rm -rf venv  # Windows: rmdir /s venv

# Create fresh virtual environment with Python 3.10
python3.10 -m venv venv
# Or on Windows with just 'python' if 3.10 is your default:
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Option 2: If Installation Fails

Some packages (like `ta`, `empyrical`) may fail to install due to setuptools compatibility issues. You can install just the core dependencies:

```bash
# Install core packages only
pip install backtrader yfinance pandas numpy matplotlib plotly streamlit

# Try installing other packages individually
pip install PyYAML python-dotenv requests lxml
```

**Note:** If `multitasking` fails to build (a dependency of yfinance), you can try:
```bash
# Use an older version of yfinance that has fewer dependencies
pip install 'yfinance>=0.2.31,<0.2.40'
```

Or update your setuptools:
```bash
pip install --upgrade setuptools pip wheel
```

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10.x

# Test core imports
python -c "import backtrader; print(f'backtrader: {backtrader.__version__}')"
python -c "import yfinance as yf; print(f'yfinance: {yf.__version__}')"
python -c "import pandas as pd; print(f'pandas: {pd.__version__}')"
python -c "import numpy as np; print(f'numpy: {np.__version__}')"
python -c "import streamlit; print(f'streamlit: {streamlit.__version__}')"
```

Expected versions:
- backtrader: 1.9.76.123 or higher
- yfinance: 0.2.31 or higher
- pandas: 2.0.3 or higher
- numpy: 1.24.3 or higher
- streamlit: 1.28.0 or higher

## Testing the Fix

### Quick Test (Verify Fix Works)

```bash
python test_multiindex_fix.py
```

Expected output:
```
Original DataFrame columns (MultiIndex):
  Type: <class 'pandas.core.indexes.multi.MultiIndex'>
  Columns: [('Open', 'AAPL'), ('High', 'AAPL'), ...]
  Is MultiIndex: True

✓ Applied MultiIndex flattening

Fixed DataFrame columns:
  Type: <class 'pandas.core.indexes.base.Index'>
  Columns: ['Open', 'High', 'Low', 'Close', 'Volume']
  Is MultiIndex: False

✅ SUCCESS: Column names can be lowercased: ['open', 'high', 'low', 'close', 'volume']

The MultiIndex fix is working correctly!
```

### Comprehensive System Test

```bash
python test_system.py
```

This runs 6 comprehensive test categories:
1. Basic backtest (Bollinger Bands on AAPL)
2. Multiple strategies (MSFT with 3 different strategies)
3. Trade tracking (TSLA with 180-day history)
4. Visualization components (NVDA with charts)
5. Different time intervals (hourly and daily)
6. Edge cases and error handling

Expected result: All 6 tests should pass (may take 2-5 minutes).

### Manual Testing

#### Test the CLI:
```bash
python src/main.py
```

Follow the prompts:
1. Ticker: `AAPL`
2. Interval: `2` (1 day)
3. Dates: Use defaults (last 365 days)
4. Strategy: `1` (Bollinger Bands)
5. Cash: `10000`
6. Advanced params: `n`

#### Test the GUI:
```bash
streamlit run src/app.py
```

Then in your browser:
1. Select "Popular Stocks" → "Tech Giants" → AAPL
2. Choose "Bollinger Bands" strategy
3. Select date range (e.g., last 90 days)
4. Click "🚀 Run Backtest"

Expected results:
- ✅ Green success message
- ✅ 8 metrics displayed (return %, Sharpe ratio, etc.)
- ✅ Interactive candlestick chart with buy/sell signals
- ✅ Trade details table
- ✅ Download CSV button

## Technical Details

### What Changed in yfinance 0.2.31+

When you download data for a single ticker:
```python
data = yf.download('AAPL', start='2024-01-01', interval='1d')
```

**Old behavior (yfinance < 0.2.31):**
```python
data.columns = Index(['Open', 'High', 'Low', 'Close', 'Volume'])
```

**New behavior (yfinance >= 0.2.31):**
```python
data.columns = MultiIndex([('Open', 'AAPL'), ('High', 'AAPL'), ...])
```

This change was likely made to support multi-ticker downloads more consistently, but it breaks compatibility with backtrader.

### Why backtrader Breaks

In `backtrader/feeds/pandafeed.py` line 212:
```python
colnames = [x.lower() for x in self.p.dataname.columns.values]
```

When `x` is a tuple like `('Open', 'AAPL')`, calling `x.lower()` raises:
```
AttributeError: 'tuple' object has no attribute 'lower'
```

### Our Solution

We intercept the data after yfinance downloads it but before passing it to backtrader, and flatten the MultiIndex to simple strings. This is transparent to both libraries and maintains full compatibility.

## Troubleshooting

### Issue: Still getting the error after pulling changes

**Solution:**
```bash
# Make sure you pulled the latest changes
git pull origin claude/backtest-stock-strategies-011CV5v8NpyM6eENovPnBqhZ

# Verify the fix is present in run_strategy.py
grep -A 5 "Fix for yfinance" src/core/run_strategy.py

# Restart your Python environment
# If using Jupyter: Kernel → Restart
# If using IDE: Close and reopen
# If using CLI: Exit and restart
```

### Issue: "ModuleNotFoundError: No module named 'backtrader'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall dependencies
pip install backtrader
```

### Issue: Charts not displaying in GUI

**Solution:**
```bash
# Install visualization dependencies
pip install plotly matplotlib

# Clear streamlit cache
streamlit cache clear

# Restart streamlit
streamlit run src/app.py
```

### Issue: "No data available for [TICKER]"

**Possible causes:**
- Invalid ticker symbol
- Date range too far in the past
- Network/internet connection issue
- Yahoo Finance API temporarily unavailable

**Solution:**
```bash
# Test if yfinance is working
python -c "import yfinance as yf; data = yf.download('AAPL', period='5d'); print(data.head())"

# If that works but the app doesn't, check your date range
# Try using a more recent date range (e.g., last 30-90 days)
```

## Summary

✅ **Fixed:** yfinance 0.2.31+ MultiIndex columns compatibility
✅ **Tested:** Verified fix works with MultiIndex test script
✅ **Committed:** Changes pushed to repository
✅ **Ready:** System ready for testing on your local machine

**Next steps:**
1. Pull the latest changes
2. Install dependencies (see installation instructions above)
3. Run `test_multiindex_fix.py` to verify the fix
4. Run `test_system.py` for comprehensive testing
5. Test the GUI with `streamlit run src/app.py`

All tests should now pass! 🎉
