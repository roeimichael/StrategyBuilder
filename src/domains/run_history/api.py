from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from src.domains.run_history.repository import RunRepository
from src.domains.run_history.models import ReplayRunRequest, SavedRunSummaryResponse, SavedRunDetailResponse
from src.domains.backtests.service import BacktestService
from src.domains.backtests.models import BacktestResponse
from src.shared.exceptions import StrategyNotFoundError, StrategyLoadError
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/runs", tags=["run-history"])
run_repository = RunRepository()
backtest_service = BacktestService()


@router.get("")
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


@router.get("/{run_id}", response_model=SavedRunDetailResponse)
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


@router.post("/{run_id}/replay", response_model=BacktestResponse)
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
