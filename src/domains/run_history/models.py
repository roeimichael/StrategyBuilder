from typing import Optional, Dict, Union
from pydantic import BaseModel, Field


class ReplayRunRequest(BaseModel):
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: Optional[str] = Field(None, example="1d")
    cash: Optional[float] = Field(None, example=10000.0)
    parameters: Optional[Dict[str, Union[int, float]]] = Field(None)


class SavedRunSummaryResponse(BaseModel):
    id: int
    ticker: str
    strategy: str
    interval: str
    pnl: Optional[float]
    return_pct: Optional[float]
    created_at: str


class SavedRunDetailResponse(BaseModel):
    id: int
    ticker: str
    strategy: str
    parameters: Dict[str, Union[int, float]]
    start_date: str
    end_date: str
    interval: str
    cash: float
    pnl: Optional[float]
    return_pct: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    total_trades: Optional[int]
    winning_trades: Optional[int]
    losing_trades: Optional[int]
    created_at: str
