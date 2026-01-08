from typing import Optional, List, Dict, Any
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import yfinance as yf

from src.config import Config
from src.services.strategy_service import StrategyService
from src.services.backtest_service import BacktestService, BacktestRequest as ServiceBacktestRequest
from src.utils.api_logger import log_errors, logger


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

# Initialize services
strategy_service = StrategyService()
backtest_service = BacktestService()


# API Models
class BacktestRequest(BaseModel):
    """API model for backtest requests"""
    ticker: str = Field(..., example="AAPL")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: str = Field(Config.DEFAULT_INTERVAL, example="1h")
    cash: float = Field(Config.DEFAULT_CASH, example=10000.0)
    parameters: Optional[Dict[str, float]] = Field(None)


class MarketDataRequest(BaseModel):
    """API model for market data requests"""
    ticker: str = Field(..., example="AAPL")
    period: str = Field("1mo", example="1mo")
    interval: str = Field(Config.DEFAULT_INTERVAL, example="1d")


class BacktestResponse(BaseModel):
    """API model for backtest responses"""
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
    chart_data: Optional[List[Dict[str, Any]]] = None


class StrategyInfo(BaseModel):
    """API model for strategy information"""
    module: str
    class_name: str
    description: str


class StrategyParameters(BaseModel):
    """API model for strategy parameters"""
    success: bool
    strategy: Dict[str, object]


# API Endpoints

@app.get("/")
@log_errors
def root() -> Dict[str, object]:
    """Root endpoint with API information"""
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
@log_errors
def health() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/strategies")
@log_errors
def get_strategies() -> Dict[str, object]:
    """List all available trading strategies"""
    try:
        strategies = strategy_service.list_strategies()
        return {
            "success": True,
            "count": len(strategies),
            "strategies": [s.dict() for s in strategies]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/strategies/{strategy_name}")
@log_errors
def get_strategy_info(strategy_name: str) -> Dict[str, object]:
    """Get detailed information about a specific strategy"""
    try:
        strategy_info = strategy_service.get_strategy_info(strategy_name)
        return {
            "success": True,
            "strategy": strategy_info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/backtest", response_model=BacktestResponse)
@log_errors
def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """Execute a strategy backtest"""
    try:
        # Convert API request to service request
        service_request = ServiceBacktestRequest(
            ticker=request.ticker,
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval,
            cash=request.cash,
            parameters=request.parameters
        )

        # Execute backtest via service
        response = backtest_service.run_backtest(service_request)

        # Return response (convert to dict for FastAPI)
        return BacktestResponse(**response.dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@app.post("/market-data")
@log_errors
def get_market_data(request: MarketDataRequest) -> Dict[str, object]:
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

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.loc[:, ~data.columns.duplicated()]
        data_dict = data.reset_index().to_dict(orient='records')

        stats = {
            'mean': data['Close'].mean().item() if 'Close' in data else None,
            'std': data['Close'].std().item() if 'Close' in data else None,
            'min': data['Close'].min().item() if 'Close' in data else None,
            'max': data['Close'].max().item() if 'Close' in data else None,
            'volume_avg': data['Volume'].mean().item() if 'Volume' in data else None,
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
@log_errors
def get_default_params() -> Dict[str, object]:
    """Get default backtest parameters"""
    return {
        "success": True,
        "parameters": strategy_service.get_default_parameters()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=True)
