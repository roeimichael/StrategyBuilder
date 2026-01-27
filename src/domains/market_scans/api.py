from fastapi import APIRouter, HTTPException
from src.domains.market_scans.models import MarketScanRequest, MarketScanResponse
from src.domains.market_scans.service import MarketScanService
from src.domains.market_data.manager import DataManager
from src.shared.utils.api_logger import log_errors
from src.shared.utils.config_reader import ConfigReader

router = APIRouter(prefix="/market-scan", tags=["market-scans"])
market_scan_service = MarketScanService()
config = ConfigReader.load_domain_config('market_scans')


@router.post("", response_model=MarketScanResponse)
@log_errors
def run_market_scan(request: MarketScanRequest) -> MarketScanResponse:
    """
    Run a strategy backtest across multiple tickers to find best performers.

    - **tickers**: List of ticker symbols to scan (optional, defaults to S&P 500)
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
        # If no tickers provided, use S&P 500 tickers
        if request.tickers is None or len(request.tickers) == 0:
            request.tickers = DataManager.get_sp500_tickers()

        if len(request.tickers) > config.MAX_TICKERS_PER_SCAN:
            raise HTTPException(
                status_code=400,
                detail=f"Too many tickers. Maximum {config.MAX_TICKERS_PER_SCAN} tickers per scan."
            )

        response = market_scan_service.run_market_scan(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market scan failed: {str(e)}")
