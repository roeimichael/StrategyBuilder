from typing import Optional
import sqlite3
from fastapi import APIRouter, HTTPException, Query
from src.domains.watchlists.models import (
    CreateWatchlistRequest,
    UpdateWatchlistRequest,
    WatchlistResponse,
    WatchlistDetailResponse,
    WatchlistListResponse,
    WatchlistPositionResponse
)
from src.domains.watchlists.repository import WatchlistRepository
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/watchlists", tags=["watchlists"])
watchlist_repository = WatchlistRepository()


@router.post("", response_model=WatchlistResponse, status_code=201)
@log_errors
def create_watchlist(request: CreateWatchlistRequest) -> WatchlistResponse:
    """
    Create a new watchlist to track a strategy on a ticker with EOD updates.

    - **name**: Unique name for the watchlist
    - **description**: Optional description
    - **ticker**: Ticker symbol to watch
    - **strategy**: Strategy name to apply
    - **parameters**: Strategy parameters
    - **interval**: Data interval (default: 1d)
    - **cash**: Starting cash amount (default: 10000)
    - **active**: Whether to track daily (default: true)
    """
    try:
        watchlist_id = watchlist_repository.create_watchlist({
            'name': request.name,
            'description': request.description,
            'ticker': request.ticker,
            'strategy': request.strategy,
            'parameters': request.parameters,
            'interval': request.interval,
            'cash': request.cash,
            'active': request.active
        })

        watchlist = watchlist_repository.get_watchlist_by_id(watchlist_id)
        return WatchlistResponse(**watchlist)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Watchlist with name '{request.name}' already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create watchlist: {str(e)}")


@router.get("", response_model=WatchlistListResponse)
@log_errors
def list_watchlists(
    active_only: bool = Query(False, description="Only show active watchlists"),
    ticker: Optional[str] = Query(None, description="Filter by ticker")
) -> WatchlistListResponse:
    """
    List all watchlists with optional filters.

    - **active_only**: Only show active watchlists
    - **ticker**: Filter by ticker symbol
    """
    try:
        watchlists = watchlist_repository.list_watchlists(active_only=active_only, ticker=ticker)
        watchlist_responses = [WatchlistResponse(**wl) for wl in watchlists]

        return WatchlistListResponse(
            success=True,
            count=len(watchlist_responses),
            watchlists=watchlist_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve watchlists: {str(e)}")


@router.get("/{watchlist_id}", response_model=WatchlistDetailResponse)
@log_errors
def get_watchlist_detail(watchlist_id: int) -> WatchlistDetailResponse:
    """
    Get detailed information about a watchlist including all positions.

    - **watchlist_id**: The ID of the watchlist
    """
    try:
        watchlist = watchlist_repository.get_watchlist_by_id(watchlist_id)
        if not watchlist:
            raise HTTPException(status_code=404, detail=f"Watchlist with ID {watchlist_id} not found")

        # Get positions
        open_positions = watchlist_repository.get_positions_for_watchlist(watchlist_id, status='OPEN')
        closed_positions = watchlist_repository.get_positions_for_watchlist(watchlist_id, status='CLOSED')

        # Calculate stats
        winning_trades = sum(1 for p in closed_positions if p['pnl'] and p['pnl'] > 0)
        losing_trades = sum(1 for p in closed_positions if p['pnl'] and p['pnl'] < 0)

        return WatchlistDetailResponse(
            watchlist=WatchlistResponse(**watchlist),
            open_positions=[WatchlistPositionResponse(**p) for p in open_positions],
            closed_positions=[WatchlistPositionResponse(**p) for p in closed_positions],
            total_trades=len(closed_positions),
            winning_trades=winning_trades,
            losing_trades=losing_trades
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve watchlist: {str(e)}")


@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
@log_errors
def update_watchlist(watchlist_id: int, request: UpdateWatchlistRequest) -> WatchlistResponse:
    """
    Update a watchlist.

    - **watchlist_id**: The ID of the watchlist to update
    - **request**: Fields to update (all optional)
    """
    try:
        existing = watchlist_repository.get_watchlist_by_id(watchlist_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Watchlist with ID {watchlist_id} not found")

        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.active is not None:
            updates['active'] = request.active

        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")

        success = watchlist_repository.update_watchlist(watchlist_id, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update watchlist")

        watchlist = watchlist_repository.get_watchlist_by_id(watchlist_id)
        return WatchlistResponse(**watchlist)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update watchlist: {str(e)}")


@router.delete("/{watchlist_id}", status_code=204)
@log_errors
def delete_watchlist(watchlist_id: int):
    """
    Delete a watchlist and all its positions.

    - **watchlist_id**: The ID of the watchlist to delete
    """
    try:
        success = watchlist_repository.delete_watchlist(watchlist_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Watchlist with ID {watchlist_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete watchlist: {str(e)}")


# Note: EOD tracking service will run separately as a scheduled job
# It will iterate through active watchlists and update positions daily
