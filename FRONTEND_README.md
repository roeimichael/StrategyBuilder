# StrategyBuilder API - Frontend Developer Guide

Welcome! This guide will help you integrate the StrategyBuilder API into your frontend application.

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** | Complete API reference with all endpoints, data models, and examples |
| **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** | Quick cheat sheet for common requests |
| **[test_api_capture.py](./test_api_capture.py)** | Test script that generates real request/response examples |
| **This file** | Getting started guide |

---

## 🚀 Getting Started

### Step 1: Test the API

Before building your frontend, test the API to see real requests and responses:

```bash
# Make sure you're in the project directory
cd StrategyBuilder

# Start the API server (in one terminal)
python run_api.py

# Run the test script (in another terminal)
python test_api_capture.py
```

This will:
1. Make requests to all API endpoints
2. Save results to `api_test_results_[timestamp].json`
3. Create `api_examples.json` with clean input-output pairs

### Step 2: Review the Examples

Open `api_examples.json` to see:
- **Exact request formats** for each endpoint
- **Real response data** from the API
- **Typical response times** to expect

Example structure:
```json
{
  "api_base_url": "http://localhost:8000",
  "endpoints": {
    "/backtest": [
      {
        "description": "Run Backtest - Bollinger Bands Strategy",
        "method": "POST",
        "request": {
          "payload": { /* exact request format */ }
        },
        "response_sample": { /* real API response */ },
        "typical_response_time_seconds": 3.245
      }
    ]
  }
}
```

### Step 3: Build Your Frontend

Use the documentation to build your UI:

1. **Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** for common patterns
2. **Reference [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** for details
3. **Copy TypeScript interfaces** from the documentation
4. **Use the React examples** as starting points

---

## 🎯 What You Need to Know

### API Basics

- **Base URL:** `http://localhost:8000`
- **Format:** All requests/responses use JSON
- **CORS:** Enabled for all origins (you won't have CORS issues)
- **Authentication:** None required
- **Rate Limiting:** None

### Key Concepts

1. **Strategies** - Pre-built trading algorithms (12 available)
2. **Backtests** - Simulations of strategies on historical data
3. **Tickers** - Stock symbols (e.g., AAPL, MSFT, GOOGL)
4. **Intervals** - Time granularity (1m, 5m, 1h, 1d, etc.)
5. **Parameters** - Configuration for strategies

### You DON'T Need to Know

- ❌ How backtesting works internally
- ❌ How strategies are implemented
- ❌ Backend architecture
- ❌ Python/Backtrader framework details

**You only need to know:**
- ✅ What endpoint to call
- ✅ What data to send
- ✅ What you'll get back

---

## 📊 Typical User Flows

### Flow 1: Simple Backtest

```
User selects ticker → User selects strategy → User clicks "Run"
                                                      ↓
                                            POST /backtest
                                                      ↓
                                            Show loading (2-10s)
                                                      ↓
                                            Display results
```

### Flow 2: Strategy Comparison

```
User selects multiple strategies → User clicks "Compare"
                                              ↓
                                    Run backtests for each
                                              ↓
                                    Show side-by-side results
```

### Flow 3: Parameter Tuning

```
User adjusts strategy parameters → User clicks "Test"
                                              ↓
                                    POST /backtest with custom params
                                              ↓
                                    Show updated results
```

---

## 🎨 UI Recommendations

### Required Elements

1. **Strategy Selector** - Dropdown or list of 12 strategies
2. **Ticker Input** - Text field for stock symbol
3. **Date Range Picker** - Start and end dates
4. **Run Button** - Trigger backtest
5. **Loading Indicator** - Show during backtest (can take 10s)
6. **Results Display** - Show key metrics

### Key Metrics to Display

**Primary:**
- Return % (most important!)
- Total Trades
- Win Rate %

**Secondary:**
- Sharpe Ratio
- Max Drawdown
- Profit Factor

**Advanced (optional):**
- All advanced_metrics fields
- Trade-by-trade breakdown
- Equity curve chart

### Chart Visualization

The backtest response includes a `chart_data` field with everything needed for interactive charts:

**What's Included:**
- **OHLC Data** - Open/High/Low/Close/Volume for each bar
- **Technical Indicators** - All indicators used by the strategy (dynamically included)
- **Trade Markers** - Buy/sell positions with dates, prices, and PnL

**Recommended Charting Libraries:**
- [Recharts](https://recharts.org/) - Simple React charts
- [Chart.js](https://www.chartjs.org/) - Flexible charting
- [TradingView Lightweight Charts](https://www.tradingview.com/lightweight-charts/) - Professional trading charts

**Example Data Structure:**
```javascript
{
  chart_data: {
    ohlc: [{date: "2024-01-01", open: 150, high: 152, low: 149, close: 151, volume: 1000000}, ...],
    indicators: {"boll_top": [152.5, ...], "boll_mid": [150.0, ...], "boll_bot": [147.5, ...]},
    trade_markers: [{date: "2024-01-05", price: 149.8, type: "BUY", action: "OPEN"}, ...]
  }
}
```

See [API_DOCUMENTATION.md - Chart Data Visualization](./API_DOCUMENTATION.md#chart-data-visualization-example) for complete React example.

### Performance Considerations

- **Cache** strategy list (doesn't change)
- **Debounce** parameter changes
- **Show progress** for backtests > 5 seconds
- **Disable UI** while backtest is running
- **Handle errors** gracefully

---

## 🧪 Testing Checklist

Before launching, test these scenarios:

- [ ] Run backtest with valid data
- [ ] Run backtest with invalid ticker (should error)
- [ ] Run backtest with invalid strategy (should error)
- [ ] Run backtest with custom parameters
- [ ] Fetch market data for multiple tickers
- [ ] Handle API downtime gracefully
- [ ] Show loading state during long requests
- [ ] Display all key metrics correctly
- [ ] Format numbers properly (2 decimal places)
- [ ] Handle null values in advanced metrics

---

## 🔧 Development Tips

### 1. Use Environment Variables

```javascript
// .env
REACT_APP_API_URL=http://localhost:8000

// In your code
const API_URL = process.env.REACT_APP_API_URL;
```

### 2. Create an API Client

```javascript
// api.js
const API_URL = 'http://localhost:8000';

export const api = {
  getStrategies: () =>
    fetch(`${API_URL}/strategies`).then(res => res.json()),

  runBacktest: (params) =>
    fetch(`${API_URL}/backtest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    }).then(res => res.json()),

  getMarketData: (params) =>
    fetch(`${API_URL}/market-data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    }).then(res => res.json())
};
```

### 3. Add TypeScript Types

Copy types from [API_DOCUMENTATION.md](./API_DOCUMENTATION.md#data-models):

```typescript
interface BacktestRequest {
  ticker: string;
  strategy: string;
  start_date?: string;
  end_date?: string;
  interval?: string;
  cash?: number;
  parameters?: Record<string, number>;
}

interface BacktestResponse {
  success: boolean;
  ticker: string;
  strategy: string;
  return_pct: number;
  sharpe_ratio: number | null;
  total_trades: number;
  advanced_metrics: AdvancedMetrics;
  // ... more fields
}
```

### 4. Error Handling

```javascript
async function runBacktest(params) {
  try {
    const response = await fetch('/backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Backtest failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Backtest error:', error);
    // Show error to user
    alert(error.message);
  }
}
```

---

## 📞 Getting Help

### During Development

1. **Check Swagger Docs:** Visit `http://localhost:8000/docs`
2. **View Error Logs:** Check `logs/api_errors.log`
3. **Run Test Script:** `python test_api_capture.py`
4. **Check Health:** `curl http://localhost:8000/health`

### Common Issues

**Issue:** CORS errors
**Solution:** Make sure API is running on `localhost:8000`

**Issue:** Timeout on backtests
**Solution:** Reduce date range or use 1d interval

**Issue:** 500 errors
**Solution:** Check `logs/api_errors.log` for details

**Issue:** Invalid ticker errors
**Solution:** Verify ticker symbol exists on Yahoo Finance

---

## 🎯 Quick Start Checklist

- [ ] Read QUICK_REFERENCE.md
- [ ] Run test_api_capture.py
- [ ] Review api_examples.json
- [ ] Copy TypeScript interfaces
- [ ] Create API client module
- [ ] Build strategy selector component
- [ ] Build backtest form component
- [ ] Build results display component
- [ ] Add loading states
- [ ] Add error handling
- [ ] Test with real data
- [ ] Deploy!

---

## 📝 Example Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          # API client functions
│   │   └── types.ts           # TypeScript interfaces
│   ├── components/
│   │   ├── StrategySelector.tsx
│   │   ├── BacktestForm.tsx
│   │   ├── ResultsDisplay.tsx
│   │   └── LoadingSpinner.tsx
│   ├── hooks/
│   │   ├── useBacktest.ts     # Custom hook for backtests
│   │   └── useStrategies.ts   # Custom hook for strategies
│   └── App.tsx
```

---

## 🚀 You're Ready!

You now have everything you need to build the frontend:

1. ✅ **API Documentation** - Complete reference
2. ✅ **Real Examples** - Actual request/response data
3. ✅ **Quick Reference** - Common patterns
4. ✅ **React Examples** - Copy-paste ready code
5. ✅ **TypeScript Types** - Type safety
6. ✅ **Testing Tools** - Verify integration

**Happy coding! 🎉**

---

**Questions?** Check `logs/api_errors.log` or run `python test_api_capture.py` to debug.
