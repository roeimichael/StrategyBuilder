# Market Scan Progress Feedback Implementation Guide

## Overview

This guide explains how to implement real-time progress feedback for the market scan endpoint using **Server-Sent Events (SSE)**. This will allow the frontend to display a progress bar showing how many stocks have been processed out of the total.

---

## Problem Statement

**Current Situation:**
- Market scan takes 5-15 minutes to complete
- Frontend has no visibility into progress
- User sees loading spinner with no indication of progress
- Cannot tell if request is stuck or still processing

**Desired Solution:**
- Real-time progress updates: "Processing stock 150/503 (29.8%)"
- Live feedback on successes/failures
- Ability to show progress bar in frontend
- Updates every few stocks (e.g., every 5 stocks = ~1%)

---

## Why Server-Sent Events (SSE)?

### SSE vs Other Options

| Technology | Use Case | Pros | Cons |
|------------|----------|------|------|
| **Server-Sent Events (SSE)** | Server → Client updates | Simple, HTTP-based, auto-reconnect, built-in browser support | One-way only (server to client) |
| **WebSockets** | Bi-directional communication | Full duplex, low latency | More complex, requires WS protocol, connection overhead |
| **Polling** | Client checks periodically | Simple to implement | Inefficient, high latency, server load |
| **Long Polling** | Client waits for updates | Better than polling | Still inefficient, complex error handling |

**SSE is the best choice because:**
1. ✅ We only need **server → client** updates (one-way)
2. ✅ Built into browsers via `EventSource` API
3. ✅ Works over HTTP/HTTPS (no special protocol needed)
4. ✅ Auto-reconnects on disconnect
5. ✅ Simple to implement in FastAPI and frontend
6. ✅ Lower overhead than WebSockets for this use case

---

## Architecture Overview

```
┌─────────────┐                  ┌─────────────┐
│  Frontend   │                  │   Backend   │
│             │                  │   (FastAPI) │
└─────────────┘                  └─────────────┘
       │                                │
       │  POST /market-scan/stream      │
       │─────────────────────────────>  │
       │                                │
       │  EventSource Connection        │ Start market scan
       │  <SSE Stream Open>             │ ─────────────────>
       │                                │
       │  data: {"progress": 1, ...}    │ Process stock 1
       │  <─────────────────────────────│
       │                                │
       │  data: {"progress": 10, ...}   │ Process stock 10
       │  <─────────────────────────────│
       │                                │
       │  data: {"progress": 50, ...}   │ Process stock 50
       │  <─────────────────────────────│
       │                                │
       │        ... continues ...        │
       │                                │
       │  data: {"progress": 503, ...}  │ Process stock 503
       │  <─────────────────────────────│
       │                                │
       │  data: {"done": true, ...}     │ Complete
       │  <─────────────────────────────│
       │                                │
       │  <SSE Stream Closed>           │
       │                                │
```

---

## Backend Implementation (FastAPI + SSE)

### Step 1: Add SSE Response Class

FastAPI doesn't have built-in SSE support, so we use `StreamingResponse`:

```python
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator

# In src/api/main.py or a new sse_utils.py file
async def event_generator(data_stream) -> AsyncGenerator[str, None]:
    """
    Convert data stream to SSE format

    SSE format:
    data: {"key": "value"}\n\n
    """
    async for data in data_stream:
        # Format as SSE event
        yield f"data: {json.dumps(data)}\n\n"
```

### Step 2: Modify Market Scan to Support Streaming

We'll create a **new streaming version** of the market scan that yields progress updates:

```python
# In src/services/backtest_service.py

async def market_scan_streaming(
    self,
    strategy_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = BacktestConfig.DEFAULT_INTERVAL,
    cash: float = BacktestConfig.DEFAULT_CASH,
    parameters: Optional[Dict[str, Union[int, float]]] = None
):
    """
    Market scan with streaming progress updates

    Yields progress updates as stocks are processed
    """
    from src.utils.sp500_tickers import get_sp500_tickers
    import numpy as np
    import time

    tickers = get_sp500_tickers()
    total_stocks = len(tickers)

    # Initialize accumulators
    stock_results = []
    total_pnl = 0.0
    total_trades = 0
    winning_trades = 0
    losing_trades = 0
    failed_stocks = []

    start_time = time.time()

    # Yield initial progress
    yield {
        'type': 'start',
        'total_stocks': total_stocks,
        'message': f'Starting market scan with {total_stocks} stocks'
    }

    for idx, ticker in enumerate(tickers, 1):
        stock_start = time.time()

        try:
            # Run backtest for this stock
            request = BacktestRequest(
                ticker=ticker,
                strategy=strategy_name,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                cash=cash,
                parameters=parameters
            )

            response = self.run_backtest(request, save_run=False)

            # Process results
            stock_result = {
                'ticker': ticker,
                'pnl': round(response.pnl, 2),
                'return_pct': round(response.return_pct, 2),
                'total_trades': response.total_trades,
                # ... other fields
            }
            stock_results.append(stock_result)

            total_pnl += response.pnl
            total_trades += response.total_trades

            stock_elapsed = time.time() - stock_start

            # Yield progress update every 5 stocks (or every stock if you want)
            if idx % 5 == 0 or idx == total_stocks:
                progress_pct = (idx / total_stocks) * 100
                elapsed_total = time.time() - start_time
                eta_seconds = (elapsed_total / idx) * (total_stocks - idx)

                yield {
                    'type': 'progress',
                    'current': idx,
                    'total': total_stocks,
                    'progress_pct': round(progress_pct, 1),
                    'ticker': ticker,
                    'stock_time': round(stock_elapsed, 2),
                    'elapsed_time': round(elapsed_total, 1),
                    'eta_seconds': round(eta_seconds, 1),
                    'successful': len(stock_results),
                    'failed': len(failed_stocks),
                    'current_pnl': round(total_pnl, 2)
                }

        except Exception as e:
            failed_stocks.append({
                'ticker': ticker,
                'error': str(e)
            })

            # Yield error update
            if idx % 5 == 0 or idx == total_stocks:
                yield {
                    'type': 'error',
                    'ticker': ticker,
                    'error': str(e),
                    'current': idx,
                    'total': total_stocks
                }

    # Calculate final statistics
    # ... (same as current market_scan method)

    # Yield final results
    yield {
        'type': 'complete',
        'total_stocks': total_stocks,
        'successful': len(stock_results),
        'failed': len(failed_stocks),
        'total_pnl': round(total_pnl, 2),
        'total_time': round(time.time() - start_time, 1),
        'stock_results': stock_results,
        'macro_statistics': macro_statistics,
        # ... full results
    }
```

### Step 3: Add Streaming Endpoint

```python
# In src/api/main.py

@app.post("/market-scan/stream")
async def market_scan_stream(request: MarketScanRequest):
    """
    Market scan with real-time progress updates via SSE

    Returns a stream of progress events as stocks are processed.

    Example response events:
    - Start: {"type": "start", "total_stocks": 503}
    - Progress: {"type": "progress", "current": 50, "total": 503, "progress_pct": 9.9}
    - Error: {"type": "error", "ticker": "XYZ", "error": "..."}
    - Complete: {"type": "complete", "stock_results": [...]}
    """
    try:
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")

        async def event_stream():
            """Generate SSE events from market scan"""
            async for progress_data in backtest_service.market_scan_streaming(
                strategy_name=request.strategy,
                start_date=request.start_date,
                end_date=request.end_date,
                interval=request.interval,
                cash=request.cash,
                parameters=request.parameters
            ):
                # Format as SSE
                yield f"data: {json.dumps(progress_data)}\n\n"

                # Small delay to prevent overwhelming client
                await asyncio.sleep(0.01)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market scan failed: {str(e)}")
```

### Step 4: Keep Non-Streaming Endpoint

**Important**: Keep the original `/market-scan` endpoint for backward compatibility. Clients can choose:
- `/market-scan` - Traditional request/response (no progress)
- `/market-scan/stream` - SSE with real-time progress

---

## Frontend Implementation

### Step 1: Connect to SSE Stream

```typescript
interface ProgressUpdate {
  type: 'start' | 'progress' | 'error' | 'complete';
  current?: number;
  total?: number;
  progress_pct?: number;
  ticker?: string;
  stock_time?: number;
  elapsed_time?: number;
  eta_seconds?: number;
  successful?: number;
  failed?: number;
  current_pnl?: number;
  error?: string;
  stock_results?: any[];
  macro_statistics?: any;
  total_time?: number;
}

const runMarketScanWithProgress = async (
  strategy: string,
  parameters: Record<string, number>
) => {
  const requestBody = {
    strategy,
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    interval: '1d',
    cash: 10000,
    parameters
  };

  // POST request to initiate scan and get EventSource URL
  const response = await fetch('http://localhost:8000/market-scan/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });

  // Note: EventSource doesn't support POST directly,
  // so we need a hybrid approach (see Alternative Approach below)
};
```

### Alternative Approach: Two-Step Process

Since `EventSource` only supports GET requests, we use a two-step process:

**Step 1: Initiate scan and get job ID**
```typescript
// POST to start the scan
const response = await fetch('http://localhost:8000/market-scan/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestBody)
});

const { job_id } = await response.json();
```

**Step 2: Connect to SSE stream for that job**
```typescript
// Connect to SSE stream with job ID
const eventSource = new EventSource(
  `http://localhost:8000/market-scan/stream/${job_id}`
);

eventSource.onmessage = (event) => {
  const data: ProgressUpdate = JSON.parse(event.data);

  switch (data.type) {
    case 'start':
      console.log(`Starting scan of ${data.total} stocks`);
      setProgress(0);
      break;

    case 'progress':
      console.log(`Progress: ${data.current}/${data.total} (${data.progress_pct}%)`);
      console.log(`ETA: ${data.eta_seconds}s`);
      setProgress(data.progress_pct);
      setCurrentStock(data.ticker);
      setCurrentPnL(data.current_pnl);
      break;

    case 'error':
      console.error(`Failed: ${data.ticker} - ${data.error}`);
      break;

    case 'complete':
      console.log('Scan complete!');
      setResults(data.stock_results);
      setMacroStats(data.macro_statistics);
      eventSource.close();
      break;
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

### Step 3: React Component with Progress Bar

```tsx
import React, { useState } from 'react';

const MarketScanWithProgress: React.FC = () => {
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStock, setCurrentStock] = useState('');
  const [eta, setEta] = useState(0);
  const [currentPnL, setCurrentPnL] = useState(0);
  const [results, setResults] = useState(null);

  const startScan = async () => {
    setScanning(true);
    setProgress(0);

    // Step 1: Start scan
    const response = await fetch('http://localhost:8000/market-scan/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        strategy: 'bollinger_bands_strategy',
        parameters: { period: 20, devfactor: 2.0 }
      })
    });

    const { job_id } = await response.json();

    // Step 2: Connect to SSE
    const eventSource = new EventSource(
      `http://localhost:8000/market-scan/stream/${job_id}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'progress') {
        setProgress(data.progress_pct);
        setCurrentStock(data.ticker);
        setEta(data.eta_seconds);
        setCurrentPnL(data.current_pnl);
      } else if (data.type === 'complete') {
        setResults(data);
        setScanning(false);
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      setScanning(false);
      eventSource.close();
    };
  };

  return (
    <div>
      <button onClick={startScan} disabled={scanning}>
        {scanning ? 'Scanning...' : 'Start Market Scan'}
      </button>

      {scanning && (
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>

          <div className="progress-info">
            <p>Progress: {progress.toFixed(1)}%</p>
            <p>Current: {currentStock}</p>
            <p>ETA: {Math.floor(eta / 60)}m {eta % 60}s</p>
            <p>Current PnL: ${currentPnL.toFixed(2)}</p>
          </div>
        </div>
      )}

      {results && (
        <div className="results">
          <h2>Scan Complete!</h2>
          <p>Total PnL: ${results.total_pnl}</p>
          {/* Display full results */}
        </div>
      )}
    </div>
  );
};
```

---

## Implementation Strategy

### Option A: Simple Job-Based Approach (Recommended)

**Pros:**
- ✅ Works with existing POST requests
- ✅ Cleaner separation of concerns
- ✅ Easy to add job management/history later
- ✅ Can support multiple concurrent scans

**Cons:**
- ❌ Requires job storage (in-memory dict is fine)
- ❌ Slightly more complex (two endpoints)

**Endpoints:**
1. `POST /market-scan/start` → Returns `{job_id}`
2. `GET /market-scan/stream/{job_id}` → SSE stream

### Option B: Direct SSE Endpoint

**Pros:**
- ✅ Simpler (one endpoint)
- ✅ No job management needed

**Cons:**
- ❌ Cannot use POST with EventSource
- ❌ Must encode parameters in URL query string
- ❌ URL length limits with complex parameters

### Option C: Hybrid Polling (Fallback)

If SSE is too complex initially, use polling:

```typescript
// Start scan
const { job_id } = await startScan();

// Poll for progress
const interval = setInterval(async () => {
  const progress = await fetch(`/market-scan/status/${job_id}`);
  const data = await progress.json();

  if (data.complete) {
    clearInterval(interval);
    setResults(data.results);
  } else {
    setProgress(data.progress_pct);
  }
}, 1000); // Poll every second
```

**Pros:**
- ✅ Very simple to implement
- ✅ Works everywhere

**Cons:**
- ❌ Higher latency (1s between updates)
- ❌ More server requests
- ❌ Less efficient than SSE

---

## Performance Considerations

### Update Frequency

**Don't send an event for every stock:**
```python
# ❌ BAD: 503 events (one per stock)
for ticker in tickers:
    process_stock()
    yield progress  # Every single stock

# ✅ GOOD: ~100 events (every 5 stocks)
for idx, ticker in enumerate(tickers):
    process_stock()
    if idx % 5 == 0:  # Update every ~1%
        yield progress
```

**Why?**
- Reduces frontend render thrashing
- Lower network overhead
- Still provides smooth progress bar

### Buffering Issues

Some proxies (nginx, Apache) buffer SSE streams. Disable buffering:

```python
# In FastAPI response headers
headers={
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # Nginx
    "Connection": "keep-alive"
}
```

### Connection Timeouts

Long-running scans may hit timeout limits:

```python
# In nginx config
proxy_read_timeout 600s;  # 10 minutes

# In FastAPI (uvicorn)
uvicorn.run(app, timeout_keep_alive=600)
```

---

## Error Handling

### Backend: Handle Disconnects

```python
async def event_stream():
    try:
        async for progress in scan_generator():
            yield f"data: {json.dumps(progress)}\n\n"
    except asyncio.CancelledError:
        # Client disconnected
        logger.info("Client disconnected from SSE stream")
        # Clean up resources
    except Exception as e:
        # Send error event
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

### Frontend: Auto-Reconnect

```typescript
const connectSSE = (jobId: string, retries = 0) => {
  const eventSource = new EventSource(`/market-scan/stream/${jobId}`);

  eventSource.onerror = () => {
    eventSource.close();

    if (retries < 3) {
      console.log(`Reconnecting... (attempt ${retries + 1})`);
      setTimeout(() => connectSSE(jobId, retries + 1), 1000);
    } else {
      console.error('Max reconnection attempts reached');
    }
  };

  return eventSource;
};
```

---

## Testing SSE Endpoint

### Using curl

```bash
# Start scan and get job ID
JOB_ID=$(curl -X POST http://localhost:8000/market-scan/start \
  -H "Content-Type: application/json" \
  -d '{"strategy": "bollinger_bands_strategy"}' | jq -r '.job_id')

# Connect to SSE stream
curl -N http://localhost:8000/market-scan/stream/$JOB_ID
```

### Using Browser

```javascript
// In browser console
const es = new EventSource('http://localhost:8000/market-scan/stream/abc123');
es.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## Migration Path

### Phase 1: Add SSE Endpoint (Don't Break Existing)
- ✅ Add new `/market-scan/stream` endpoint
- ✅ Keep existing `/market-scan` endpoint unchanged
- ✅ Both work in parallel

### Phase 2: Frontend Gradual Adoption
- ✅ Add feature flag: `USE_SSE_PROGRESS`
- ✅ Default to old endpoint, opt-in to SSE
- ✅ Test with subset of users

### Phase 3: Full Migration
- ✅ Make SSE default
- ✅ Deprecate old endpoint (keep for 6 months)
- ✅ Eventually remove old endpoint

---

## Summary

### What You Need to Implement:

**Backend (FastAPI):**
1. ✅ Add `market_scan_streaming()` method to `BacktestService`
2. ✅ Add `POST /market-scan/start` endpoint (returns job_id)
3. ✅ Add `GET /market-scan/stream/{job_id}` endpoint (SSE)
4. ✅ Store active jobs in memory (`Dict[str, AsyncGenerator]`)

**Frontend (React):**
1. ✅ Add `EventSource` connection to SSE endpoint
2. ✅ Add progress bar component
3. ✅ Handle `start`, `progress`, `error`, `complete` events
4. ✅ Display: progress %, current stock, ETA, running PnL

### Benefits:

- ✅ Real-time progress feedback
- ✅ Better user experience (progress bar instead of spinner)
- ✅ Ability to cancel long-running scans
- ✅ Live PnL updates
- ✅ Identify stuck/slow stocks in real-time

### Estimated Implementation Time:

- Backend: 2-3 hours
- Frontend: 1-2 hours
- Testing: 1 hour
- **Total: 4-6 hours**

---

## Example Output

```
Progress: 5.0% (25/503) - Current: AAPL - ETA: 8m 45s - PnL: $1,250
Progress: 10.0% (50/503) - Current: MSFT - ETA: 7m 30s - PnL: $3,450
Progress: 20.0% (100/503) - Current: GOOGL - ETA: 6m 15s - PnL: $8,900
...
Complete! Total time: 9m 23s - Total PnL: $125,430
```

This provides much better UX than a blank loading spinner for 10 minutes!
