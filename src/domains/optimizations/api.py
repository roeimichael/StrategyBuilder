"""Optimization API endpoints for strategy parameter optimization."""
from fastapi import APIRouter, HTTPException
from src.domains.optimizations.models import OptimizationRequest, OptimizationResponse
from src.domains.optimizations.service import OptimizationService
from src.shared.exceptions import StrategyNotFoundError, StrategyLoadError
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/optimize", tags=["optimizations"])
optimization_service = OptimizationService()


@router.post("", response_model=OptimizationResponse)
@log_errors
def run_optimization(request: OptimizationRequest) -> OptimizationResponse:
    try:
        response = optimization_service.run_optimization(request)
        return response
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
