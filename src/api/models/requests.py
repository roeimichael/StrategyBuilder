from typing import Optional, Dict, Union
from pydantic import BaseModel, Field
from src.config.backtest_config import BacktestConfig

class BacktestRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: str = Field(BacktestConfig.DEFAULT_INTERVAL, example="1h")
    cash: float = Field(BacktestConfig.DEFAULT_CASH, example=10000.0)
    parameters: Optional[Dict[str, Union[int, float]]] = Field(None)
    include_chart_data: bool = Field(False, example=False)
    columnar_format: bool = Field(True, example=True)

class MarketDataRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    period: str = Field("1mo", example="1mo")
    interval: str = Field(BacktestConfig.DEFAULT_INTERVAL, example="1d")
