from typing import Optional, List, Dict, Any
from datetime import datetime
import datetime as dt
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.config import Config
from src.services.strategy_service import StrategyService
from src.services.backtest_service import BacktestService, BacktestRequest as ServiceBacktestRequest
from src.core.data_manager import DataManager
from src.utils.api_logger import log_errors
from src.api.models import BacktestRequest, MarketDataRequest, BacktestResponse, StrategyInfo
from src.exceptions import StrategyNotFoundError, StrategyLoadError

app = FastAPI(title=Config.API_TITLE, description="Algorithmic Trading Backtesting Platform", version=Config.API_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=Config.CORS_ORIGINS, allow_credentials=Config.CORS_CREDENTIALS,
                   allow_methods=Config.CORS_METHODS, allow_headers=Config.CORS_HEADERS)
strategy_service = StrategyService()
backtest_service = BacktestService()
data_manager = DataManager()

@app.get("/")
@log_errors
def root() -> Dict[str, object]:
    return {
        "name": Config.API_TITLE, "version": Config.API_VERSION, "status": "running", "docs": "/docs",
        "endpoints": {"strategies": "/strategies", "backtest": "/backtest", "market_data": "/market-data", "health": "/health"}
    }

@app.get("/health")
@log_errors
def health() -> Dict[str, str]:
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/strategies")
@log_errors
def get_strategies() -> Dict[str, object]:
    try:
        strategies = strategy_service.list_strategies()
        return {"success": True, "count": len(strategies), "strategies": [s.dict() for s in strategies]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategies/{strategy_name}")
@log_errors
def get_strategy_info(strategy_name: str) -> Dict[str, object]:
    try:
        strategy_info = strategy_service.get_strategy_info(strategy_name)
        return {"success": True, "strategy": strategy_info}
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest", response_model=BacktestResponse)
@log_errors
def run_backtest(request: BacktestRequest) -> BacktestResponse:
    try:
        service_request = ServiceBacktestRequest(
            ticker=request.ticker, strategy=request.strategy, start_date=request.start_date,
            end_date=request.end_date, interval=request.interval, cash=request.cash, parameters=request.parameters
        )
        response = backtest_service.run_backtest(service_request)
        return BacktestResponse(**response.dict())
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

@app.post("/market-data")
@log_errors
def get_market_data(request: MarketDataRequest) -> Dict[str, object]:
    try:
        end_date = dt.date.today()
        period_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825,
                     'ytd': (dt.date.today() - dt.date(dt.date.today().year, 1, 1)).days, 'max': 3650}
        days = period_map.get(request.period, 365)
        start_date = end_date - dt.timedelta(days=days)
        data = data_manager.get_data(ticker=request.ticker, start_date=start_date, end_date=end_date, interval=request.interval)
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.ticker}")
        data_dict = data.reset_index().to_dict(orient='records')
        stats = {
            'mean': data['Close'].mean().item() if 'Close' in data else None,
            'std': data['Close'].std().item() if 'Close' in data else None,
            'min': data['Close'].min().item() if 'Close' in data else None,
            'max': data['Close'].max().item() if 'Close' in data else None,
            'volume_avg': data['Volume'].mean().item() if 'Volume' in data else None,
        }
        return {
            "success": True, "ticker": request.ticker, "period": request.period, "interval": request.interval,
            "data_points": len(data_dict), "data": data_dict, "statistics": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@app.get("/parameters/default")
@log_errors
def get_default_params() -> Dict[str, object]:
    return {"success": True, "parameters": strategy_service.get_default_parameters()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=True)
