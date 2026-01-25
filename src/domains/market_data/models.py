from pydantic import BaseModel, Field, field_validator
import re


class MarketDataRequest(BaseModel):
    ticker: str = Field(..., example="AAPL", min_length=1, max_length=10)
    period: str = Field("1mo", example="1mo")
    interval: str = Field("1d", example="1d")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not re.match(r'^[A-Z0-9\-\.]+$', v.upper()):
            raise ValueError('Ticker must contain only alphanumeric characters, hyphens, and dots')
        return v.upper()

    @field_validator('period')
    @classmethod
    def validate_period(cls, v: str) -> str:
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max']
        if v not in valid_periods:
            raise ValueError(f'Period must be one of: {", ".join(valid_periods)}')
        return v

    @field_validator('interval')
    @classmethod
    def validate_interval(cls, v: str) -> str:
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        if v not in valid_intervals:
            raise ValueError(f'Interval must be one of: {", ".join(valid_intervals)}')
        return v
