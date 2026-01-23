from typing import List, Optional
from pydantic import BaseModel, Field


class TickerPrice(BaseModel):
    ticker: str
    price: Optional[float]
    change: Optional[float]
    change_pct: Optional[float]
    volume: Optional[int]
    timestamp: str
    error: Optional[str] = None


class LiveMonitorRequest(BaseModel):
    tickers: List[str] = Field(..., example=["AAPL", "MSFT", "GOOGL"], max_items=50)


class LiveMonitorResponse(BaseModel):
    success: bool
    timestamp: str
    prices: List[TickerPrice]
