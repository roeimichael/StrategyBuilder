from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from src.domains.backtests.service import BacktestService, BacktestRequest as ServiceBacktestRequest
from src.domains.backtests.models import BacktestRequest, BacktestResponse
from src.shared.exceptions import StrategyNotFoundError, StrategyLoadError
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/backtest", tags=["backtests"])
backtest_service = BacktestService()


def convert_to_columnar(chart_data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    """Convert chart data from row-based to columnar format."""
    if not chart_data:
        return {}
    columnar = {}
    for key in chart_data[0].keys():
        columnar[key] = [point.get(key) for point in chart_data]
    return columnar


@router.post("", response_model=BacktestResponse)
@log_errors
def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """Run a backtest with the specified parameters."""
    try:
        service_request = ServiceBacktestRequest(
            ticker=request.ticker, strategy=request.strategy, start_date=request.start_date,
            end_date=request.end_date, interval=request.interval, cash=request.cash, parameters=request.parameters
        )
        response = backtest_service.run_backtest(service_request)
        response_dict = response.dict()
        if not request.include_chart_data:
            response_dict['chart_data'] = None
        elif request.columnar_format and response_dict.get('chart_data'):
            response_dict['chart_data'] = convert_to_columnar(response_dict['chart_data'])
        return BacktestResponse(**response_dict)
    except (StrategyNotFoundError, StrategyLoadError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")
