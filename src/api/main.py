from typing import Optional, List, Dict, Any
from datetime import datetime
import datetime as dt
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.config import Config
from src.services.strategy_service import StrategyService
from src.services.backtest_service import BacktestService, BacktestRequest as ServiceBacktestRequest
from src.core.data_manager import DataManager
from src.core.optimizer import StrategyOptimizer
from src.data.run_repository import RunRepository
from src.data.preset_repository import PresetRepository
from src.utils.api_logger import log_errors
from src.api.models import (
    BacktestRequest, MarketDataRequest, BacktestResponse, StrategyInfo,
    ReplayRunRequest, SavedRunSummaryResponse, SavedRunDetailResponse,
    OptimizationRequest, OptimizationResponse, OptimizationResult,
    CreatePresetRequest, PresetResponse
)
from src.exceptions import StrategyNotFoundError, StrategyLoadError

app = FastAPI(title=Config.API_TITLE, description="Algorithmic Trading Backtesting Platform",
              version=Config.API_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=Config.CORS_ORIGINS, allow_credentials=Config.CORS_CREDENTIALS,
                   allow_methods=Config.CORS_METHODS, allow_headers=Config.CORS_HEADERS)
app.add_middleware(GZipMiddleware, minimum_size=1000)
strategy_service = StrategyService()
backtest_service = BacktestService()
data_manager = DataManager()
run_repository = RunRepository()
preset_repository = PresetRepository()


def convert_to_columnar(chart_data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    if not chart_data:
        return {}
    columnar = {}
    for key in chart_data[0].keys():
        columnar[key] = [point.get(key) for point in chart_data]
    return columnar


@app.get("/")
@log_errors
def root() -> Dict[str, object]:
    return {
        "name": Config.API_TITLE, "version": Config.API_VERSION, "status": "running", "docs": "/docs",
        "endpoints": {
            "strategies": "/strategies",
            "backtest": "/backtest",
            "optimize": "/optimize",
            "market_data": "/market-data",
            "health": "/health",
            "runs": "/runs",
            "run_detail": "/runs/{run_id}",
            "replay_run": "/runs/{run_id}/replay",
            "presets": "/presets",
            "preset_detail": "/presets/{preset_id}",
            "preset_backtest": "/presets/{preset_id}/backtest"
        }
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
        # Validate strategy exists before running backtest
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")

        service_request = ServiceBacktestRequest(
            ticker=request.ticker, strategy=request.strategy, start_date=request.start_date,
            end_date=request.end_date, interval=request.interval, cash=request.cash, parameters=request.parameters
        )
        response = backtest_service.run_backtest(service_request)
        response_dict = response.dict()
        if not request.include_chart_data:
            response_dict['chart_data'] = None
        elif request.columnar_format and response_dict.get('chart_data'):
            response_dict['chart_data'] = convert_to_columnar(response_dict['chart_data'])
        return BacktestResponse(**response_dict)
    except HTTPException:
        raise
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IndexError as e:
        if "array assignment index out of range" in str(e):
            raise HTTPException(status_code=400, detail=f"Insufficient data for strategy indicators. Try using a longer date range.")
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@app.post("/optimize", response_model=OptimizationResponse)
@log_errors
def optimize_strategy(request: OptimizationRequest) -> OptimizationResponse:
    try:
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")

        optimizer = StrategyOptimizer(strategy_class, data_manager)

        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date() if request.start_date else dt.date.today() - dt.timedelta(days=365)
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date() if request.end_date else dt.date.today()

        results = optimizer.run_optimization(
            ticker=request.ticker,
            start_date=start_date,
            end_date=end_date,
            interval=request.interval,
            cash=request.cash,
            param_ranges=request.optimization_params
        )

        total_combinations = 1
        for param_values in request.optimization_params.values():
            total_combinations *= len(param_values)

        optimization_results = [
            OptimizationResult(
                parameters=result['parameters'],
                pnl=result['pnl'],
                return_pct=result['return_pct'],
                sharpe_ratio=result['sharpe_ratio'],
                start_value=result['start_value'],
                end_value=result['end_value']
            )
            for result in results
        ]

        return OptimizationResponse(
            success=True,
            ticker=request.ticker,
            strategy=request.strategy,
            interval=request.interval,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            total_combinations=total_combinations,
            top_results=optimization_results
        )
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.post("/market-data")
@log_errors
def get_market_data(request: MarketDataRequest) -> Dict[str, object]:
    try:
        end_date = dt.date.today()
        period_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825,
                      'ytd': (dt.date.today() - dt.date(dt.date.today().year, 1, 1)).days, 'max': 3650}
        days = period_map.get(request.period, 365)
        start_date = end_date - dt.timedelta(days=days)
        data = data_manager.get_data(ticker=request.ticker, start_date=start_date, end_date=end_date,
                                     interval=request.interval)
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


@app.get("/runs")
@log_errors
def get_runs(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    limit: int = Query(100, description="Maximum number of results", ge=1, le=1000),
    offset: int = Query(0, description="Number of results to skip", ge=0)
) -> Dict[str, Any]:
    """
    List saved backtest runs with optional filters.

    - **ticker**: Filter by ticker symbol (optional)
    - **strategy**: Filter by strategy name (optional)
    - **limit**: Maximum number of results (default: 100, max: 1000)
    - **offset**: Number of results to skip for pagination (default: 0)
    """
    try:
        runs = run_repository.list_runs(ticker=ticker, strategy=strategy, limit=limit, offset=offset)
        total_count = run_repository.get_run_count(ticker=ticker, strategy=strategy)

        summary_runs = [
            SavedRunSummaryResponse(
                id=run['id'],
                ticker=run['ticker'],
                strategy=run['strategy'],
                interval=run['interval'],
                pnl=run['pnl'],
                return_pct=run['return_pct'],
                created_at=run['created_at']
            )
            for run in runs
        ]

        return {
            "success": True,
            "total_count": total_count,
            "count": len(summary_runs),
            "limit": limit,
            "offset": offset,
            "runs": [run.dict() for run in summary_runs]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve runs: {str(e)}")


@app.get("/runs/{run_id}", response_model=SavedRunDetailResponse)
@log_errors
def get_run_detail(run_id: int) -> SavedRunDetailResponse:
    """
    Get detailed information about a specific saved run.

    - **run_id**: The ID of the saved run
    """
    try:
        run = run_repository.get_run_by_id(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run with ID {run_id} not found")

        return SavedRunDetailResponse(
            id=run['id'],
            ticker=run['ticker'],
            strategy=run['strategy'],
            parameters=run['parameters'],
            start_date=run['start_date'],
            end_date=run['end_date'],
            interval=run['interval'],
            cash=run['cash'],
            pnl=run['pnl'],
            return_pct=run['return_pct'],
            sharpe_ratio=run['sharpe_ratio'],
            max_drawdown=run['max_drawdown'],
            total_trades=run['total_trades'],
            winning_trades=run['winning_trades'],
            losing_trades=run['losing_trades'],
            created_at=run['created_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve run: {str(e)}")


@app.post("/runs/{run_id}/replay", response_model=BacktestResponse)
@log_errors
def replay_run(run_id: int, request: ReplayRunRequest) -> BacktestResponse:
    """
    Replay a saved backtest run with optional parameter overrides.

    - **run_id**: The ID of the saved run to replay
    - **request**: Optional overrides for start_date, end_date, interval, cash, or parameters
    """
    try:
        overrides = {}
        if request.start_date is not None:
            overrides['start_date'] = request.start_date
        if request.end_date is not None:
            overrides['end_date'] = request.end_date
        if request.interval is not None:
            overrides['interval'] = request.interval
        if request.cash is not None:
            overrides['cash'] = request.cash
        if request.parameters is not None:
            overrides['parameters'] = request.parameters

        response = backtest_service.run_backtest_from_saved_run(run_id, overrides)
        return BacktestResponse(**response.dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replay run: {str(e)}")


@app.post("/presets", response_model=PresetResponse)
@log_errors
def create_preset(request: CreatePresetRequest) -> PresetResponse:
    """
    Create a new strategy preset for reuse.

    - **name**: Unique name for this preset
    - **ticker**: Ticker symbol
    - **strategy**: Strategy name
    - **parameters**: Strategy parameters as key-value pairs
    - **interval**: Time interval
    - **notes**: Optional notes about this preset
    """
    try:
        # Validate that strategy exists
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")

        # Check if preset with same name/strategy/ticker already exists
        if preset_repository.preset_exists(request.name, request.strategy, request.ticker):
            raise HTTPException(
                status_code=409,
                detail=f"Preset with name '{request.name}' for strategy '{request.strategy}' and ticker '{request.ticker}' already exists"
            )

        # Create preset
        preset_data = {
            'name': request.name,
            'ticker': request.ticker,
            'strategy': request.strategy,
            'parameters': request.parameters,
            'interval': request.interval,
            'notes': request.notes
        }

        preset_id = preset_repository.create_preset(preset_data)

        # Retrieve and return the created preset
        created_preset = preset_repository.get_preset(preset_id)

        return PresetResponse(
            id=created_preset['id'],
            name=created_preset['name'],
            ticker=created_preset['ticker'],
            strategy=created_preset['strategy'],
            parameters=created_preset['parameters'],
            interval=created_preset['interval'],
            notes=created_preset['notes'],
            created_at=created_preset['created_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create preset: {str(e)}")


@app.get("/presets")
@log_errors
def get_presets(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    limit: int = Query(100, description="Maximum number of results", ge=1, le=1000),
    offset: int = Query(0, description="Number of results to skip", ge=0)
) -> Dict[str, Any]:
    """
    List saved strategy presets with optional filters.

    - **ticker**: Filter by ticker symbol (optional)
    - **strategy**: Filter by strategy name (optional)
    - **limit**: Maximum number of results (default: 100, max: 1000)
    - **offset**: Number of results to skip for pagination (default: 0)
    """
    try:
        presets = preset_repository.list_presets(ticker=ticker, strategy=strategy, limit=limit, offset=offset)
        total_count = preset_repository.get_preset_count(ticker=ticker, strategy=strategy)

        preset_responses = [
            PresetResponse(
                id=preset['id'],
                name=preset['name'],
                ticker=preset['ticker'],
                strategy=preset['strategy'],
                parameters=preset['parameters'],
                interval=preset['interval'],
                notes=preset['notes'],
                created_at=preset['created_at']
            )
            for preset in presets
        ]

        return {
            "success": True,
            "total_count": total_count,
            "count": len(preset_responses),
            "limit": limit,
            "offset": offset,
            "presets": [preset.dict() for preset in preset_responses]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve presets: {str(e)}")


@app.delete("/presets/{preset_id}")
@log_errors
def delete_preset(preset_id: int) -> Dict[str, Any]:
    """
    Delete a strategy preset by ID.

    - **preset_id**: The ID of the preset to delete
    """
    try:
        deleted = preset_repository.delete_preset(preset_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")

        return {
            "success": True,
            "message": f"Preset {preset_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete preset: {str(e)}")


@app.post("/presets/{preset_id}/backtest", response_model=BacktestResponse)
@log_errors
def backtest_from_preset(preset_id: int,
                         start_date: Optional[str] = Query(None, example="2024-01-01"),
                         end_date: Optional[str] = Query(None, example="2024-12-31"),
                         cash: Optional[float] = Query(None, example=10000.0)) -> BacktestResponse:
    """
    Run a backtest using a saved preset configuration.

    - **preset_id**: The ID of the preset to use
    - **start_date**: Optional override for start date
    - **end_date**: Optional override for end date
    - **cash**: Optional override for initial cash
    """
    try:
        # Load preset
        preset = preset_repository.get_preset(preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")

        # Build backtest request from preset
        backtest_request = ServiceBacktestRequest(
            ticker=preset['ticker'],
            strategy=preset['strategy'],
            start_date=start_date,
            end_date=end_date,
            interval=preset['interval'],
            cash=cash if cash is not None else 10000.0,
            parameters=preset['parameters']
        )

        # Run backtest
        response = backtest_service.run_backtest(backtest_request, save_run=True)
        return BacktestResponse(**response.dict())

    except HTTPException:
        raise
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run backtest from preset: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=True)
