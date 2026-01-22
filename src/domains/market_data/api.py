from typing import Dict
import datetime as dt
from fastapi import APIRouter, HTTPException
from src.domains.market_data.manager import DataManager
from src.domains.market_data.models import MarketDataRequest
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/market-data", tags=["market-data"])
data_manager = DataManager()


@router.post("")
@log_errors
def get_market_data(request: MarketDataRequest) -> Dict[str, object]:
    """Fetch historical market data for a ticker."""
    try:
        end_date = dt.date.today()
        period_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825,
                      'ytd': (dt.date.today() - dt.date(dt.date.today().year, 1, 1)).days, 'max': 3650}
        days = period_map.get(request.period, 365)
        start_date = end_date - dt.timedelta(days=days)
        data = data_manager.get_data(ticker=request.ticker, start_date=start_date, end_date=end_date,
                                     interval=request.interval)
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.ticker}")
        data_dict = data.reset_index().to_dict(orient='records')
        stats = {
            'mean': data['Close'].mean().item() if 'Close' in data else None,
            'std': data['Close'].std().item() if 'Close' in data else None,
            'min': data['Close'].min().item() if 'Close' in data else None,
            'max': data['Close'].max().item() if 'Close' in data else None,
            'volume_avg': data['Volume'].mean().item() if 'Volume' in data else None,
        }
        return {
            "success": True, "ticker": request.ticker, "period": request.period, "interval": request.interval,
            "data_points": len(data_dict), "data": data_dict, "statistics": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")
