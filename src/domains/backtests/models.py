from typing import Optional, Dict, Union, List, Any
from pydantic import BaseModel, Field
from src.shared.config.backtest_config import BacktestConfig


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


class BacktestResponse(BaseModel):
    success: bool
    ticker: str
    strategy: str
    start_value: float
    end_value: float
    pnl: float
    return_pct: float
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    total_trades: int
    interval: str
    start_date: str
    end_date: str
    advanced_metrics: Optional[Dict[str, Any]] = None
    chart_data: Optional[Union[List[Dict[str, Any]], Dict[str, List[Any]]]] = None


class OptimizationRequest(BaseModel):
    ticker: str = Field(..., example="BTC-USD")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: str = Field(BacktestConfig.DEFAULT_INTERVAL, example="1d")
    cash: float = Field(BacktestConfig.DEFAULT_CASH, example=10000.0)
    optimization_params: Dict[str, List[Union[int, float]]] = Field(..., example={"period": [10, 20, 30], "devfactor": [1.5, 2.0, 2.5]})


class OptimizationResult(BaseModel):
    parameters: Dict[str, Union[int, float]]
    pnl: float
    return_pct: float
    sharpe_ratio: Optional[float]
    start_value: float
    end_value: float


class OptimizationResponse(BaseModel):
    success: bool
    ticker: str
    strategy: str
    interval: str
    start_date: str
    end_date: str
    total_combinations: int
    top_results: List[OptimizationResult]
