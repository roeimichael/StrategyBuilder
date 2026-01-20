from typing import Optional, List, Dict, Any
from datetime import datetime
import datetime as dt
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
from src.data.watchlist_repository import WatchlistRepository
from src.data.portfolio_repository import PortfolioRepository
from src.utils.api_logger import log_errors
from src.api.models import (
    BacktestRequest, MarketDataRequest, BacktestResponse, StrategyInfo,
    ReplayRunRequest, SavedRunSummaryResponse, SavedRunDetailResponse,
    OptimizationRequest, OptimizationResponse, OptimizationResult,
    CreatePresetRequest, PresetResponse, SnapshotRequest, SnapshotResponse,
    SnapshotPositionState, CreateWatchlistRequest, WatchlistEntryResponse,
    MarketScanRequest, MarketScanResponse,
    AddPortfolioPositionRequest, UpdatePortfolioPositionRequest, PortfolioAnalysisRequest,
    PortfolioPositionResponse, PortfolioSummaryResponse, PortfolioAnalysisResponse
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
watchlist_repository = WatchlistRepository()
portfolio_repository = PortfolioRepository()

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
            "market_scan": "/market-scan",
            "market_data": "/market-data",
            "health": "/health",
            "runs": "/runs",
            "run_detail": "/runs/{run_id}",
            "replay_run": "/runs/{run_id}/replay",
            "presets": "/presets",
            "preset_detail": "/presets/{preset_id}",
            "preset_backtest": "/presets/{preset_id}/backtest",
            "portfolio": "/portfolio",
            "portfolio_position": "/portfolio/{position_id}",
            "portfolio_analyze": "/portfolio/analyze"
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
    except ValueError as e:
        error_msg = str(e)
        if "No data available" in error_msg or "Failed to fetch data" in error_msg:
            raise HTTPException(status_code=400, detail=f"Invalid ticker or no data available: {error_msg}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {error_msg}")
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

@app.post("/market-scan", response_model=MarketScanResponse)
@log_errors
def market_scan(request: MarketScanRequest) -> MarketScanResponse:
    try:
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")

        result = backtest_service.market_scan(
            strategy_name=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval,
            cash=request.cash,
            parameters=request.parameters
        )

        return MarketScanResponse(
            success=result['success'],
            strategy=result['strategy'],
            start_value=result['start_value'],
            end_value=result['end_value'],
            pnl=result['pnl'],
            return_pct=result['return_pct'],
            sharpe_ratio=result['sharpe_ratio'],
            max_drawdown=result['max_drawdown'],
            total_trades=result['total_trades'],
            winning_trades=result['winning_trades'],
            losing_trades=result['losing_trades'],
            interval=result['interval'],
            start_date=result['start_date'],
            end_date=result['end_date'],
            stocks_scanned=result['stocks_scanned'],
            stocks_with_trades=result['stocks_with_trades'],
            stock_results=result['stock_results'],
            macro_statistics=result['macro_statistics']
        )
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market scan failed: {str(e)}")

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
    ticker: Optional[str] = Query(None),
    strategy: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
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
    try:
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")
        if preset_repository.preset_exists(request.name, request.strategy):
            raise HTTPException(
                status_code=409,
                detail=f"Preset with name '{request.name}' for strategy '{request.strategy}' already exists"
            )
        preset_data = {
            'name': request.name,
            'strategy': request.strategy,
            'parameters': request.parameters,
            'notes': request.notes
        }
        preset_id = preset_repository.create_preset(preset_data)
        created_preset = preset_repository.get_preset(preset_id)
        return PresetResponse(
            id=created_preset['id'],
            name=created_preset['name'],
            strategy=created_preset['strategy'],
            parameters=created_preset['parameters'],
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
    strategy: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    try:
        presets = preset_repository.list_presets(strategy=strategy, limit=limit, offset=offset)
        total_count = preset_repository.get_preset_count(strategy=strategy)
        preset_responses = [
            PresetResponse(
                id=preset['id'],
                name=preset['name'],
                strategy=preset['strategy'],
                parameters=preset['parameters'],
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

@app.get("/presets/{preset_id}", response_model=PresetResponse)
@log_errors
def get_preset(preset_id: int) -> PresetResponse:
    try:
        preset = preset_repository.get_preset(preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")
        return PresetResponse(
            id=preset['id'],
            name=preset['name'],
            strategy=preset['strategy'],
            parameters=preset['parameters'],
            notes=preset['notes'],
            created_at=preset['created_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve preset: {str(e)}")

@app.delete("/presets/{preset_id}")
@log_errors
def delete_preset(preset_id: int) -> Dict[str, Any]:
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
                         ticker: str = Query(..., example="AAPL"),
                         start_date: Optional[str] = Query(None, example="2024-01-01"),
                         end_date: Optional[str] = Query(None, example="2024-12-31"),
                         interval: str = Query("1d", example="1d"),
                         cash: Optional[float] = Query(None, example=10000.0)) -> BacktestResponse:
    try:
        preset = preset_repository.get_preset(preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")
        backtest_request = ServiceBacktestRequest(
            ticker=ticker,
            strategy=preset['strategy'],
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            cash=cash if cash is not None else 10000.0,
            parameters=preset['parameters']
        )
        response = backtest_service.run_backtest(backtest_request, save_run=True)
        return BacktestResponse(**response.dict())
    except HTTPException:
        raise
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run backtest from preset: {str(e)}")

@app.post("/snapshot", response_model=SnapshotResponse)
@log_errors
def get_strategy_snapshot(request: SnapshotRequest) -> SnapshotResponse:
    try:
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")
        snapshot_data = backtest_service.get_snapshot(
            ticker=request.ticker,
            strategy_name=request.strategy,
            interval=request.interval,
            lookback_bars=request.lookback_bars,
            parameters=request.parameters,
            cash=request.cash
        )
        return SnapshotResponse(
            success=True,
            ticker=snapshot_data['ticker'],
            strategy=snapshot_data['strategy'],
            interval=snapshot_data['interval'],
            lookback_bars=snapshot_data['lookback_bars'],
            last_bar=snapshot_data['last_bar'],
            indicators=snapshot_data['indicators'],
            position_state=SnapshotPositionState(**snapshot_data['position_state']),
            recent_trades=snapshot_data['recent_trades'],
            portfolio_value=snapshot_data['portfolio_value'],
            cash=snapshot_data['cash'],
            timestamp=snapshot_data['timestamp']
        )
    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        if "No data available" in error_msg or "Failed to fetch data" in error_msg:
            raise HTTPException(status_code=400, detail=f"Invalid ticker or no data available: {error_msg}")
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=f"Invalid input: {error_msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snapshot failed: {str(e)}")

@app.post("/watchlist", response_model=WatchlistEntryResponse)
@log_errors
def create_watchlist_entry(request: CreateWatchlistRequest) -> WatchlistEntryResponse:
    try:
        if not request.preset_id and not request.run_id:
            raise HTTPException(
                status_code=400,
                detail="Either preset_id or run_id must be provided"
            )
        if request.preset_id:
            preset = preset_repository.get_preset(request.preset_id)
            if not preset:
                raise HTTPException(
                    status_code=404,
                    detail=f"Preset with ID {request.preset_id} not found"
                )
        if request.run_id:
            run = run_repository.get_run_by_id(request.run_id)
            if not run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Run with ID {request.run_id} not found"
                )
        entry_data = {
            'name': request.name,
            'preset_id': request.preset_id,
            'run_id': request.run_id,
            'frequency': request.frequency,
            'enabled': request.enabled
        }
        entry_id = watchlist_repository.create_entry(entry_data)
        created_entry = watchlist_repository.get_entry(entry_id)
        return WatchlistEntryResponse(**created_entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create watchlist entry: {str(e)}")

@app.get("/watchlist", response_model=List[WatchlistEntryResponse])
@log_errors
def list_watchlist_entries(enabled_only: bool = Query(False)) -> List[WatchlistEntryResponse]:
    try:
        entries = watchlist_repository.list_entries(enabled_only=enabled_only)
        return [WatchlistEntryResponse(**entry) for entry in entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list watchlist entries: {str(e)}")

@app.get("/watchlist/{entry_id}", response_model=WatchlistEntryResponse)
@log_errors
def get_watchlist_entry(entry_id: int) -> WatchlistEntryResponse:
    try:
        entry = watchlist_repository.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail=f"Watchlist entry with ID {entry_id} not found")
        return WatchlistEntryResponse(**entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get watchlist entry: {str(e)}")

@app.delete("/watchlist/{entry_id}")
@log_errors
def delete_watchlist_entry(entry_id: int) -> Dict[str, Any]:
    try:
        deleted = watchlist_repository.delete_entry(entry_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Watchlist entry with ID {entry_id} not found")
        return {
            "success": True,
            "message": f"Watchlist entry {entry_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete watchlist entry: {str(e)}")

@app.patch("/watchlist/{entry_id}")
@log_errors
def update_watchlist_entry(entry_id: int, enabled: Optional[bool] = Query(None)) -> Dict[str, Any]:
    try:
        if enabled is None:
            raise HTTPException(status_code=400, detail="At least one field must be provided to update")
        updates = {'enabled': enabled}
        updated = watchlist_repository.update_entry(entry_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Watchlist entry with ID {entry_id} not found")
        return {
            "success": True,
            "message": f"Watchlist entry {entry_id} updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update watchlist entry: {str(e)}")

@app.post("/portfolio", response_model=PortfolioPositionResponse)
@log_errors
def add_portfolio_position(request: AddPortfolioPositionRequest) -> PortfolioPositionResponse:
    try:
        position_size = request.quantity * request.entry_price
        position = {
            'ticker': request.ticker.upper(),
            'quantity': request.quantity,
            'entry_price': request.entry_price,
            'entry_date': request.entry_date,
            'position_size': position_size,
            'notes': request.notes
        }
        position_id = portfolio_repository.add_position(position)
        created_position = portfolio_repository.get_position_by_id(position_id)

        if not created_position:
            raise HTTPException(status_code=500, detail="Failed to retrieve created position")

        return PortfolioPositionResponse(**created_position)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add position: {str(e)}")

@app.get("/portfolio", response_model=PortfolioSummaryResponse)
@log_errors
def get_portfolio() -> PortfolioSummaryResponse:
    try:
        positions = portfolio_repository.get_all_positions()
        total_value = portfolio_repository.get_total_portfolio_value()

        position_responses = [PortfolioPositionResponse(**pos) for pos in positions]

        return PortfolioSummaryResponse(
            total_positions=len(positions),
            total_portfolio_value=total_value,
            positions=position_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio: {str(e)}")

@app.get("/portfolio/{position_id}", response_model=PortfolioPositionResponse)
@log_errors
def get_portfolio_position(position_id: int) -> PortfolioPositionResponse:
    try:
        position = portfolio_repository.get_position_by_id(position_id)
        if not position:
            raise HTTPException(status_code=404, detail=f"Position with ID {position_id} not found")
        return PortfolioPositionResponse(**position)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve position: {str(e)}")

@app.put("/portfolio/{position_id}", response_model=PortfolioPositionResponse)
@log_errors
def update_portfolio_position(position_id: int, request: UpdatePortfolioPositionRequest) -> PortfolioPositionResponse:
    try:
        updates = {}
        if request.ticker is not None:
            updates['ticker'] = request.ticker.upper()
        if request.quantity is not None:
            updates['quantity'] = request.quantity
        if request.entry_price is not None:
            updates['entry_price'] = request.entry_price
        if request.entry_date is not None:
            updates['entry_date'] = request.entry_date
        if request.notes is not None:
            updates['notes'] = request.notes

        if 'quantity' in updates or 'entry_price' in updates:
            current = portfolio_repository.get_position_by_id(position_id)
            if not current:
                raise HTTPException(status_code=404, detail=f"Position with ID {position_id} not found")
            quantity = updates.get('quantity', current['quantity'])
            entry_price = updates.get('entry_price', current['entry_price'])
            updates['position_size'] = quantity * entry_price

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        updated = portfolio_repository.update_position(position_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Position with ID {position_id} not found")

        position = portfolio_repository.get_position_by_id(position_id)
        return PortfolioPositionResponse(**position)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update position: {str(e)}")

@app.delete("/portfolio/{position_id}")
@log_errors
def delete_portfolio_position(position_id: int) -> Dict[str, Any]:
    try:
        deleted = portfolio_repository.delete_position(position_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Position with ID {position_id} not found")
        return {
            "success": True,
            "message": f"Position {position_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete position: {str(e)}")

@app.post("/portfolio/analyze", response_model=PortfolioAnalysisResponse)
@log_errors
def analyze_portfolio(request: PortfolioAnalysisRequest) -> PortfolioAnalysisResponse:
    try:
        strategy_class = strategy_service.load_strategy_class(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")

        positions = portfolio_repository.get_all_positions()
        if not positions:
            raise HTTPException(status_code=400, detail="Portfolio is empty. Add positions before running analysis.")

        result = backtest_service.analyze_portfolio(
            positions=positions,
            strategy_name=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval,
            parameters=request.parameters
        )

        return PortfolioAnalysisResponse(
            success=result['success'],
            strategy=result['strategy'],
            interval=result['interval'],
            start_date=result['start_date'],
            end_date=result['end_date'],
            total_portfolio_value=result['total_portfolio_value'],
            weighted_pnl=result['weighted_pnl'],
            weighted_return_pct=result['weighted_return_pct'],
            weighted_sharpe_ratio=result['weighted_sharpe_ratio'],
            weighted_max_drawdown=result['weighted_max_drawdown'],
            total_trades=result['total_trades'],
            winning_trades=result['winning_trades'],
            losing_trades=result['losing_trades'],
            positions_analyzed=result['positions_analyzed'],
            position_results=result['position_results'],
            portfolio_statistics=result['portfolio_statistics']
        )
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=True)
