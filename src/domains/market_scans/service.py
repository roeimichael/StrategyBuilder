from typing import List
from datetime import datetime
from src.domains.market_scans.models import MarketScanRequest, MarketScanResponse, MarketScanTickerResult
from src.domains.backtests.service import BacktestService, BacktestRequest
from src.shared.utils.config_reader import ConfigReader


class MarketScanService:
    def __init__(self):
        self.backtest_service = BacktestService()
        self.config = ConfigReader.load_domain_config('market_scans')

    def run_market_scan(self, request: MarketScanRequest) -> MarketScanResponse:
        """
        Run a strategy backtest across multiple tickers.

        Args:
            request: MarketScanRequest containing list of tickers and strategy config

        Returns:
            MarketScanResponse with results for each ticker
        """
        results: List[MarketScanTickerResult] = []
        successful_scans = 0
        failed_scans = 0

        for ticker in request.tickers:
            try:
                # Create backtest request for this ticker
                backtest_request = BacktestRequest(
                    ticker=ticker,
                    strategy=request.strategy,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    interval=request.interval,
                    cash=request.cash,
                    parameters=request.parameters or {}
                )

                # Run backtest (don't save to run history by default)
                backtest_response = self.backtest_service.run_backtest(
                    backtest_request,
                    save_run=self.config.SAVE_SCAN_RUNS
                )

                # Apply filters if specified
                if request.min_return_pct is not None and backtest_response.return_pct < request.min_return_pct:
                    continue
                if request.min_sharpe_ratio is not None and (
                    backtest_response.sharpe_ratio is None or backtest_response.sharpe_ratio < request.min_sharpe_ratio
                ):
                    continue

                results.append(MarketScanTickerResult(
                    ticker=ticker,
                    success=True,
                    pnl=backtest_response.pnl,
                    return_pct=backtest_response.return_pct,
                    sharpe_ratio=backtest_response.sharpe_ratio,
                    max_drawdown=backtest_response.max_drawdown,
                    total_trades=backtest_response.total_trades
                ))
                successful_scans += 1

            except Exception as e:
                results.append(MarketScanTickerResult(
                    ticker=ticker,
                    success=False,
                    error=str(e)
                ))
                failed_scans += 1

        # Sort results by return_pct descending
        successful_results = [r for r in results if r.success]
        successful_results.sort(key=lambda x: x.return_pct or float('-inf'), reverse=True)

        return MarketScanResponse(
            success=True,
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval,
            total_tickers=len(request.tickers),
            successful_scans=successful_scans,
            failed_scans=failed_scans,
            results=results,
            top_performers=successful_results[:self.config.TOP_PERFORMERS_COUNT]
        )
