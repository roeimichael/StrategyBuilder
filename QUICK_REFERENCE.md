# StrategyBuilder API - Quick Reference

**Base URL:** `http://localhost:8000`

---

## 📋 Endpoint Summary

| Method | Endpoint | Purpose | Response Time |
|--------|----------|---------|---------------|
| GET | `/` | API info | < 50ms |
| GET | `/health` | Health check | < 50ms |
| GET | `/strategies` | List strategies | < 100ms |
| GET | `/strategies/{name}` | Strategy details | < 100ms |
| GET | `/parameters/default` | Default params | < 50ms |
| POST | `/backtest` | Run backtest | 2-10s |
| POST | `/market-data` | Get market data | 1-3s |

---

## 🚀 Most Common Requests

### 1. Run a Backtest (Simple)

```javascript
fetch('http://localhost:8000/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: "AAPL",
    strategy: "bollinger_bands_strategy",
    start_date: "2023-01-01",
    end_date: "2023-12-31",
    interval: "1d",
    cash: 10000.0
  })
})
```

### 2. Get All Strategies

```javascript
fetch('http://localhost:8000/strategies')
```

### 3. Get Market Data

```javascript
fetch('http://localhost:8000/market-data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: "AAPL",
    period: "1mo",
    interval: "1d"
  })
})
```

---

## 📊 Available Strategies

| Strategy Name | Description |
|---------------|-------------|
| `bollinger_bands_strategy` | Mean reversion using Bollinger Bands |
| `adx_strategy` | Adaptive trend/mean reversion |
| `alligator_strategy` | Long/short with Alligator indicator |
| `williams_r_strategy` | Williams %R oscillator |
| `mfi_strategy` | Money Flow Index |
| `rsi_stochastic_strategy` | Combined RSI + Stochastic |
| `cci_atr_strategy` | CCI with ATR volatility |
| `keltner_channel_strategy` | Keltner Channel breakout |
| `tema_crossover_strategy` | TEMA 20/60 crossover |
| `tema_macd_strategy` | TEMA + MACD combined |
| `momentum_multi_strategy` | Multi-indicator momentum |
| `cmf_atr_macd_strategy` | MACD + CMF + ATR with stops |

---

## 🕒 Valid Intervals

**For Backtests & Market Data:**
- `"1m"` - 1 minute
- `"5m"` - 5 minutes
- `"15m"` - 15 minutes
- `"30m"` - 30 minutes
- `"1h"` - 1 hour
- `"1d"` - 1 day (recommended)
- `"1wk"` - 1 week
- `"1mo"` - 1 month

---

## 📈 Key Response Fields

### Backtest Results

```javascript
{
  return_pct: 12.51,           // Total return percentage
  sharpe_ratio: 1.45,          // Risk-adjusted return
  max_drawdown: 8.32,          // Maximum loss from peak (%)
  total_trades: 15,            // Number of trades
  advanced_metrics: {
    win_rate: 60.0,            // % of winning trades
    profit_factor: 2.34,       // Gross profit / Gross loss
    largest_win: 320.50,       // Best trade ($)
    largest_loss: -180.25,     // Worst trade ($)
    expectancy: 83.38          // Expected $ per trade
  }
}
```

---

## ⚠️ Important Notes

1. **Backtests take time** (2-10 seconds) - Show loading indicator
2. **Date format must be** "YYYY-MM-DD"
3. **Start dates** - Don't go back more than 2 years for intraday data
4. **Default cash** is $10,000 if not specified
5. **Position sizing** is automatic (95% of cash by default)

---

## 🔧 Custom Parameters Example

```javascript
{
  ticker: "AAPL",
  strategy: "rsi_stochastic_strategy",
  start_date: "2023-01-01",
  cash: 25000.0,
  parameters: {
    position_size_pct: 80,      // Use 80% of cash per trade
    rsi_period: 14,              // RSI calculation period
    rsi_oversold: 30,            // Buy when RSI < 30
    rsi_overbought: 70           // Sell when RSI > 70
  }
}
```

---

## 🐛 Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Strategy module not found" | Invalid strategy name | Check `/strategies` for valid names |
| "No data available for TICKER" | Invalid ticker symbol | Verify ticker exists on Yahoo Finance |
| "Field 'ticker' is required" | Missing required field | Add ticker to request body |
| 500 Internal Server Error | Backend issue | Check `logs/api_errors.log` |

---

## 🎯 Pro Tips

1. **Use 1d interval** for fastest backtests
2. **Start with 90 days** of data for quick testing
3. **Check health endpoint** before running backtests
4. **Cache strategy list** - it doesn't change often
5. **Show progress** - Backtests can take 10+ seconds

---

## 📱 React Hook Example

```jsx
function useBacktest() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runBacktest = async (params) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8000/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      if (!res.ok) throw new Error('Backtest failed');
      const result = await res.json();
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, runBacktest };
}
```

---

**For full documentation, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**
