from typing import Optional, List, Dict, Union
from pydantic import BaseModel


class ParameterInfo(BaseModel):
    name: str
    type: str
    default: Union[int, float]
    min: Union[int, float]
    max: Union[int, float]
    step: Union[int, float]
    description: str


class StrategyInfo(BaseModel):
    module: str
    class_name: str
    description: str
    optimizable_params: Optional[List[ParameterInfo]] = None


class StrategyParameters(BaseModel):
    success: bool
    strategy: Dict[str, object]
