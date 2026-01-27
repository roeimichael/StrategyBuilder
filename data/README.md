# Data Directory

This directory contains static data files used by the StrategyBuilder application.

## tickers.txt

**Purpose:** Contains the list of S&P 500 ticker symbols used as the default for market scans.

**Format:**
- One ticker symbol per line
- Plain text format
- No headers or special characters
- Ticker symbols should match Yahoo Finance format (e.g., use `BRK-B` not `BRK.B`)

**Usage:**
- When a user runs a market scan without specifying tickers, the system uses this list
- The system first tries to fetch the latest S&P 500 list from Wikipedia
- If Wikipedia fetch fails, it falls back to reading this file

**How to Update:**
1. Replace the contents of `tickers.txt` with your updated S&P 500 ticker list
2. Ensure one ticker per line
3. Use Yahoo Finance ticker format (hyphens instead of dots for special characters)
4. No need to restart the application - changes take effect on next market scan

**Current File:**
The current file contains a sample list of ~50 major S&P 500 stocks. **Replace this with your complete S&P 500 ticker list** for full market scan coverage.

## Database Files

Database files (*.db) are automatically created in this directory when the application runs:
- `market_data.db` - Cached market data
- `strategy_runs.db` - Backtest run history
- `presets.db` - Saved strategy presets
- `portfolios.db` - Portfolio configurations
- `watchlists.db` - Watchlist tracking data
