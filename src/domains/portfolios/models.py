from typing import List, Optional
from pydantic import BaseModel, Field


class PortfolioHolding(BaseModel):
    ticker: str = Field(..., example="AAPL")
    shares: float = Field(..., example=100.0)
    weight: Optional[float] = Field(None, example=0.25, description="Weight in portfolio (0-1)")


class CreatePortfolioRequest(BaseModel):
    name: str = Field(..., example="My Tech Portfolio")
    description: Optional[str] = Field(None, example="Large cap tech stocks")
    holdings: List[PortfolioHolding] = Field(..., min_items=1)


class UpdatePortfolioRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    holdings: Optional[List[PortfolioHolding]] = None


class PortfolioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    holdings: List[PortfolioHolding]
    total_stocks: int
    created_at: str
    updated_at: str


class PortfolioListResponse(BaseModel):
    success: bool
    count: int
    portfolios: List[PortfolioResponse]


class PortfolioBacktestRequest(BaseModel):
    preset_id: int = Field(..., description="Preset ID to apply to portfolio")
    start_date: str = Field(..., example="2023-01-01")
    end_date: str = Field(..., example="2024-01-01")
    use_weights: bool = Field(default=False, description="Use portfolio weights for position sizing")


class PortfolioBacktestResult(BaseModel):
    ticker: str
    weight: Optional[float]
    pnl: float
    return_pct: float
    sharpe_ratio: Optional[float]


class PortfolioBacktestResponse(BaseModel):
    success: bool
    portfolio_name: str
    strategy: str
    weighted_pnl: Optional[float]
    weighted_return_pct: Optional[float]
    results: List[PortfolioBacktestResult]
