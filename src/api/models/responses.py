from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel

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

class StrategyInfo(BaseModel):
    module: str
    class_name: str
    description: str

class StrategyParameters(BaseModel):
    success: bool
    strategy: Dict[str, object]
