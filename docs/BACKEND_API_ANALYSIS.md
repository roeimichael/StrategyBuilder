# Backend API Analysis & Recommendations

Based on the frontend API documentation provided, here's a comprehensive analysis of current usage, gaps, and recommendations.

---

## 🚨 Critical Issues

### 1. **Preset API Mismatch** (HIGH PRIORITY)

**Problem:** The frontend documentation shows they're still expecting `ticker` and `interval` in preset creation:

```json
// What frontend is sending:
{
  "name": "My ADX Strategy",
  "ticker": "TEMPLATE",  // ❌ Using workaround
  "strategy": "adx_strategy",
  "parameters": {...},
  "interval": "1d",      // ❌ No longer needed
  "notes": "..."
}
```

**Backend Reality:** We just modified presets to be strategy-only (no ticker/interval).

**Impact:** Frontend will get 422 validation errors when creating presets.

**Solution Required:**
- Update frontend to remove `ticker` and `interval` from POST /presets
- Update frontend to ADD `ticker` and `interval` as query params to POST /presets/{id}/backtest
  ```
  POST /presets/5/backtest?ticker=AAPL&interval=1d&start_date=...
  ```

**Frontend Developer Instructions:**
```typescript
// ✅ NEW: Create preset (strategy-only)
POST /presets
{
  "name": "My ADX Strategy",
  "strategy": "adx_strategy",
  "parameters": {"adx_period": 14, "adx_threshold": 25},
  "notes": "Good for trending markets"
}

// ✅ NEW: Apply preset to any ticker
POST /presets/5/backtest?ticker=AAPL&interval=1d&start_date=2024-01-01&end_date=2025-01-01&cash=10000
```

---

### 2. **Portfolio API Not Discovered** (HIGH PRIORITY)

**Problem:** Frontend is manually running individual backtests for portfolio simulation and proposing a new `/portfolio/simulate` endpoint.

**Backend Reality:** We already built comprehensive portfolio management with weighted analysis!

**Unused Portfolio Endpoints:**
- ✅ `POST /portfolio` - Add position (ticker, quantity, entry_price, entry_date)
- ✅ `GET /portfolio` - Get all positions with total portfolio value
- ✅ `GET /portfolio/{id}` - Get single position
- ✅ `PUT /portfolio/{id}` - Update position
- ✅ `DELETE /portfolio/{id}` - Remove position
- ✅ `POST /portfolio/analyze` - Run weighted portfolio analysis with strategy

**What They Need:**
```typescript
// 1. Add positions to portfolio
POST /portfolio
{
  "ticker": "AAPL",
  "quantity": 100,
  "entry_price": 150.50,
  "entry_date": "2024-01-15",
  "notes": "Initial tech position"
}
// Response: position_size auto-calculated (100 × 150.50 = $15,050)

// 2. Run strategy analysis across entire portfolio (weighted by position size)
POST /portfolio/analyze
{
  "strategy": "adx_strategy",
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "interval": "1d",
  "parameters": {"adx_period": 14}
}
// Returns weighted PnL, per-position results, macro statistics
```

**Key Features They're Missing:**
- Automatic position_size calculation (quantity × entry_price)
- Weighted portfolio analysis (by position size, not equal weight)
- Per-position breakdown with portfolio-level aggregation
- Portfolio statistics (avg/median/std PnL, profitability rate, etc.)

**Action Required:** Provide frontend developer with the Portfolio API guide at `docs/PORTFOLIO_TRACKER_FRONTEND_GUIDE.md`

---

## ✅ What's Working Well

### Endpoints Being Used Correctly:
1. **Health & Connection**
   - ✅ GET /health
   - ✅ GET /

2. **Backtest Tab**
   - ✅ GET /strategies
   - ✅ GET /strategies/{name}
   - ✅ POST /backtest
   - ✅ POST /market-data

3. **Optimize Tab**
   - ✅ POST /optimize

4. **Market Scan Tab**
   - ✅ POST /market-scan (with full stock_results and macro_statistics)

5. **Run History Tab**
   - ✅ GET /runs (with pagination)
   - ✅ GET /runs/{id}
   - ✅ POST /runs/{id}/replay

6. **Watchlist Tab**
   - ✅ POST /watchlist
   - ✅ GET /watchlist
   - ✅ PATCH /watchlist/{id}
   - ✅ DELETE /watchlist/{id}
   - ✅ POST /snapshot

7. **Live Monitor Tab**
   - ✅ POST /market-data

---

## 🔧 Improvements Needed

### 1. **Server-Side Partial String Matching** (MEDIUM PRIORITY)

**Current:** Frontend does client-side partial matching for ticker filter in runs:
```typescript
// Frontend code:
runs.filter(run => run.ticker.toLowerCase().includes(searchTerm.toLowerCase()))
```

**Problem:** Loads all runs then filters client-side. Inefficient for large datasets.

**Recommendation:** Add server-side LIKE query support

**Backend Change:**
```python
# In src/data/run_repository.py - list_runs()
if ticker:
    # Current: exact match
    query += ' AND ticker = ?'

    # Proposed: partial match
    query += ' AND ticker LIKE ?'
    params.append(f'%{ticker}%')
```

**Benefits:**
- Reduces data transfer
- Faster filtering for large datasets
- Consistent behavior across tabs

---

### 2. **Strategy Descriptions Missing** (LOW PRIORITY)

**Current Response:**
```json
{
  "module": "adx_strategy",
  "class_name": "adx_strat",
  "description": ""  // ❌ Empty
}
```

**Problem:** Frontend wants to show strategy descriptions in UI.

**Recommendation:** Add docstrings to strategy classes

**Example:**
```python
# In src/strategies/adx_strategy.py
class adx_strat(Strategy):
    """
    ADX-based trend following strategy.

    Enters long positions when ADX indicates strong trend (above threshold)
    and Plus DI > Minus DI. Uses ATR-based stops for risk management.
    Best for trending markets with clear directional moves.
    """
```

**Backend Change:** Extract docstring in `StrategyService.get_strategy_info()`

---

### 3. **GET /presets/{id} Endpoint** (LOW PRIORITY)

**Status:** Endpoint exists but not documented in frontend API docs.

**Current:** Frontend only uses GET /presets (list all)

**Use Case:** When displaying preset details before running backtest

**Recommendation:** Document this endpoint for frontend use

```
GET /presets/5

Response:
{
  "id": 5,
  "name": "My ADX Strategy",
  "strategy": "adx_strategy",
  "parameters": {"adx_period": 14, "adx_threshold": 25},
  "notes": "Good for trending markets",
  "created_at": "2026-01-20T16:00:00"
}
```

---

### 4. **Market Scan Progress Updates** (NICE TO HAVE)

**Current:** 10-minute request with no progress feedback

**Frontend Request:** Server-Sent Events (SSE) or WebSocket for real-time progress

**Current UX:** Indeterminate loading spinner

**Proposed Implementation:**
```python
# Option 1: SSE (simpler)
@app.get("/market-scan/stream")
async def market_scan_stream(request: MarketScanRequest):
    async def event_generator():
        for i, ticker in enumerate(tickers):
            # Run backtest
            result = run_backtest(ticker, ...)

            # Yield progress event
            yield f"data: {json.dumps({
                'progress': (i + 1) / len(tickers),
                'current_ticker': ticker,
                'completed': i + 1,
                'total': len(tickers)
            })}\n\n"

        # Final result
        yield f"data: {json.dumps({
            'complete': True,
            'results': final_results
        })}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Benefits:**
- Show "Scanning AAPL... (145/503)" progress
- Better UX for long-running operations
- Can cancel if taking too long

**Complexity:** Moderate. Requires SSE client implementation in frontend.

---

## 📊 Unused Endpoints

These endpoints exist but aren't being used:

### 1. **GET /watchlist/{id}**
- **Exists:** Yes
- **Used:** No (frontend only uses GET /watchlist to list all)
- **Recommendation:** Keep for consistency with other endpoints

### 2. **GET /presets/{id}**
- **Exists:** Yes
- **Used:** No (frontend only uses GET /presets to list all)
- **Recommendation:** Document for frontend use (see improvement #3)

---

## 🗑️ Nothing to Remove

All built endpoints have valid use cases. Even if not currently used by frontend, they provide:
- REST API consistency (GET /resource and GET /resource/{id} pattern)
- Potential future features
- Third-party integration capabilities

---

## 📋 Action Items Summary

### Immediate (Required for Frontend to Work):

1. **Communicate Preset API Changes**
   - Frontend must remove `ticker` and `interval` from POST /presets
   - Frontend must add `ticker` and `interval` as query params to POST /presets/{id}/backtest
   - Provide updated examples

2. **Share Portfolio API Documentation**
   - Send `docs/PORTFOLIO_TRACKER_FRONTEND_GUIDE.md` to frontend developer
   - Explain weighted analysis concept
   - Show how it replaces their proposed `/portfolio/simulate` endpoint

### Short-Term (Nice to Have):

3. **Add Server-Side Partial String Matching**
   - Update `run_repository.list_runs()` to use LIKE queries
   - Test with large datasets

4. **Add Strategy Descriptions**
   - Add docstrings to all strategy classes
   - Extract in `StrategyService.get_strategy_info()`

5. **Document GET /presets/{id}**
   - Add to frontend API documentation
   - Show use case for preset detail view

### Long-Term (Future Enhancement):

6. **Market Scan Progress Updates**
   - Implement SSE or WebSocket for real-time progress
   - Show ticker-by-ticker progress
   - Add cancel capability

---

## 🎯 Expected Outcomes

After implementing immediate actions:
- ✅ Frontend can create strategy-only presets
- ✅ Presets are reusable across any ticker
- ✅ Portfolio tab uses proper weighted analysis
- ✅ Position management with auto-calculated sizing
- ✅ Per-position and portfolio-level metrics

After short-term improvements:
- ✅ Faster run history filtering
- ✅ Strategy descriptions in UI
- ✅ Better preset detail views

After long-term enhancements:
- ✅ Real-time market scan progress
- ✅ Ability to cancel long-running scans
- ✅ Better UX for lengthy operations

---

## 📝 Communication Template for Frontend Developer

```
Hi [Frontend Developer],

Based on your API documentation, I've identified two critical updates:

1. **Preset API Changed** (Breaking Change)
   - Presets are now strategy-only (no ticker/interval)
   - When creating: Remove ticker/interval fields
   - When running: Add ticker/interval as query params
   - See updated examples in attached document

2. **Portfolio API Available** (New Feature)
   - We already built the portfolio management API you proposed!
   - Includes position management and weighted analysis
   - See complete guide: docs/PORTFOLIO_TRACKER_FRONTEND_GUIDE.md
   - No need for manual per-ticker simulation

Additional improvements:
- GET /presets/{id} is available for preset details
- Consider server-side filtering for runs (I can add LIKE support)
- Strategy descriptions coming soon

Let me know if you need clarification on any endpoints!
```

---

## Summary

| Category | Count | Priority |
|----------|-------|----------|
| Critical Issues | 2 | 🚨 High |
| Improvements Needed | 4 | 🔧 Medium-Low |
| Unused Endpoints | 2 | ℹ️ Info Only |
| Endpoints to Remove | 0 | N/A |
| **Working Well** | **20+** | ✅ Good |

**Overall Assessment:** The API is well-designed and mostly working. The two critical issues are communication gaps that can be quickly resolved. Once the frontend developer is aware of:
1. The new preset API structure
2. The existing portfolio API

...they should be able to utilize the full backend capabilities effectively.
