from fastapi import APIRouter, HTTPException
from src.domains.live_monitor.models import LiveMonitorRequest, LiveMonitorResponse
from src.domains.live_monitor.service import LiveMonitorService
from src.shared.utils.api_logger import log_errors
from src.shared.utils.config_reader import ConfigReader

router = APIRouter(prefix="/live-monitor", tags=["live-monitor"])
live_monitor_service = LiveMonitorService()
config = ConfigReader.load_domain_config('live_monitor')


@router.post("", response_model=LiveMonitorResponse)
@log_errors
def get_live_prices(request: LiveMonitorRequest) -> LiveMonitorResponse:
    """
    Get current prices for a list of tickers without analysis.

    - **tickers**: List of ticker symbols

    Returns current price, change from previous close, volume, and timestamp.
    This is a simple price monitoring endpoint without backtesting or strategy analysis.
    """
    try:
        if len(request.tickers) > config.MAX_TICKERS_PER_REQUEST:
            raise HTTPException(
                status_code=400,
                detail=f"Too many tickers. Maximum {config.MAX_TICKERS_PER_REQUEST} tickers per request."
            )

        response = live_monitor_service.get_live_prices(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live prices: {str(e)}")
