from fastapi import APIRouter, HTTPException
from src.domains.live_monitor.models import LiveMonitorRequest, LiveMonitorResponse
from src.domains.live_monitor.service import LiveMonitorService
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/live-monitor", tags=["live-monitor"])
live_monitor_service = LiveMonitorService()


@router.post("", response_model=LiveMonitorResponse)
@log_errors
def get_live_prices(request: LiveMonitorRequest) -> LiveMonitorResponse:
    """
    Get current prices for a list of tickers without analysis.

    - **tickers**: List of ticker symbols (max 50)

    Returns current price, change from previous close, volume, and timestamp.
    This is a simple price monitoring endpoint without backtesting or strategy analysis.
    """
    try:
        if len(request.tickers) > 50:
            raise HTTPException(
                status_code=400,
                detail="Too many tickers. Maximum 50 tickers per request."
            )

        response = live_monitor_service.get_live_prices(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live prices: {str(e)}")
