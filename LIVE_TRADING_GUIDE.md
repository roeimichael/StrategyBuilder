# Live Trading & Monitoring Guide

## Overview

The Live Trading feature allows you to monitor stocks using your tested strategies and receive trading signals automatically. This is perfect for tracking strategies that performed well in backtesting and applying them to live market data.

## Features

✅ **Save Backtest Configurations** - Store successful backtests in a database
✅ **Active Monitoring** - Track multiple stocks with different strategies
✅ **Trading Signals** - Automatically detect buy/sell signals
✅ **Historical View** - Review all past backtests and their performance
✅ **Daily Automation** - Run monitoring script via scheduler

---

## Getting Started

### 1. Run a Backtest

1. Open the Streamlit GUI:
   ```bash
   streamlit run src/app.py
   ```

2. Go to the **"📊 Backtest"** tab

3. Configure and run your backtest:
   - Select ticker(s)
   - Choose strategy
   - Set date range
   - Run backtest

### 2. Save Backtest to Database

After a successful backtest:

1. Click **"💾 Save to Database"** button
   - Stores all backtest results
   - Saves strategy configuration
   - Records performance metrics

2. OR click **"📡 Add to Live Monitoring"** directly
   - Automatically saves to database
   - Adds stock to active monitoring list

### 3. Manage Monitored Stocks

Go to the **"🔴 Live Trading"** tab:

#### Subtab 1: 📊 Backtest History
- View all saved backtests
- Filter by ticker or strategy
- See detailed performance metrics
- Add successful strategies to monitoring

#### Subtab 2: 📡 Active Monitoring
- See all monitored stocks
- View configuration for each
- Remove stocks from monitoring
- Check last monitoring time

#### Subtab 3: 📈 Signals & Performance
- View recent trading signals
- See buy/sell recommendations
- Track signal history
- Analyze performance

---

## Running the Monitoring Script

The monitoring script checks your monitored stocks and generates signals.

### Manual Run

```bash
python src/monitor_stocks.py
```

**With verbose output:**
```bash
python src/monitor_stocks.py --verbose
```

### What the Script Does

1. ✅ Loads all actively monitored stocks
2. ✅ Downloads latest market data for each
3. ✅ Runs the configured strategy
4. ✅ Detects trading signals
5. ✅ Logs signals to database
6. ✅ Updates last checked timestamp

### Example Output

```
======================================================================
📡 Stock Monitoring - 2025-01-15 09:00:00
======================================================================

📊 Monitoring 3 stock(s)...

🔍 Checking AAPL (Bollinger Bands, 1d)...
  💰 Current price: $185.23
  🔔 Signal detected: SELL at $185.23
  ✅ Logged SELL signal at $185.23

🔍 Checking MSFT (TEMA + MACD, 1d)...
  💰 Current price: $420.15
  ✓ No new signals

🔍 Checking TSLA (ADX Adaptive, 1d)...
  💰 Current price: $238.45
  ✓ No new signals

======================================================================
✅ Monitoring complete! Found 1 new signal(s)
======================================================================
```

---

## Automated Daily Monitoring

### Option 1: Cron (Linux/Mac)

Edit crontab:
```bash
crontab -e
```

Add daily run at 9 AM:
```bash
0 9 * * * cd /path/to/StrategyBuilder && python src/monitor_stocks.py >> logs/monitor.log 2>&1
```

### Option 2: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. **Trigger:** Daily at 9:00 AM (after market open)
4. **Action:** Start a program
   - **Program:** `python`
   - **Arguments:** `src\monitor_stocks.py`
   - **Start in:** `C:\path\to\StrategyBuilder`

### Option 3: Python Scheduler

Create `schedule_monitoring.py`:

```python
import schedule
import time
from src.monitor_stocks import monitor_stocks

# Run every day at 9:00 AM
schedule.every().day.at("09:00").do(monitor_stocks)

print("Monitoring scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

Run continuously:
```bash
python schedule_monitoring.py
```

---

## Database Structure

All data is stored in `data/trading.db` (SQLite database).

### Tables

1. **backtests** - Backtest history and results
2. **monitored_stocks** - Active monitoring list
3. **trading_signals** - Buy/sell signals
4. **positions** - Open/closed positions

### Backup Database

```bash
# Create backup
cp data/trading.db data/trading_backup_$(date +%Y%m%d).db

# Restore from backup
cp data/trading_backup_20250115.db data/trading.db
```

---

## Best Practices

### 1. Test First
- Always backtest a strategy thoroughly
- Test on multiple time periods
- Verify performance metrics

### 2. Monitor Selectively
- Don't monitor too many stocks (5-10 is good)
- Focus on strategies with high Sharpe ratio
- Only monitor strategies with proven win rate

### 3. Review Signals Daily
- Check signals in GUI regularly
- Verify signals against charts
- Don't blindly follow signals - use your judgment

### 4. Adjust Parameters
- Fine-tune strategy parameters
- Re-run backtests with different settings
- Update monitored stocks with better configs

### 5. Risk Management
- This is for signal generation only
- NOT for automated trading (requires broker integration)
- Always manage risk manually
- Use stop losses

---

## Example Workflow

### Day 1: Research & Backtest
1. Run backtests on AAPL with Bollinger Bands strategy
2. Test different parameters (period 15, 20, 25)
3. Find best configuration: period=20, devfactor=2
4. Results: +15% return, 60% win rate, Sharpe 1.2
5. **Save to database** ✅

### Day 2: Add to Monitoring
1. Go to Live Trading tab
2. Review backtest in history
3. Click "Add to Monitoring"
4. Stock is now actively monitored ✅

### Day 3-30: Daily Monitoring
1. Monitoring script runs daily at 9 AM
2. Checks AAPL price and runs strategy
3. When signal detected: Logs to database
4. Review signals in GUI
5. Make trading decisions

### Day 31: Review & Adjust
1. Check signal history (30 days)
2. Analyze performance
3. Adjust strategy parameters if needed
4. Add more stocks or remove underperformers

---

## Troubleshooting

### No Signals Generated

**Problem:** Monitoring script runs but no signals
**Solution:**
- Check if strategy would generate signals in backtest
- Verify date range in monitoring script
- Try shorter interval (1h instead of 1d)
- Some strategies are conservative and wait for strong signals

### Database Locked Error

**Problem:** `database is locked`
**Solution:**
- Close any other connections to database
- Don't run monitoring script while GUI is open
- Restart Streamlit app

### Price Data Not Available

**Problem:** `No data available for ticker`
**Solution:**
- Verify ticker symbol is correct
- Check if market is open
- Try different interval
- Yahoo Finance may have temporary outage

---

## Future Enhancements

🔜 **Real-time Updates** - Live chart updates every minute
🔜 **Email Notifications** - Get alerts when signals detected
🔜 **Broker Integration** - Auto-execute trades (requires API keys)
🔜 **Portfolio Tracking** - Track actual positions and P&L
🔜 **Strategy Optimization** - Auto-tune parameters

---

## FAQ

**Q: Does this automatically execute trades?**
A: No. This generates signals only. You must manually execute trades.

**Q: How often should I run the monitoring script?**
A: Once per day is sufficient for daily strategies. For hourly strategies, run every hour.

**Q: Can I monitor multiple strategies on the same stock?**
A: Yes! Add the stock multiple times with different strategies.

**Q: What happens if monitoring script fails?**
A: It just skips that run. Next scheduled run will continue normally.

**Q: Can I edit a monitored stock's parameters?**
A: Not directly. Remove it and add again with new parameters.

**Q: How long are signals stored?**
A: Forever (until you manually delete database). Use date filter to view recent ones.

---

## Support

For issues or questions:
- Check `test_system.py` for system health
- Review logs in console output
- Verify database integrity
- Test with simple strategies first (Bollinger Bands)

**Happy Trading! 📈**
