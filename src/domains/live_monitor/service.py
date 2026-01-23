import yfinance as yf
from datetime import datetime
from typing import List
from src.domains.live_monitor.models import LiveMonitorRequest, LiveMonitorResponse, TickerPrice


class LiveMonitorService:
    """Service for fetching real-time stock prices."""

    def get_live_prices(self, request: LiveMonitorRequest) -> LiveMonitorResponse:
        """
        Fetch current prices for a list of tickers.

        Args:
            request: LiveMonitorRequest with list of tickers

        Returns:
            LiveMonitorResponse with current prices
        """
        prices = []
        timestamp = datetime.now().isoformat()

        for ticker_symbol in request.tickers:
            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.fast_info

                # Get current price and previous close
                current_price = info.get('lastPrice') or info.get('regularMarketPrice')
                prev_close = info.get('previousClose')

                change = None
                change_pct = None
                if current_price and prev_close:
                    change = current_price - prev_close
                    change_pct = (change / prev_close) * 100

                prices.append(TickerPrice(
                    ticker=ticker_symbol,
                    price=current_price,
                    change=change,
                    change_pct=change_pct,
                    volume=info.get('regularMarketVolume'),
                    timestamp=timestamp
                ))

            except Exception as e:
                prices.append(TickerPrice(
                    ticker=ticker_symbol,
                    price=None,
                    change=None,
                    change_pct=None,
                    volume=None,
                    timestamp=timestamp,
                    error=str(e)
                ))

        return LiveMonitorResponse(
            success=True,
            timestamp=timestamp,
            prices=prices
        )
