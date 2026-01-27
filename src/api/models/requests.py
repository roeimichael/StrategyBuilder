from typing import Optional, Dict, Union, List
from pydantic import BaseModel, Field
from src.shared.config import BacktestConfig

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

class OptimizationRequest(BaseModel):
    ticker: str = Field(..., example="BTC-USD")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: str = Field(BacktestConfig.DEFAULT_INTERVAL, example="1d")
    cash: float = Field(BacktestConfig.DEFAULT_CASH, example=10000.0)
    optimization_params: Dict[str, List[Union[int, float]]] = Field(..., example={"period": [10, 20, 30], "devfactor": [1.5, 2.0, 2.5]})

class MarketDataRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    period: str = Field("1mo", example="1mo")
    interval: str = Field(BacktestConfig.DEFAULT_INTERVAL, example="1d")

class ReplayRunRequest(BaseModel):
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: Optional[str] = Field(None, example="1d")
    cash: Optional[float] = Field(None, example=10000.0)
    parameters: Optional[Dict[str, Union[int, float]]] = Field(None)
