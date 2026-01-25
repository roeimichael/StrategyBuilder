from typing import Dict, Union, Optional
from pydantic import BaseModel, Field, field_validator


class CreatePresetRequest(BaseModel):
    name: str = Field(..., example="My Bollinger Strategy", min_length=1, max_length=100)
    description: Optional[str] = Field(None, example="Conservative Bollinger Bands with 2.5 std dev", max_length=500)
    strategy: str = Field(..., example="bollinger_bands_strategy", min_length=1, max_length=100)
    parameters: Dict[str, Union[int, float]] = Field(
        ...,
        example={"period": 20, "devfactor": 2.5}
    )
    interval: str = Field(default="1d", example="1d")
    cash: float = Field(default=10000.0, example=10000.0, gt=0)

    @field_validator('interval')
    @classmethod
    def validate_interval(cls, v: str) -> str:
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        if v not in valid_intervals:
            raise ValueError(f'Interval must be one of: {", ".join(valid_intervals)}')
        return v


class UpdatePresetRequest(BaseModel):
    name: Optional[str] = Field(None, example="Updated Name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, example="Updated description", max_length=500)
    parameters: Optional[Dict[str, Union[int, float]]] = Field(None)
    interval: Optional[str] = Field(None, example="1h")
    cash: Optional[float] = Field(None, example=25000.0, gt=0)

    @field_validator('interval')
    @classmethod
    def validate_interval(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        if v not in valid_intervals:
            raise ValueError(f'Interval must be one of: {", ".join(valid_intervals)}')
        return v


class PresetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    strategy: str
    parameters: Dict[str, Union[int, float]]
    interval: str
    cash: float
    created_at: str
    updated_at: str


class PresetListResponse(BaseModel):
    success: bool
    count: int
    presets: list[PresetResponse]
