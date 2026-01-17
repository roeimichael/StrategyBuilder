# Market Scan Feature - Frontend Implementation Guide

## Overview

The Market Scan feature allows users to test a trading strategy across all S&P 500 stocks (503 tickers) in a single operation. This provides a comprehensive view of how a strategy performs across the entire market, enabling identification of winning strategies and macro trend analysis.

## API Endpoint

### POST `/market-scan`

Executes a backtest strategy across all S&P 500 stocks and returns aggregated results with per-stock breakdown.

**Request Body:**
```typescript
interface MarketScanRequest {
  strategy: string;                      // Required: Strategy name
  start_date?: string;                   // Optional: "YYYY-MM-DD" format
  end_date?: string;                     // Optional: "YYYY-MM-DD" format
  interval?: string;                     // Optional: "1d", "1h", etc. (default: "1d")
  cash?: number;                         // Optional: Initial capital per stock (default: 10000)
  parameters?: Record<string, number>;   // Optional: Strategy parameters
}
```

**Response:**
```typescript
interface MarketScanResponse {
  success: boolean;
  strategy: string;

  // Aggregate Portfolio Metrics
  start_value: number;                   // Total initial capital across all stocks
  end_value: number;                     // Total final value
  pnl: number;                           // Total profit/loss
  return_pct: number;                    // Overall return percentage
  sharpe_ratio: number | null;           // Portfolio Sharpe ratio
  max_drawdown: number | null;           // Portfolio max drawdown %

  // Trading Activity
  total_trades: number;                  // Total trades across all stocks
  winning_trades: number;
  losing_trades: number;

  // Market Coverage
  stocks_scanned: number;                // Number of stocks processed
  stocks_with_trades: number;            // Stocks that generated trades

  // Date Range
  interval: string;
  start_date: string;
  end_date: string;

  // Per-Stock Results (sorted by PnL descending)
  stock_results: StockScanResult[];

  // Macro Statistics
  macro_statistics: MacroStatistics;
}

interface StockScanResult {
  ticker: string;
  pnl: number;
  return_pct: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  start_value: number;
  end_value: number;
}

interface MacroStatistics {
  // PnL Distribution
  avg_pnl: number;
  median_pnl: number;
  std_pnl: number;
  min_pnl: number;
  max_pnl: number;

  // Return Distribution
  avg_return_pct: number;
  median_return_pct: number;
  std_return_pct: number;
  min_return_pct: number;
  max_return_pct: number;

  // Stock Profitability
  profitable_stocks: number;             // Stocks with PnL > 0
  losing_stocks: number;                 // Stocks with PnL < 0
  neutral_stocks: number;                // Stocks with PnL = 0
  profitability_rate: number;            // % of profitable stocks

  // Trading Metrics
  avg_trades_per_stock: number;
  win_rate: number;                      // Overall win rate %
}
```

## Frontend Implementation

### 1. Market Scan Tab/Page Structure

```typescript
// Main Market Scan Component
const MarketScanPage = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<MarketScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="market-scan-container">
      <MarketScanForm onSubmit={handleMarketScan} loading={loading} />
      {loading && <LoadingIndicator />}
      {error && <ErrorMessage error={error} />}
      {results && (
        <>
          <AggregateMetricsPanel data={results} />
          <MacroStatisticsPanel data={results.macro_statistics} />
          <StockResultsTable data={results.stock_results} />
          <VisualizationsPanel data={results} />
        </>
      )}
    </div>
  );
};
```

### 2. API Call Implementation

```typescript
const runMarketScan = async (request: MarketScanRequest): Promise<MarketScanResponse> => {
  const response = await fetch('http://localhost:8086/market-scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Market scan failed');
  }

  return response.json();
};

// Example usage
const handleMarketScan = async (formData: MarketScanRequest) => {
  setLoading(true);
  setError(null);

  try {
    const results = await runMarketScan(formData);
    setResults(results);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

### 3. Aggregate Metrics Panel

Display high-level portfolio performance:

```typescript
const AggregateMetricsPanel = ({ data }: { data: MarketScanResponse }) => (
  <div className="aggregate-panel">
    <h2>Portfolio Performance</h2>
    <div className="metrics-grid">
      <MetricCard
        label="Total PnL"
        value={formatCurrency(data.pnl)}
        trend={data.pnl >= 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        label="Return"
        value={`${data.return_pct}%`}
        trend={data.return_pct >= 0 ? 'positive' : 'negative'}
      />
      <MetricCard label="Sharpe Ratio" value={data.sharpe_ratio?.toFixed(2) || 'N/A'} />
      <MetricCard label="Max Drawdown" value={`${data.max_drawdown}%`} />
      <MetricCard label="Total Trades" value={data.total_trades} />
      <MetricCard
        label="Win Rate"
        value={`${((data.winning_trades / data.total_trades) * 100).toFixed(1)}%`}
      />
      <MetricCard
        label="Stocks Traded"
        value={`${data.stocks_with_trades}/${data.stocks_scanned}`}
      />
    </div>
  </div>
);
```

### 4. Macro Statistics Panel

Display distribution and statistical insights:

```typescript
const MacroStatisticsPanel = ({ data }: { data: MacroStatistics }) => (
  <div className="macro-panel">
    <h2>Market-Wide Statistics</h2>

    <div className="stats-section">
      <h3>PnL Distribution</h3>
      <StatRow label="Average PnL" value={formatCurrency(data.avg_pnl)} />
      <StatRow label="Median PnL" value={formatCurrency(data.median_pnl)} />
      <StatRow label="Std Deviation" value={formatCurrency(data.std_pnl)} />
      <StatRow label="Range" value={`${formatCurrency(data.min_pnl)} to ${formatCurrency(data.max_pnl)}`} />
    </div>

    <div className="stats-section">
      <h3>Return Distribution</h3>
      <StatRow label="Average Return" value={`${data.avg_return_pct}%`} />
      <StatRow label="Median Return" value={`${data.median_return_pct}%`} />
      <StatRow label="Std Deviation" value={`${data.std_return_pct}%`} />
      <StatRow label="Range" value={`${data.min_return_pct}% to ${data.max_return_pct}%`} />
    </div>

    <div className="stats-section">
      <h3>Stock Profitability</h3>
      <ProfitabilityChart
        profitable={data.profitable_stocks}
        losing={data.losing_stocks}
        neutral={data.neutral_stocks}
      />
      <StatRow label="Profitability Rate" value={`${data.profitability_rate}%`} />
      <StatRow label="Avg Trades/Stock" value={data.avg_trades_per_stock.toFixed(2)} />
    </div>
  </div>
);
```

### 5. Stock Results Table (Sortable & Filterable)

```typescript
const StockResultsTable = ({ data }: { data: StockScanResult[] }) => {
  const [sortField, setSortField] = useState<keyof StockScanResult>('pnl');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filterText, setFilterText] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'profitable' | 'losing'>('all');

  const filteredAndSorted = useMemo(() => {
    let filtered = data;

    // Apply ticker search filter
    if (filterText) {
      filtered = filtered.filter(stock =>
        stock.ticker.toLowerCase().includes(filterText.toLowerCase())
      );
    }

    // Apply profitability filter
    if (filterType === 'profitable') {
      filtered = filtered.filter(stock => stock.pnl > 0);
    } else if (filterType === 'losing') {
      filtered = filtered.filter(stock => stock.pnl < 0);
    }

    // Sort
    return [...filtered].sort((a, b) => {
      const aVal = a[sortField] ?? 0;
      const bVal = b[sortField] ?? 0;
      return sortDirection === 'desc' ? bVal - aVal : aVal - bVal;
    });
  }, [data, sortField, sortDirection, filterText, filterType]);

  return (
    <div className="stock-results-table">
      <div className="table-controls">
        <input
          type="text"
          placeholder="Search ticker..."
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
        />
        <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
          <option value="all">All Stocks</option>
          <option value="profitable">Profitable Only</option>
          <option value="losing">Losing Only</option>
        </select>
      </div>

      <table>
        <thead>
          <tr>
            <SortableHeader field="ticker" label="Ticker" />
            <SortableHeader field="pnl" label="PnL" />
            <SortableHeader field="return_pct" label="Return %" />
            <SortableHeader field="total_trades" label="Trades" />
            <SortableHeader field="winning_trades" label="Win" />
            <SortableHeader field="losing_trades" label="Loss" />
            <SortableHeader field="sharpe_ratio" label="Sharpe" />
            <SortableHeader field="max_drawdown" label="Max DD" />
          </tr>
        </thead>
        <tbody>
          {filteredAndSorted.map((stock) => (
            <tr key={stock.ticker} onClick={() => handleStockClick(stock)}>
              <td>{stock.ticker}</td>
              <td className={stock.pnl >= 0 ? 'positive' : 'negative'}>
                {formatCurrency(stock.pnl)}
              </td>
              <td className={stock.return_pct >= 0 ? 'positive' : 'negative'}>
                {stock.return_pct}%
              </td>
              <td>{stock.total_trades}</td>
              <td>{stock.winning_trades}</td>
              <td>{stock.losing_trades}</td>
              <td>{stock.sharpe_ratio?.toFixed(2) || 'N/A'}</td>
              <td>{stock.max_drawdown?.toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### 6. Visualizations

```typescript
const VisualizationsPanel = ({ data }: { data: MarketScanResponse }) => (
  <div className="visualizations">
    {/* PnL Distribution Histogram */}
    <div className="chart-container">
      <h3>PnL Distribution</h3>
      <Histogram
        data={data.stock_results.map(s => s.pnl)}
        bins={50}
        xLabel="PnL ($)"
        yLabel="Number of Stocks"
      />
    </div>

    {/* Return Distribution Histogram */}
    <div className="chart-container">
      <h3>Return Distribution</h3>
      <Histogram
        data={data.stock_results.map(s => s.return_pct)}
        bins={50}
        xLabel="Return (%)"
        yLabel="Number of Stocks"
      />
    </div>

    {/* Risk-Return Scatter Plot */}
    <div className="chart-container">
      <h3>Risk vs Return</h3>
      <ScatterPlot
        data={data.stock_results.map(s => ({
          x: s.max_drawdown || 0,
          y: s.return_pct,
          label: s.ticker
        }))}
        xLabel="Max Drawdown (%)"
        yLabel="Return (%)"
      />
    </div>

    {/* Top Winners/Losers Bar Chart */}
    <div className="chart-container">
      <h3>Top 10 Winners vs Top 10 Losers</h3>
      <BarChart
        winners={data.stock_results.slice(0, 10)}
        losers={data.stock_results.slice(-10).reverse()}
      />
    </div>
  </div>
);
```

### 7. Integration with Existing Backtest Tab

Add a "Scan Entire Market" button in the backtest results view:

```typescript
const BacktestResults = ({ result, strategy, parameters }: BacktestResultsProps) => {
  const navigate = useNavigate();

  const handleMarketScan = () => {
    // Navigate to market scan tab with pre-filled strategy and parameters
    navigate('/market-scan', {
      state: {
        strategy: strategy,
        parameters: parameters,
        interval: result.interval
      }
    });
  };

  return (
    <div className="backtest-results">
      {/* Existing backtest results display */}

      <div className="action-buttons">
        <button onClick={handleMarketScan} className="market-scan-btn">
          🔍 Scan Entire S&P 500 with This Strategy
        </button>
      </div>
    </div>
  );
};
```

## User Experience Considerations

### Loading States
- Market scan takes 5-10 minutes for full S&P 500 scan
- Display progress indicator: "Scanning 503 stocks... This may take 5-10 minutes"
- Consider showing partial results as they come in (requires backend streaming support)

### Response Size
- Full response: ~75KB (manageable)
- Gzipped: ~20-30KB
- No pagination needed - can handle all data client-side

### Error Handling
```typescript
try {
  const results = await runMarketScan(request);
} catch (error) {
  if (error.message.includes('Strategy') && error.message.includes('not found')) {
    showError('Invalid strategy selected. Please choose a valid strategy.');
  } else if (error.message.includes('timeout')) {
    showError('Market scan timed out. Try a shorter date range or check server logs.');
  } else {
    showError(`Market scan failed: ${error.message}`);
  }
}
```

### Caching Strategy
```typescript
// Cache results to avoid re-running expensive scans
const cacheKey = `market-scan-${strategy}-${start_date}-${end_date}-${JSON.stringify(parameters)}`;
const cachedResults = localStorage.getItem(cacheKey);

if (cachedResults) {
  const { data, timestamp } = JSON.parse(cachedResults);
  const age = Date.now() - timestamp;

  // Use cache if less than 24 hours old
  if (age < 24 * 60 * 60 * 1000) {
    return data;
  }
}

// Run scan and cache results
const results = await runMarketScan(request);
localStorage.setItem(cacheKey, JSON.stringify({
  data: results,
  timestamp: Date.now()
}));
```

## Example Request/Response

**Request:**
```json
{
  "strategy": "bollinger_bands_strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "interval": "1d",
  "cash": 10000.0,
  "parameters": {
    "period": 20,
    "devfactor": 2.0
  }
}
```

**Response (abbreviated):**
```json
{
  "success": true,
  "strategy": "bollinger_bands_strategy",
  "start_value": 5030000.0,
  "end_value": 5234500.0,
  "pnl": 204500.0,
  "return_pct": 4.07,
  "sharpe_ratio": 1.23,
  "max_drawdown": -5.67,
  "total_trades": 1250,
  "winning_trades": 680,
  "losing_trades": 570,
  "interval": "1d",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "stocks_scanned": 503,
  "stocks_with_trades": 487,
  "stock_results": [
    {
      "ticker": "NVDA",
      "pnl": 2450.50,
      "return_pct": 24.51,
      "total_trades": 8,
      "winning_trades": 6,
      "losing_trades": 2,
      "sharpe_ratio": 3.2,
      "max_drawdown": -4.5,
      "start_value": 10000.0,
      "end_value": 12450.50
    },
    // ... 502 more stocks
  ],
  "macro_statistics": {
    "avg_pnl": 406.56,
    "median_pnl": 125.30,
    "std_pnl": 850.25,
    "min_pnl": -1250.50,
    "max_pnl": 2450.50,
    "avg_return_pct": 4.07,
    "median_return_pct": 1.25,
    "std_return_pct": 8.50,
    "min_return_pct": -12.51,
    "max_return_pct": 24.51,
    "profitable_stocks": 320,
    "losing_stocks": 167,
    "neutral_stocks": 16,
    "profitability_rate": 63.62,
    "avg_trades_per_stock": 2.49,
    "win_rate": 54.40
  }
}
```

## Performance Tips

1. **Use pagination for very large tables** (500+ rows)
2. **Implement virtual scrolling** for stock results table
3. **Lazy load visualizations** - render charts only when tab is visible
4. **Debounce filter inputs** to avoid re-rendering on every keystroke
5. **Use Web Workers** for heavy computations (histogram bins, etc.)
6. **Cache results** to avoid re-running expensive scans

## Testing Checklist

- [ ] Form validates required fields (strategy)
- [ ] Loading state displays during scan
- [ ] Error messages display for invalid requests
- [ ] All 503 stocks displayed in results table
- [ ] Sorting works for all columns
- [ ] Filtering by ticker works
- [ ] Filtering by profitability works
- [ ] Macro statistics display correctly
- [ ] Visualizations render without errors
- [ ] "Scan Market" button in backtest tab navigates correctly
- [ ] Response caching works
- [ ] Long-running requests don't block UI
