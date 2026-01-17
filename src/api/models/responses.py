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

class SavedRunSummaryResponse(BaseModel):
    id: int
    ticker: str
    strategy: str
    interval: str
    pnl: Optional[float]
    return_pct: Optional[float]
    created_at: str

class SavedRunDetailResponse(BaseModel):
    id: int
    ticker: str
    strategy: str
    parameters: Dict[str, Union[int, float]]
    start_date: str
    end_date: str
    interval: str
    cash: float
    pnl: Optional[float]
    return_pct: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    total_trades: Optional[int]
    winning_trades: Optional[int]
    losing_trades: Optional[int]
    created_at: str

class PresetResponse(BaseModel):
    id: int
    name: str
    ticker: str
    strategy: str
    parameters: Dict[str, Union[int, float]]
    interval: str
    notes: Optional[str]
    created_at: str

class SnapshotPositionState(BaseModel):
    in_position: bool
    position_type: Optional[str] = None
    entry_price: Optional[float] = None
    current_price: Optional[float] = None
    size: Optional[float] = None
    unrealized_pnl: Optional[float] = None

class SnapshotResponse(BaseModel):
    success: bool
    ticker: str
    strategy: str
    interval: str
    lookback_bars: int
    last_bar: Dict[str, Any]
    indicators: Dict[str, Any]
    position_state: SnapshotPositionState
    recent_trades: List[Dict[str, Any]]
    portfolio_value: float
    cash: float
    timestamp: str

class WatchlistEntryResponse(BaseModel):
    id: int
    name: str
    preset_id: Optional[int]
    run_id: Optional[int]
    frequency: str
    enabled: bool
    created_at: str
    last_run_at: Optional[str]

class StockScanResult(BaseModel):
    ticker: str
    pnl: float
    return_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    start_value: float
    end_value: float

class MarketScanResponse(BaseModel):
    success: bool
    strategy: str
    start_value: float
    end_value: float
    pnl: float
    return_pct: float
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    total_trades: int
    winning_trades: int
    losing_trades: int
    interval: str
    start_date: str
    end_date: str
    stocks_scanned: int
    stocks_with_trades: int
    stock_results: List[Dict[str, Any]]
    macro_statistics: Dict[str, Any]
