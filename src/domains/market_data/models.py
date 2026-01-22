from pydantic import BaseModel, Field
from src.shared.config.backtest_config import BacktestConfig


class MarketDataRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    period: str = Field("1mo", example="1mo")
    interval: str = Field(BacktestConfig.DEFAULT_INTERVAL, example="1d")
