"""
StrategyBuilder FastAPI Backend
Provides RESTful API access to backtesting functionality, strategies, and market data analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import importlib
import inspect
import os
import sys
import io
from contextlib import redirect_stdout
import backtrader as bt
import yfinance as yf
import pandas as pd
import numpy as np

# Import core components
from run_strategy import Run_strategy
from strategy_skeleton import Strategy_skeleton
from parameters import Parameters

# Initialize FastAPI app
app = FastAPI(
    title="StrategyBuilder API",
    description="Algorithmic Trading Backtesting Platform API",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Pydantic Models ====================

class BacktestRequest(BaseModel):
    """Request model for running a backtest"""
    ticker: str = Field(..., description="Stock/crypto ticker symbol", example="AAPL")
    strategy_name: str = Field(..., description="Strategy class name", example="Bollinger_three")
    start_date: Optional[date] = Field(None, description="Start date for backtest (YYYY-MM-DD)")
    interval: str = Field("1h", description="Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Strategy parameters")

class PairBacktestRequest(BaseModel):
    """Request model for running a pair trading backtest"""
    ticker_x: str = Field(..., description="First ticker symbol", example="GLD")
    ticker_y: str = Field(..., description="Second ticker symbol", example="GDX")
    strategy_name: str = Field(..., description="Strategy class name", example="pair_trading_strategy")
    start_date: Optional[date] = Field(None, description="Start date for backtest")
    interval: str = Field("1h", description="Data interval")

class MarketDataRequest(BaseModel):
    """Request model for fetching market data"""
    ticker: str = Field(..., description="Ticker symbol", example="AAPL")
    period: str = Field("1mo", description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    interval: str = Field("1d", description="Data interval")

class ScanRequest(BaseModel):
    """Request model for scanning stocks"""
    tickers: List[str] = Field(..., description="List of ticker symbols to scan")
    condition: str = Field(..., description="Scanning condition/criteria")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")

class BacktestResult(BaseModel):
    """Response model for backtest results"""
    success: bool
    ticker: str
    strategy: str
    start_value: float
    end_value: float
    roi_percent: float
    total_return_percent: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    trades: int = 0
    output: str

# ==================== Helper Functions ====================

def get_default_parameters() -> Dict[str, Any]:
    """Get default strategy parameters"""
    return {
        'cash': Parameters.cash,
        'macd1': Parameters.macd1,
        'macd2': Parameters.macd2,
        'macdsig': Parameters.macdsig,
        'atrperiod': Parameters.atrperiod,
        'atrdist': Parameters.atrdist,
        'order_pct': Parameters.order_pct,
    }

def load_strategy_class(strategy_name: str):
    """Dynamically load strategy class by name"""
    # Search in root directory
    try:
        module = importlib.import_module(strategy_name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, bt.Strategy) and obj != bt.Strategy and obj != Strategy_skeleton:
                return obj
    except (ImportError, ModuleNotFoundError):
        pass

    # Search in strategies directory
    try:
        module = importlib.import_module(f'strategies.{strategy_name}')
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, bt.Strategy) and obj != bt.Strategy and obj != Strategy_skeleton:
                return obj
    except (ImportError, ModuleNotFoundError):
        pass

    raise ValueError(f"Strategy '{strategy_name}' not found")

def list_available_strategies() -> List[Dict[str, str]]:
    """List all available strategy classes"""
    strategies = []

    # Scan root directory
    for file in os.listdir('.'):
        if file.endswith('.py') and file not in ['api.py', 'run_strategy.py', 'run_strategy_2.py',
                                                   'strategy_skeleton.py', 'parameters.py', 'cmf_indicator.py']:
            module_name = file[:-3]
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, bt.Strategy) and obj != bt.Strategy and obj != Strategy_skeleton:
                        strategies.append({
                            'name': name,
                            'module': module_name,
                            'location': 'root'
                        })
            except Exception:
                pass

    # Scan strategies directory
    strategies_dir = 'strategies'
    if os.path.exists(strategies_dir):
        for file in os.listdir(strategies_dir):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]
                try:
                    module = importlib.import_module(f'strategies.{module_name}')
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, bt.Strategy) and obj != bt.Strategy and obj != Strategy_skeleton:
                            strategies.append({
                                'name': name,
                                'module': module_name,
                                'location': 'strategies'
                            })
                except Exception:
                    pass

    return strategies

# ==================== API Endpoints ====================

@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "name": "StrategyBuilder API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "strategies": "/strategies",
            "backtest": "/backtest",
            "pair_backtest": "/backtest/pair",
            "market_data": "/data/market",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/strategies")
def get_strategies():
    """List all available trading strategies"""
    try:
        strategies = list_available_strategies()
        return {
            "success": True,
            "count": len(strategies),
            "strategies": strategies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies/{strategy_name}")
def get_strategy_info(strategy_name: str):
    """Get detailed information about a specific strategy"""
    try:
        strategy_class = load_strategy_class(strategy_name)

        # Extract docstring and parameters
        docstring = inspect.getdoc(strategy_class) or "No description available"

        # Try to get parameters from __init__
        init_signature = inspect.signature(strategy_class.__init__)
        params = []
        for param_name, param in init_signature.parameters.items():
            if param_name not in ['self', 'args']:
                params.append({
                    'name': param_name,
                    'default': str(param.default) if param.default != inspect.Parameter.empty else None
                })

        return {
            "success": True,
            "strategy": {
                "name": strategy_class.__name__,
                "description": docstring,
                "parameters": params,
                "module": strategy_class.__module__
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest", response_model=BacktestResult)
def run_backtest(request: BacktestRequest):
    """Run a backtest for a single asset strategy"""
    try:
        # Load strategy
        strategy_class = load_strategy_class(request.strategy_name)

        # Prepare parameters
        params = get_default_parameters()
        if request.parameters:
            params.update(request.parameters)

        # Set start date
        start_date = request.start_date if request.start_date else (
            datetime.now().date() - relativedelta(years=1)
        )

        # Capture output
        output_buffer = io.StringIO()

        try:
            with redirect_stdout(output_buffer):
                # Run backtest
                runner = Run_strategy(params, strategy_class)
                runner.runstrat(request.ticker, start_date, request.interval)

                # Extract results
                start_value = params['cash']
                end_value = runner.cerebro.broker.getvalue()
                roi_percent = ((end_value / start_value) - 1) * 100

                # Get analyzers
                results = runner.cerebro.run()
                strat = results[0]

                sharpe = None
                max_dd = None

                try:
                    sharpe_analyzer = strat.analyzers.mysharpe.get_analysis()
                    sharpe = sharpe_analyzer.get('sharperatio', None)
                except:
                    pass

                try:
                    # Get drawdown from observers
                    max_dd = max([observer.maxdrawdown for observer in runner.cerebro.observers
                                 if hasattr(observer, 'maxdrawdown')], default=None)
                except:
                    pass

        except Exception as e:
            output_buffer.write(f"\nError during backtest: {str(e)}")
            raise

        output = output_buffer.getvalue()

        return BacktestResult(
            success=True,
            ticker=request.ticker,
            strategy=request.strategy_name,
            start_value=start_value,
            end_value=end_value,
            roi_percent=round(roi_percent, 2),
            total_return_percent=round(roi_percent, 2),
            sharpe_ratio=round(sharpe, 2) if sharpe else None,
            max_drawdown=round(max_dd, 2) if max_dd else None,
            output=output
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

@app.post("/backtest/pair")
def run_pair_backtest(request: PairBacktestRequest):
    """Run a backtest for pair trading strategy"""
    try:
        # Load strategy
        strategy_class = load_strategy_class(request.strategy_name)

        # Set start date
        start_date = request.start_date if request.start_date else (
            datetime.now().date() - relativedelta(years=1)
        )

        # Capture output
        output_buffer = io.StringIO()

        with redirect_stdout(output_buffer):
            # Import run_strategy_2 for pair trading
            from run_strategy_2 import Run_strategy as Run_strategy_2

            # Run backtest
            runner = Run_strategy_2(strategy_class)
            runner.runstrat(request.ticker_x, request.ticker_y, start_date, request.interval)

            # Extract results
            start_value = 10000  # Default from run_strategy_2
            end_value = runner.cerebro.broker.getvalue()
            roi_percent = ((end_value / start_value) - 1) * 100

        output = output_buffer.getvalue()

        return {
            "success": True,
            "ticker_x": request.ticker_x,
            "ticker_y": request.ticker_y,
            "strategy": request.strategy_name,
            "start_value": start_value,
            "end_value": end_value,
            "roi_percent": round(roi_percent, 2),
            "output": output
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pair backtest failed: {str(e)}")

@app.post("/data/market")
def get_market_data(request: MarketDataRequest):
    """Fetch historical market data for a ticker"""
    try:
        data = yf.download(
            request.ticker,
            period=request.period,
            interval=request.interval,
            progress=False
        )

        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {request.ticker}")

        # Convert to JSON-friendly format
        data_dict = data.reset_index().to_dict(orient='records')

        # Calculate basic statistics
        stats = {
            'mean': float(data['Close'].mean()) if 'Close' in data else None,
            'std': float(data['Close'].std()) if 'Close' in data else None,
            'min': float(data['Close'].min()) if 'Close' in data else None,
            'max': float(data['Close'].max()) if 'Close' in data else None,
            'volume_avg': float(data['Volume'].mean()) if 'Volume' in data else None,
        }

        return {
            "success": True,
            "ticker": request.ticker,
            "period": request.period,
            "interval": request.interval,
            "data_points": len(data_dict),
            "data": data_dict,
            "statistics": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@app.get("/data/ticker/{ticker}/info")
def get_ticker_info(ticker: str):
    """Get detailed information about a ticker"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract relevant info
        relevant_info = {
            'symbol': info.get('symbol'),
            'name': info.get('longName') or info.get('shortName'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'market_cap': info.get('marketCap'),
            'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'currency': info.get('currency'),
            'exchange': info.get('exchange'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
            'avg_volume': info.get('averageVolume'),
            'description': info.get('longBusinessSummary'),
        }

        return {
            "success": True,
            "ticker": ticker,
            "info": relevant_info
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ticker info: {str(e)}")

@app.get("/parameters/default")
def get_default_params():
    """Get default strategy parameters"""
    return {
        "success": True,
        "parameters": get_default_parameters()
    }

@app.post("/scan")
def scan_tickers(request: ScanRequest):
    """Scan multiple tickers based on criteria (placeholder for future implementation)"""
    # This is a placeholder - implement actual scanning logic based on your needs
    return {
        "success": True,
        "message": "Scanning functionality to be implemented",
        "tickers_scanned": len(request.tickers),
        "condition": request.condition
    }

# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
