from typing import Dict, List, Union
from pydantic import BaseModel, Field


class OptimizationRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    start_date: str = Field(..., example="2023-01-01")
    end_date: str = Field(..., example="2024-01-01")
    interval: str = Field(default="1d", example="1d")
    cash: float = Field(default=10000.0, example=10000.0)
    param_ranges: Dict[str, List[Union[int, float]]] = Field(
        ...,
        example={"period": [10, 15, 20], "devfactor": [1.5, 2.0, 2.5]}
    )


class OptimizationResult(BaseModel):
    parameters: Dict[str, Union[int, float]]
    pnl: float
    return_pct: float
    sharpe_ratio: Union[float, None]
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
