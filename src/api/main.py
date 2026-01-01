"""
StrategyBuilder FastAPI Application
Provides RESTful API for algorithmic trading backtesting
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import sys
import os
import importlib
import inspect

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import backtrader as bt
import yfinance as yf

from core.run_strategy import Run_strategy
from core.strategy_skeleton import Strategy_skeleton

# Initialize FastAPI
app = FastAPI(
    title="StrategyBuilder API",
    description="Algorithmic Trading Backtesting Platform",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Request/Response Models ====================

class BacktestRequest(BaseModel):
    """Backtest execution request"""
    ticker: str = Field(..., example="AAPL", description="Stock or crypto ticker symbol")
    strategy: str = Field(..., example="bollinger_bands_strategy", description="Strategy module name")
    start_date: Optional[str] = Field(None, example="2024-01-01", description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, example="2024-12-31", description="End date (YYYY-MM-DD)")
    interval: str = Field("1d", example="1h", description="Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)")
    cash: float = Field(10000.0, example=10000.0, description="Initial cash")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Strategy-specific parameters")

class MarketDataRequest(BaseModel):
    """Market data request"""
    ticker: str = Field(..., example="AAPL")
    period: str = Field("1mo", example="1mo", description="Period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    interval: str = Field("1d", example="1d")

class BacktestResponse(BaseModel):
    """Backtest results"""
    success: bool
    ticker: str
    strategy: str
    start_value: float
    end_value: float
    pnl: float
    return_pct: float
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    total_trades: int
    interval: str
    start_date: str
    end_date: str
    advanced_metrics: Optional[Dict[str, Any]] = None

# ==================== Utility Functions ====================

def get_default_parameters(strategy_params=None):
    """Get default strategy parameters"""
    params = {
        'cash': 10000,
        'macd1': 12,
        'macd2': 26,
        'macdsig': 9,
        'atrperiod': 14,
        'atrdist': 2.0,
        'order_pct': 1.0,
    }
    if strategy_params:
        params.update(strategy_params)
    return params

def load_strategy_class(strategy_name: str):
    """Dynamically load strategy class from strategies directory"""
    try:
        # Remove .py extension if provided
        if strategy_name.endswith('.py'):
            strategy_name = strategy_name[:-3]

        # Import the module
        module = importlib.import_module(f'strategies.{strategy_name}')

        # Find the strategy class in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, bt.Strategy) and obj not in [bt.Strategy, Strategy_skeleton]:
                return obj

        raise ValueError(f"No valid strategy class found in {strategy_name}")

    except ImportError as e:
        raise ValueError(f"Strategy module '{strategy_name}' not found: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading strategy: {str(e)}")

def list_strategies():
    """List all available strategy modules"""
    strategies_dir = os.path.join(os.path.dirname(__file__), '..', 'strategies')
    strategies = []

    for filename in os.listdir(strategies_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f'strategies.{module_name}')
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, bt.Strategy) and obj not in [bt.Strategy, Strategy_skeleton]:
                        strategies.append({
                            'module': module_name,
                            'class_name': name,
                            'description': obj.__doc__ or "No description"
                        })
            except Exception:
                pass

    return strategies

# ==================== API Endpoints ====================

@app.get("/")
def root():
    """API information"""
    return {
        "name": "StrategyBuilder API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "strategies": "/strategies",
            "backtest": "/backtest",
            "market_data": "/market-data",
            "health": "/health"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/strategies")
def get_strategies():
    """List all available trading strategies"""
    try:
        strategies = list_strategies()
        return {
            "success": True,
            "count": len(strategies),
            "strategies": strategies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies/{strategy_name}")
def get_strategy_info(strategy_name: str):
    """Get information about a specific strategy"""
    try:
        strategy_class = load_strategy_class(strategy_name)

        # Get strategy parameters
        params = {}
        if hasattr(strategy_class, 'params'):
            for param in strategy_class.params:
                if isinstance(param, tuple) and len(param) >= 2:
                    params[param[0]] = param[1]

        return {
            "success": True,
            "strategy": {
                "module": strategy_name,
                "class_name": strategy_class.__name__,
                "description": strategy_class.__doc__ or "No description",
                "parameters": params
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest):
    """Execute a backtest for a given ticker and strategy"""
    try:
        # Load strategy
        strategy_class = load_strategy_class(request.strategy)

        # Prepare parameters
        params = get_default_parameters(request.parameters)
        params['cash'] = request.cash

        # Parse dates
        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        else:
            start_date = datetime.now().date() - relativedelta(years=1)

        end_date = None
        if request.end_date:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        # Run backtest
        runner = Run_strategy(params, strategy_class)
        results = runner.runstrat(request.ticker, start_date, request.interval, end_date)

        return BacktestResponse(
            success=True,
            ticker=results['ticker'],
            strategy=request.strategy,
            start_value=results['start_value'],
            end_value=results['end_value'],
            pnl=results['pnl'],
            return_pct=round(results['return_pct'], 2),
            sharpe_ratio=round(results['sharpe_ratio'], 2) if results['sharpe_ratio'] else None,
            max_drawdown=round(results['max_drawdown'], 2) if results['max_drawdown'] else None,
            total_trades=results['total_trades'],
            interval=results['interval'],
            start_date=str(results['start_date']),
            end_date=str(results['end_date']),
            advanced_metrics=results.get('advanced_metrics', {})
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

@app.post("/market-data")
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
            raise HTTPException(status_code=404, detail=f"No data found for {request.ticker}")

        # Convert to JSON-friendly format
        data_dict = data.reset_index().to_dict(orient='records')

        # Calculate statistics
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

@app.get("/parameters/default")
def get_default_params():
    """Get default strategy parameters"""
    return {
        "success": True,
        "parameters": get_default_parameters()
    }

# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
