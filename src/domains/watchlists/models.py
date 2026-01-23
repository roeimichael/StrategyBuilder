from typing import Dict, Union, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class PositionType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class CreateWatchlistRequest(BaseModel):
    name: str = Field(..., example="My Tech Watchlist")
    description: Optional[str] = Field(None, example="Watching tech stocks with Bollinger strategy")
    ticker: str = Field(..., example="AAPL")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    parameters: Dict[str, Union[int, float]] = Field(..., example={"period": 20, "devfactor": 2.0})
    interval: str = Field(default="1d", example="1d")
    cash: float = Field(default=10000.0, example=10000.0)
    active: bool = Field(default=True, description="Whether to track this watchlist daily")


class UpdateWatchlistRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class WatchlistResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    ticker: str
    strategy: str
    parameters: Dict[str, Union[int, float]]
    interval: str
    cash: float
    active: bool
    current_value: Optional[float]
    pnl: Optional[float]
    return_pct: Optional[float]
    created_at: str
    last_updated: str


class WatchlistPositionResponse(BaseModel):
    id: int
    watchlist_id: int
    position_type: PositionType
    entry_date: str
    entry_price: float
    size: float
    exit_date: Optional[str]
    exit_price: Optional[float]
    pnl: Optional[float]
    status: PositionStatus


class WatchlistDetailResponse(BaseModel):
    watchlist: WatchlistResponse
    open_positions: List[WatchlistPositionResponse]
    closed_positions: List[WatchlistPositionResponse]
    total_trades: int
    winning_trades: int
    losing_trades: int


class WatchlistListResponse(BaseModel):
    success: bool
    count: int
    watchlists: List[WatchlistResponse]
