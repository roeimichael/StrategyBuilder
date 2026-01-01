import os
import sys
import importlib
import inspect
from typing import Optional, List, Dict, Type
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import backtrader as bt
import yfinance as yf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import Config
from core.run_strategy import Run_strategy
from core.strategy_skeleton import Strategy_skeleton

app = FastAPI(
    title=Config.API_TITLE,
    description="Algorithmic Trading Backtesting Platform",
    version=Config.API_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=Config.CORS_CREDENTIALS,
    allow_methods=Config.CORS_METHODS,
    allow_headers=Config.CORS_HEADERS,
)

class BacktestRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: str = Field(Config.DEFAULT_INTERVAL, example="1h")
    cash: float = Field(Config.DEFAULT_CASH, example=10000.0)
    parameters: Optional[Dict[str, float]] = Field(None)

class MarketDataRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    period: str = Field("1mo", example="1mo")
    interval: str = Field(Config.DEFAULT_INTERVAL, example="1d")

class BacktestResponse(BaseModel):
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
    advanced_metrics: Optional[Dict[str, float]] = None

class StrategyInfo(BaseModel):
    module: str
    class_name: str
    description: str

class StrategyParameters(BaseModel):
    success: bool
    strategy: Dict[str, object]

def get_default_parameters(strategy_params: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    params = Config.get_default_parameters()
    if strategy_params:
        params.update(strategy_params)
    return params

def load_strategy_class(strategy_name: str) -> Type[bt.Strategy]:
    try:
        if strategy_name.endswith('.py'):
            strategy_name = strategy_name[:-3]
        module = importlib.import_module(f'strategies.{strategy_name}')
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, bt.Strategy) and obj not in [bt.Strategy, Strategy_skeleton]:
                return obj
        raise ValueError(f"No valid strategy class found in {strategy_name}")
    except ImportError as e:
        raise ValueError(f"Strategy module '{strategy_name}' not found: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading strategy: {str(e)}")

def list_strategies() -> List[StrategyInfo]:
    strategies_dir = os.path.join(os.path.dirname(__file__), '..', 'strategies')
    strategies = []
    for filename in os.listdir(strategies_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f'strategies.{module_name}')
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, bt.Strategy) and obj not in [bt.Strategy, Strategy_skeleton]:
                        strategies.append(StrategyInfo(
                            module=module_name,
                            class_name=name,
                            description=obj.__doc__ or ""
                        ))
            except Exception:
                pass
    return strategies

@app.get("/")
def root() -> Dict[str, object]:
    return {
        "name": Config.API_TITLE,
        "version": Config.API_VERSION,
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
def health() -> Dict[str, str]:
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/strategies")
def get_strategies() -> Dict[str, object]:
    try:
        strategies = list_strategies()
        return {
            "success": True,
            "count": len(strategies),
            "strategies": [s.dict() for s in strategies]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies/{strategy_name}")
def get_strategy_info(strategy_name: str) -> Dict[str, object]:
    try:
        strategy_class = load_strategy_class(strategy_name)
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
                "description": strategy_class.__doc__ or "",
                "parameters": params
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest) -> BacktestResponse:
    try:
        strategy_class = load_strategy_class(request.strategy)
        params = get_default_parameters(request.parameters)
        params['cash'] = request.cash
        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        else:
            start_date = datetime.now().date() - relativedelta(years=Config.DEFAULT_BACKTEST_PERIOD_YEARS)
        end_date = None
        if request.end_date:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
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
def get_market_data(request: MarketDataRequest) -> Dict[str, object]:
    try:
        data = yf.download(
            request.ticker,
            period=request.period,
            interval=request.interval,
            progress=False
        )
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.ticker}")
        data_dict = data.reset_index().to_dict(orient='records')
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
def get_default_params() -> Dict[str, object]:
    return {
        "success": True,
        "parameters": get_default_parameters()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=True)
