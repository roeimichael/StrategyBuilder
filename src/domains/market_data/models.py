from pydantic import BaseModel, Field


class MarketDataRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    period: str = Field("1mo", example="1mo")
    interval: str = Field("1d", example="1d")
