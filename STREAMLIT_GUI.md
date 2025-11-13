# StrategyBuilder Streamlit GUI

## 🚀 Quick Start

### Running the GUI Application

```bash
# From project root
streamlit run src/app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`

## 📋 Features

### Stock Selection
- **S&P 500**: Choose from all 500 stocks in the S&P 500 index
- **Popular Stocks**: Pre-categorized lists (Tech Giants, Finance, Healthcare, Consumer, Energy)
- **Custom Input**: Enter any ticker symbols manually

### Strategy Selection
- 6 pre-built trading strategies with descriptions
- Dynamic parameter adjustment for strategies with configurable settings
- Advanced parameters (MACD, ATR settings)

### Date & Time Configuration
- Interactive calendar date pickers
- Multiple time intervals (5m, 15m, 30m, 1h, 1d, 1wk)
- Custom date ranges

### Backtest Configuration
- Starting capital selection
- Position size control (% of capital per trade)
- Advanced indicator parameters

### Results & Visualization
- **Key Metrics**: Portfolio value, returns, Sharpe ratio, max drawdown, win rate
- **Interactive Chart**: Candlestick chart with entry/exit signals
  - Green triangles (▲) = Buy signals
  - Red triangles (▼) = Sell signals
  - Color-coded by profitability
- **Performance Analysis**:
  - Cumulative P&L over time
  - Trade return distribution histogram
- **Trade Details Table**:
  - Entry/exit dates and prices
  - Position sizes and P&L
  - Color-coded profits/losses
  - Download as CSV

### Multi-Stock Support
- Run backtests on multiple stocks simultaneously
- Tab-based navigation for results
- Individual analysis for each stock

## 💡 Usage Tips

1. **Start Simple**: Begin with a single stock and default parameters
2. **Compare Strategies**: Run the same stock with different strategies to compare
3. **Optimize Parameters**: Use the advanced parameters to tune strategy performance
4. **Multi-Stock Analysis**: Select multiple stocks to find the best performers
5. **Download Data**: Export trade details for further analysis in Excel

## 🎨 UI Components

- **Sidebar**: All configuration options
- **Main Panel**: Results display with charts and tables
- **Progress Bar**: Shows backtest execution progress
- **Download Buttons**: Export trade data

## 🔧 Troubleshooting

### Chart Not Loading
- Check internet connection (requires data download from Yahoo Finance)
- Verify ticker symbol is valid
- Try a different date range (some tickers may have limited historical data)

### No Trades Executed
- Strategy may not have generated signals in the selected date range
- Try adjusting strategy parameters
- Try a different date range or time interval

### Slow Performance
- Backtesting multiple stocks takes time
- Shorter time intervals (5m, 15m) require more data processing
- Consider using daily interval for faster results

## 📊 Understanding the Charts

### Price Chart
- **Candlestick**: Green = up day, Red = down day
- **Buy Signals**: Green triangles pointing up (▲)
- **Sell Signals**: Red/green triangles pointing down (▼)
- **Volume**: Bar chart below price shows trading volume
- **Hover**: Mouse over for detailed price information

### Cumulative P&L
- Shows total profit/loss accumulation over time
- Area under curve = total gains
- Zero line = break-even point

### Return Distribution
- Histogram of individual trade returns
- Green = winning trades
- Red = losing trades
- Shows if strategy has consistent or varied returns

## 🎯 Example Workflow

1. Select "Popular Stocks" → "Tech Giants" → Choose AAPL, MSFT
2. Select "Bollinger Bands" strategy
3. Set date range: Last 365 days
4. Keep default parameters or adjust
5. Click "🚀 Run Backtest"
6. View results in tabs
7. Analyze charts and trade details
8. Download trade data if needed
9. Try different strategies to compare

## 📈 Next Steps

After analyzing results:
- Adjust strategy parameters to optimize performance
- Test on different time periods to validate robustness
- Compare multiple strategies on the same stock
- Look for consistent winners across different market conditions
- Use trade details to understand why certain trades worked/failed
