# Portfolio Tracker - Frontend Implementation Guide

## Overview

The Portfolio Tracker feature allows users to manage a portfolio of stock positions and run strategy analysis across the entire portfolio with weighted results based on position sizes. This provides insights into how a strategy performs across a diversified portfolio rather than individual stocks.

## Key Features

- **Position Management**: Add, update, delete, and view portfolio positions
- **Automatic Position Sizing**: Calculate position size from quantity × entry price
- **Weighted Analysis**: Run backtests with results weighted by position size
- **Portfolio Statistics**: Comprehensive stats across all positions
- **Individual Results**: See how each position performed

## API Endpoints

### 1. Add Portfolio Position

**POST `/portfolio`**

Add a new position to the portfolio.

```typescript
interface AddPortfolioPositionRequest {
  ticker: string;           // Stock ticker (1-10 chars)
  quantity: number;         // Number of shares (> 0)
  entry_price: number;      // Entry price per share (> 0)
  entry_date: string;       // Entry date "YYYY-MM-DD"
  notes?: string;           // Optional notes (max 500 chars)
}

interface PortfolioPositionResponse {
  id: number;
  ticker: string;
  quantity: number;
  entry_price: number;
  entry_date: string;
  position_size: number;    // Automatically calculated: quantity × entry_price
  notes: string | null;
  created_at: string;
  updated_at: string;
}
```

**Example:**
```typescript
const addPosition = async (position: AddPortfolioPositionRequest) => {
  const response = await fetch('http://localhost:8086/portfolio', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(position)
  });
  return response.json();
};

// Usage
const newPosition = await addPosition({
  ticker: "AAPL",
  quantity: 100,
  entry_price: 150.50,
  entry_date: "2024-01-15",
  notes: "Initial tech position"
});
// Returns: { id: 1, ticker: "AAPL", position_size: 15050.0, ... }
```

### 2. Get Portfolio

**GET `/portfolio`**

Retrieve all positions and portfolio summary.

```typescript
interface PortfolioSummaryResponse {
  total_positions: number;
  total_portfolio_value: number;
  positions: PortfolioPositionResponse[];
}
```

**Example:**
```typescript
const getPortfolio = async () => {
  const response = await fetch('http://localhost:8086/portfolio');
  return response.json();
};

// Usage
const portfolio = await getPortfolio();
console.log(`Portfolio Value: $${portfolio.total_portfolio_value.toFixed(2)}`);
console.log(`Positions: ${portfolio.total_positions}`);
```

### 3. Get Single Position

**GET `/portfolio/{position_id}`**

Retrieve a specific position by ID.

```typescript
const getPosition = async (positionId: number) => {
  const response = await fetch(`http://localhost:8086/portfolio/${positionId}`);
  if (!response.ok) throw new Error('Position not found');
  return response.json();
};
```

### 4. Update Position

**PUT `/portfolio/{position_id}`**

Update an existing position. All fields are optional.

```typescript
interface UpdatePortfolioPositionRequest {
  ticker?: string;
  quantity?: number;
  entry_price?: number;
  entry_date?: string;
  notes?: string;
}
```

**Example:**
```typescript
const updatePosition = async (positionId: number, updates: UpdatePortfolioPositionRequest) => {
  const response = await fetch(`http://localhost:8086/portfolio/${positionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  });
  return response.json();
};

// Usage: Increase position size
await updatePosition(1, {
  quantity: 150,  // Changed from 100
  notes: "Increased position"
});
// position_size automatically recalculated: 150 × 150.50 = $22,575
```

### 5. Delete Position

**DELETE `/portfolio/{position_id}`**

Remove a position from the portfolio.

```typescript
const deletePosition = async (positionId: number) => {
  const response = await fetch(`http://localhost:8086/portfolio/${positionId}`, {
    method: 'DELETE'
  });
  return response.json();
};

// Returns: { success: true, message: "Position 1 deleted successfully" }
```

### 6. Analyze Portfolio

**POST `/portfolio/analyze`**

Run strategy analysis across all portfolio positions with weighted results.

```typescript
interface PortfolioAnalysisRequest {
  strategy: string;                      // Required: Strategy name
  start_date?: string;                   // Optional: "YYYY-MM-DD"
  end_date?: string;                     // Optional: "YYYY-MM-DD"
  interval?: string;                     // Optional: "1d", "1h", etc. (default: "1d")
  parameters?: Record<string, number>;   // Optional: Strategy parameters
}

interface PositionAnalysisResult {
  position_id: number;
  ticker: string;
  position_size: number;
  weight: number;                        // Percentage of total portfolio
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

interface PortfolioAnalysisResponse {
  success: boolean;
  strategy: string;
  interval: string;
  start_date: string;
  end_date: string;

  // Portfolio-level weighted metrics
  total_portfolio_value: number;
  weighted_pnl: number;                  // Sum of all position PnLs
  weighted_return_pct: number;           // Weighted average return
  weighted_sharpe_ratio: number | null;  // Weighted average Sharpe
  weighted_max_drawdown: number | null;  // Weighted average drawdown

  // Trading activity
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  positions_analyzed: number;

  // Individual position results
  position_results: PositionAnalysisResult[];

  // Portfolio statistics
  portfolio_statistics: {
    avg_position_pnl: number;
    median_position_pnl: number;
    std_position_pnl: number;
    min_position_pnl: number;
    max_position_pnl: number;
    avg_position_return: number;
    median_position_return: number;
    profitable_positions: number;
    losing_positions: number;
    win_rate: number;
    avg_trades_per_position: number;
  };
}
```

**Example:**
```typescript
const analyzePortfolio = async (request: PortfolioAnalysisRequest) => {
  const response = await fetch('http://localhost:8086/portfolio/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return response.json();
};

// Usage
const analysis = await analyzePortfolio({
  strategy: "bollinger_bands_strategy",
  start_date: "2024-01-01",
  end_date: "2024-03-31",
  interval: "1d",
  parameters: {
    period: 20,
    devfactor: 2.0
  }
});

console.log(`Portfolio PnL: $${analysis.weighted_pnl.toFixed(2)}`);
console.log(`Weighted Return: ${analysis.weighted_return_pct.toFixed(2)}%`);
```

## Frontend Implementation

### 1. Portfolio Management Page

```typescript
const PortfolioPage = () => {
  const [positions, setPositions] = useState<PortfolioPositionResponse[]>([]);
  const [totalValue, setTotalValue] = useState<number>(0);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);

  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    const portfolio = await getPortfolio();
    setPositions(portfolio.positions);
    setTotalValue(portfolio.total_portfolio_value);
  };

  return (
    <div className="portfolio-page">
      <PortfolioSummary
        totalValue={totalValue}
        totalPositions={positions.length}
      />

      <div className="actions">
        <button onClick={() => setShowAddForm(true)}>
          Add Position
        </button>
        <button
          onClick={() => setShowAnalysis(true)}
          disabled={positions.length === 0}
        >
          Analyze Portfolio
        </button>
      </div>

      <PositionsTable
        positions={positions}
        onUpdate={loadPortfolio}
        onDelete={loadPortfolio}
      />

      {showAddForm && (
        <AddPositionModal
          onClose={() => setShowAddForm(false)}
          onSuccess={() => {
            setShowAddForm(false);
            loadPortfolio();
          }}
        />
      )}

      {showAnalysis && (
        <AnalysisModal
          positions={positions}
          onClose={() => setShowAnalysis(false)}
        />
      )}
    </div>
  );
};
```

### 2. Portfolio Summary Component

```typescript
const PortfolioSummary = ({ totalValue, totalPositions }: {
  totalValue: number;
  totalPositions: number;
}) => (
  <div className="portfolio-summary">
    <h2>Portfolio Overview</h2>
    <div className="metrics">
      <MetricCard
        label="Total Value"
        value={`$${totalValue.toLocaleString()}`}
        icon="💰"
      />
      <MetricCard
        label="Positions"
        value={totalPositions}
        icon="📊"
      />
    </div>
  </div>
);
```

### 3. Positions Table

```typescript
const PositionsTable = ({ positions, onUpdate, onDelete }: {
  positions: PortfolioPositionResponse[];
  onUpdate: () => void;
  onDelete: () => void;
}) => {
  const [editingId, setEditingId] = useState<number | null>(null);

  const handleEdit = async (id: number, updates: UpdatePortfolioPositionRequest) => {
    await updatePosition(id, updates);
    setEditingId(null);
    onUpdate();
  };

  const handleDelete = async (id: number) => {
    if (confirm('Delete this position?')) {
      await deletePosition(id);
      onDelete();
    }
  };

  return (
    <table className="positions-table">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Quantity</th>
          <th>Entry Price</th>
          <th>Position Size</th>
          <th>Entry Date</th>
          <th>Notes</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {positions.map(position => (
          <tr key={position.id}>
            {editingId === position.id ? (
              <EditRow
                position={position}
                onSave={(updates) => handleEdit(position.id, updates)}
                onCancel={() => setEditingId(null)}
              />
            ) : (
              <>
                <td>{position.ticker}</td>
                <td>{position.quantity}</td>
                <td>${position.entry_price.toFixed(2)}</td>
                <td>${position.position_size.toLocaleString()}</td>
                <td>{position.entry_date}</td>
                <td>{position.notes || '-'}</td>
                <td>
                  <button onClick={() => setEditingId(position.id)}>Edit</button>
                  <button onClick={() => handleDelete(position.id)}>Delete</button>
                </td>
              </>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

### 4. Add Position Form

```typescript
const AddPositionModal = ({ onClose, onSuccess }: {
  onClose: () => void;
  onSuccess: () => void;
}) => {
  const [formData, setFormData] = useState<AddPortfolioPositionRequest>({
    ticker: '',
    quantity: 0,
    entry_price: 0,
    entry_date: new Date().toISOString().split('T')[0],
    notes: ''
  });

  const [positionSize, setPositionSize] = useState(0);

  useEffect(() => {
    setPositionSize(formData.quantity * formData.entry_price);
  }, [formData.quantity, formData.entry_price]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addPosition(formData);
      onSuccess();
    } catch (error) {
      alert(`Failed to add position: ${error.message}`);
    }
  };

  return (
    <Modal onClose={onClose}>
      <h2>Add Position</h2>
      <form onSubmit={handleSubmit}>
        <Input
          label="Ticker"
          value={formData.ticker}
          onChange={(ticker) => setFormData({...formData, ticker: ticker.toUpperCase()})}
          required
          maxLength={10}
        />

        <Input
          label="Quantity"
          type="number"
          value={formData.quantity}
          onChange={(quantity) => setFormData({...formData, quantity: parseFloat(quantity)})}
          required
          min={0.01}
          step={0.01}
        />

        <Input
          label="Entry Price"
          type="number"
          value={formData.entry_price}
          onChange={(entry_price) => setFormData({...formData, entry_price: parseFloat(entry_price)})}
          required
          min={0.01}
          step={0.01}
        />

        <div className="position-size-preview">
          Position Size: ${positionSize.toLocaleString()}
        </div>

        <Input
          label="Entry Date"
          type="date"
          value={formData.entry_date}
          onChange={(entry_date) => setFormData({...formData, entry_date})}
          required
        />

        <TextArea
          label="Notes (Optional)"
          value={formData.notes}
          onChange={(notes) => setFormData({...formData, notes})}
          maxLength={500}
        />

        <div className="form-actions">
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="submit">Add Position</button>
        </div>
      </form>
    </Modal>
  );
};
```

### 5. Portfolio Analysis Component

```typescript
const AnalysisModal = ({ positions, onClose }: {
  positions: PortfolioPositionResponse[];
  onClose: () => void;
}) => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PortfolioAnalysisResponse | null>(null);
  const [request, setRequest] = useState<PortfolioAnalysisRequest>({
    strategy: 'bollinger_bands_strategy',
    start_date: '',
    end_date: '',
    interval: '1d',
    parameters: {}
  });

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const analysis = await analyzePortfolio(request);
      setResults(analysis);
    } catch (error) {
      alert(`Analysis failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal onClose={onClose} size="large">
      <h2>Portfolio Analysis</h2>

      {!results ? (
        <AnalysisForm
          request={request}
          onChange={setRequest}
          onSubmit={handleAnalyze}
          loading={loading}
          positions={positions}
        />
      ) : (
        <AnalysisResults results={results} />
      )}
    </Modal>
  );
};
```

### 6. Analysis Results Display

```typescript
const AnalysisResults = ({ results }: { results: PortfolioAnalysisResponse }) => (
  <div className="analysis-results">
    {/* Weighted Portfolio Metrics */}
    <section className="weighted-metrics">
      <h3>Portfolio Performance (Weighted)</h3>
      <div className="metrics-grid">
        <MetricCard
          label="Portfolio Value"
          value={`$${results.total_portfolio_value.toLocaleString()}`}
        />
        <MetricCard
          label="Weighted PnL"
          value={`$${results.weighted_pnl.toLocaleString()}`}
          trend={results.weighted_pnl >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label="Weighted Return"
          value={`${results.weighted_return_pct.toFixed(2)}%`}
          trend={results.weighted_return_pct >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label="Weighted Sharpe"
          value={results.weighted_sharpe_ratio?.toFixed(2) || 'N/A'}
        />
        <MetricCard
          label="Weighted Max DD"
          value={`${results.weighted_max_drawdown?.toFixed(2)}%`}
        />
        <MetricCard
          label="Win Rate"
          value={`${results.portfolio_statistics.win_rate.toFixed(1)}%`}
        />
      </div>
    </section>

    {/* Portfolio Statistics */}
    <section className="portfolio-stats">
      <h3>Portfolio Statistics</h3>
      <StatsGrid>
        <StatRow label="Avg Position PnL" value={`$${results.portfolio_statistics.avg_position_pnl.toFixed(2)}`} />
        <StatRow label="Median Position PnL" value={`$${results.portfolio_statistics.median_position_pnl.toFixed(2)}`} />
        <StatRow label="Std Dev PnL" value={`$${results.portfolio_statistics.std_position_pnl.toFixed(2)}`} />
        <StatRow label="Min PnL" value={`$${results.portfolio_statistics.min_position_pnl.toFixed(2)}`} />
        <StatRow label="Max PnL" value={`$${results.portfolio_statistics.max_position_pnl.toFixed(2)}`} />
        <StatRow label="Profitable Positions" value={`${results.portfolio_statistics.profitable_positions}/${results.positions_analyzed}`} />
        <StatRow label="Avg Trades/Position" value={results.portfolio_statistics.avg_trades_per_position.toFixed(2)} />
      </StatsGrid>
    </section>

    {/* Individual Position Results */}
    <section className="position-results">
      <h3>Position Results</h3>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Weight</th>
            <th>PnL</th>
            <th>Return</th>
            <th>Trades</th>
            <th>Win/Loss</th>
            <th>Sharpe</th>
            <th>Max DD</th>
          </tr>
        </thead>
        <tbody>
          {results.position_results.map(pos => (
            <tr key={pos.position_id}>
              <td>{pos.ticker}</td>
              <td>{pos.weight}%</td>
              <td className={pos.pnl >= 0 ? 'positive' : 'negative'}>
                ${pos.pnl.toFixed(2)}
              </td>
              <td className={pos.return_pct >= 0 ? 'positive' : 'negative'}>
                {pos.return_pct}%
              </td>
              <td>{pos.total_trades}</td>
              <td>{pos.winning_trades}/{pos.losing_trades}</td>
              <td>{pos.sharpe_ratio?.toFixed(2) || 'N/A'}</td>
              <td>{pos.max_drawdown?.toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>

    {/* Visualizations */}
    <section className="visualizations">
      <h3>Portfolio Breakdown</h3>
      <PieChart
        data={results.position_results.map(p => ({
          label: p.ticker,
          value: p.weight
        }))}
        title="Portfolio Allocation"
      />

      <BarChart
        data={results.position_results.map(p => ({
          label: p.ticker,
          value: p.pnl
        }))}
        title="Position PnL Distribution"
      />
    </section>
  </div>
);
```

## Understanding Weighted Calculations

### How Weighting Works

When you run a portfolio analysis, each position is weighted by its proportion of the total portfolio value:

```
Weight = Position Size / Total Portfolio Value
```

**Example Portfolio:**
- AAPL: $15,000 (30% of portfolio)
- MSFT: $25,000 (50% of portfolio)
- GOOGL: $10,000 (20% of portfolio)
- Total: $50,000

**If strategy returns are:**
- AAPL: +5%
- MSFT: +3%
- GOOGL: -2%

**Weighted return calculation:**
```
Weighted Return = (0.30 × 5%) + (0.50 × 3%) + (0.20 × -2%)
                = 1.5% + 1.5% - 0.4%
                = 2.6%
```

This gives you a realistic portfolio-level return that accounts for position sizes.

## Data Persistence

All portfolio positions are stored in SQLite database:

**Database Schema:**
```sql
CREATE TABLE portfolio_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quantity REAL NOT NULL,
    entry_price REAL NOT NULL,
    entry_date TEXT NOT NULL,
    position_size REAL NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**Position Size Auto-Calculation:**
- Automatically calculated: `position_size = quantity × entry_price`
- Updated automatically when quantity or entry_price changes
- No manual input required

## Error Handling

```typescript
// Empty portfolio check
try {
  const analysis = await analyzePortfolio(request);
} catch (error) {
  if (error.message.includes('Portfolio is empty')) {
    alert('Please add positions to your portfolio before running analysis');
  } else if (error.message.includes('Strategy') && error.message.includes('not found')) {
    alert('Invalid strategy selected');
  } else {
    alert(`Analysis failed: ${error.message}`);
  }
}

// Position not found
try {
  await deletePosition(999);
} catch (error) {
  if (error.status === 404) {
    alert('Position not found');
  }
}
```

## Best Practices

1. **Validate inputs** before submission (positive numbers, valid dates)
2. **Show position size preview** when entering quantity/price
3. **Confirm deletions** to prevent accidental data loss
4. **Cache portfolio data** to reduce API calls
5. **Show loading states** during analysis (can take 1-2 minutes for multiple positions)
6. **Highlight weighted vs unweighted** metrics clearly
7. **Export results** to CSV for further analysis
8. **Persist selected strategy** for quick re-analysis

## Performance Tips

- Portfolio analysis time: ~30-60 seconds per position
- For 5 positions: expect 2-5 minutes total
- Show progress indicator: "Analyzing AAPL... (1/5)"
- Consider batch loading for large portfolios
- Cache strategy parameters for quick re-runs

## Example Complete Flow

```typescript
// 1. Add positions
await addPosition({ ticker: "AAPL", quantity: 100, entry_price: 150, entry_date: "2024-01-01" });
await addPosition({ ticker: "MSFT", quantity: 50, entry_price: 300, entry_date: "2024-01-01" });
await addPosition({ ticker: "GOOGL", quantity: 75, entry_price: 140, entry_date: "2024-01-01" });

// 2. View portfolio
const portfolio = await getPortfolio();
// Returns: { total_positions: 3, total_portfolio_value: 40500 }

// 3. Run analysis
const analysis = await analyzePortfolio({
  strategy: "bollinger_bands_strategy",
  start_date: "2024-01-01",
  end_date: "2024-03-31",
  parameters: { period: 20, devfactor: 2.0 }
});

// 4. View weighted results
console.log(`Weighted PnL: $${analysis.weighted_pnl}`);
console.log(`Weighted Return: ${analysis.weighted_return_pct}%`);

// 5. Check individual positions
analysis.position_results.forEach(pos => {
  console.log(`${pos.ticker}: ${pos.weight}% weight, ${pos.return_pct}% return`);
});
```

## Testing Checklist

- [ ] Add position with all fields
- [ ] Add position with only required fields
- [ ] Position size auto-calculates correctly
- [ ] View portfolio shows all positions
- [ ] Total portfolio value is accurate
- [ ] Update position recalculates position_size
- [ ] Delete position removes from database
- [ ] Analysis with empty portfolio shows error
- [ ] Analysis returns weighted metrics
- [ ] Individual position results match weights
- [ ] Portfolio statistics are accurate
- [ ] Negative PnL displays correctly
- [ ] Large position sizes format correctly

## Integration with Existing Features

### From Backtest Results
Add "Save to Portfolio" button:
```typescript
<button onClick={() => saveToPortfolio(backtestResult)}>
  Add {ticker} to Portfolio
</button>
```

### From Presets
Add "Add to Portfolio" action:
```typescript
<button onClick={() => {
  setShowAddPositionModal(true);
  setPreFilledTicker(preset.ticker);
}}>
  Add to Portfolio
</button>
```

This comprehensive portfolio tracking system provides powerful insights into strategy performance across diversified positions with proper weighting and detailed analytics.
