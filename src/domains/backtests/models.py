from typing import Optional, Dict, Union, List, Any
from pydantic import BaseModel, Field, field_validator, ValidationError
from datetime import datetime
import re


class BacktestRequest(BaseModel):
    ticker: str = Field(..., example="AAPL", min_length=1, max_length=10)
    strategy: str = Field(..., example="bollinger_bands_strategy", min_length=1, max_length=100)
    start_date: Optional[str] = Field(None, example="2024-01-01")
    end_date: Optional[str] = Field(None, example="2024-12-31")
    interval: str = Field("1d", example="1d")
    cash: float = Field(10000.0, example=10000.0, gt=0)
    parameters: Optional[Dict[str, Union[int, float]]] = Field(None)
    include_chart_data: bool = Field(False, example=False)
    columnar_format: bool = Field(True, example=True)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not re.match(r'^[A-Z0-9\-\.]+$', v.upper()):
            raise ValueError('Ticker must contain only alphanumeric characters, hyphens, and dots')
        return v.upper()

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
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
