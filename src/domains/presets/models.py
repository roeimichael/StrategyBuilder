from typing import Dict, Union, Optional
from pydantic import BaseModel, Field


class CreatePresetRequest(BaseModel):
    name: str = Field(..., example="My Bollinger Strategy")
    description: Optional[str] = Field(None, example="Conservative Bollinger Bands with 2.5 std dev")
    strategy: str = Field(..., example="bollinger_bands_strategy")
    parameters: Dict[str, Union[int, float]] = Field(
        ...,
        example={"period": 20, "devfactor": 2.5}
    )
    interval: str = Field(default="1d", example="1d")
    cash: float = Field(default=10000.0, example=10000.0)


class UpdatePresetRequest(BaseModel):
    name: Optional[str] = Field(None, example="Updated Name")
    description: Optional[str] = Field(None, example="Updated description")
    parameters: Optional[Dict[str, Union[int, float]]] = Field(None)
    interval: Optional[str] = Field(None, example="1h")
    cash: Optional[float] = Field(None, example=25000.0)


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
