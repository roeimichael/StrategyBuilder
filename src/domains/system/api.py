from typing import Dict
from datetime import datetime
from fastapi import APIRouter
from src.shared.config import Config
from src.shared.utils.api_logger import log_errors
from src.domains.strategies.service import StrategyService

router = APIRouter(tags=["system"])
strategy_service = StrategyService()


@router.get("/")
@log_errors
def root() -> Dict[str, object]:
    """API root endpoint with information and available endpoints."""
    return {
        "name": Config.API_TITLE, "version": Config.API_VERSION, "status": "running", "docs": "/docs",
        "endpoints": {
            "strategies": "/strategies",
            "backtest": "/backtest",
            "market_data": "/market-data",
            "health": "/health",
            "runs": "/runs",
            "run_detail": "/runs/{run_id}",
            "replay_run": "/runs/{run_id}/replay",
            "parameters": "/parameters/default"
        }
    }


@router.get("/health")
@log_errors
def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.get("/parameters/default")
@log_errors
def get_default_params() -> Dict[str, object]:
    """Get default parameters for all strategies."""
    return {"success": True, "parameters": strategy_service.get_default_parameters()}
