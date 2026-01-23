from fastapi import APIRouter, HTTPException
from src.domains.market_scans.models import MarketScanRequest, MarketScanResponse
from src.domains.market_scans.service import MarketScanService
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/market-scan", tags=["market-scans"])
market_scan_service = MarketScanService()


@router.post("", response_model=MarketScanResponse)
@log_errors
def run_market_scan(request: MarketScanRequest) -> MarketScanResponse:
    """
    Run a strategy backtest across multiple tickers to find best performers.

    - **tickers**: List of ticker symbols to scan
    - **strategy**: Strategy name to apply
    - **start_date**: Backtest start date (YYYY-MM-DD)
    - **end_date**: Backtest end date (YYYY-MM-DD)
    - **interval**: Data interval (1d, 1h, etc.)
    - **cash**: Starting cash amount for each backtest
    - **parameters**: Strategy parameters (optional)
    - **min_return_pct**: Filter results by minimum return % (optional)
    - **min_sharpe_ratio**: Filter results by minimum Sharpe ratio (optional)
    """
    try:
        if len(request.tickers) > 500:
            raise HTTPException(
                status_code=400,
                detail="Too many tickers. Maximum 500 tickers per scan."
            )

        response = market_scan_service.run_market_scan(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market scan failed: {str(e)}")
