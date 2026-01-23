from typing import Dict
from fastapi import APIRouter, HTTPException
from src.domains.strategies.service import StrategyService
from src.shared.exceptions import StrategyNotFoundError, StrategyLoadError
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/strategies", tags=["strategies"])
strategy_service = StrategyService()


@router.get("")
@log_errors
def get_strategies() -> Dict[str, object]:
    """List all available trading strategies."""
    try:
        strategies = strategy_service.list_strategies()
        return {"success": True, "count": len(strategies), "strategies": [s.dict() for s in strategies]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_name}")
@log_errors
def get_strategy_info(strategy_name: str) -> Dict[str, object]:
    """Get detailed information about a specific strategy."""
    try:
        strategy_info = strategy_service.get_strategy_info(strategy_name)
        return {"success": True, "strategy": strategy_info}
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Note: /parameters/default endpoint is in system/api.py
