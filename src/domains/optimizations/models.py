from typing import Dict, List, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re


class OptimizationRequest(BaseModel):
    ticker: str = Field(..., example="AAPL", min_length=1, max_length=10)
    strategy: str = Field(..., example="bollinger_bands_strategy", min_length=1, max_length=100)
    start_date: str = Field(..., example="2023-01-01")
    end_date: str = Field(..., example="2024-01-01")
    interval: str = Field(default="1d", example="1d")
    cash: float = Field(default=10000.0, example=10000.0, gt=0)
    param_ranges: Dict[str, List[Union[int, float]]] = Field(
        ...,
        example={"period": [10, 15, 20], "devfactor": [1.5, 2.0, 2.5]}
    )

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not re.match(r'^[A-Z0-9\-\.]+$', v.upper()):
            raise ValueError('Ticker must contain only alphanumeric characters, hyphens, and dots')
        return v.upper()

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @field_validator('interval')
    @classmethod
    def validate_interval(cls, v: str) -> str:
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        if v not in valid_intervals:
            raise ValueError(f'Interval must be one of: {", ".join(valid_intervals)}')
        return v

    @field_validator('param_ranges')
    @classmethod
    def validate_param_ranges(cls, v: Dict[str, List[Union[int, float]]]) -> Dict[str, List[Union[int, float]]]:
        if not v:
            raise ValueError('param_ranges cannot be empty')
        for param_name, values in v.items():
            if not values:
                raise ValueError(f'Parameter "{param_name}" must have at least one value')
            if len(values) > 100:
                raise ValueError(f'Parameter "{param_name}" has too many values (max 100)')
        return v


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
