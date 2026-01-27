from typing import List, Dict, Union, Optional
from pydantic import BaseModel, Field


class MarketScanRequest(BaseModel):
    tickers: Optional[List[str]] = Field(None, example=["AAPL", "MSFT", "GOOGL", "AMZN"], description="Optional ticker list. If not provided, defaults to S&P 500 tickers")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    start_date: str = Field(..., example="2023-01-01")
    end_date: str = Field(..., example="2024-01-01")
    interval: str = Field(default="1d", example="1d")
    cash: float = Field(default=10000.0, example=10000.0)
    parameters: Optional[Dict[str, Union[int, float]]] = Field(default=None)
    min_return_pct: Optional[float] = Field(default=None, example=5.0, description="Filter results by minimum return %")
    min_sharpe_ratio: Optional[float] = Field(default=None, example=1.0, description="Filter results by minimum Sharpe ratio")


class MarketScanTickerResult(BaseModel):
    ticker: str
    success: bool
    pnl: Optional[float] = None
    return_pct: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    total_trades: Optional[int] = None
    error: Optional[str] = None


class MarketScanResponse(BaseModel):
    success: bool
    strategy: str
    start_date: str
    end_date: str
    interval: str
    total_tickers: int
    successful_scans: int
    failed_scans: int
    results: List[MarketScanTickerResult]
    top_performers: List[MarketScanTickerResult]  # Sorted by return_pct
