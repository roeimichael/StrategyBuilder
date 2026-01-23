from typing import Dict, List, Union
from datetime import datetime
from src.domains.optimizations.models import OptimizationRequest, OptimizationResponse, OptimizationResult
from src.domains.strategies.service import StrategyService
from src.domains.backtests.optimizer import StrategyOptimizer
from src.domains.market_data.manager import DataManager


class OptimizationService:
    def __init__(self):
        self.data_manager = DataManager()

    def run_optimization(self, request: OptimizationRequest) -> OptimizationResponse:
        """
        Run strategy optimization with specified parameter ranges.

        Args:
            request: OptimizationRequest containing ticker, strategy, date range, and parameter ranges

        Returns:
            OptimizationResponse with top performing parameter combinations
        """
        # Load strategy class
        strategy_class = StrategyService.load_strategy_class(request.strategy)

        # Parse dates
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        # Create optimizer
        optimizer = StrategyOptimizer(strategy_class, self.data_manager)

        # Run optimization
        results = optimizer.run_optimization(
            ticker=request.ticker,
            start_date=start_date,
            end_date=end_date,
            interval=request.interval,
            cash=request.cash,
            param_ranges=request.param_ranges
        )

        # Convert results to response models
        optimization_results = [
            OptimizationResult(
                parameters=result['parameters'],
                pnl=result['pnl'],
                return_pct=result['return_pct'],
                sharpe_ratio=result['sharpe_ratio'],
                start_value=result['start_value'],
                end_value=result['end_value']
            )
            for result in results[:20]  # Top 20 results
        ]

        return OptimizationResponse(
            success=True,
            ticker=request.ticker,
            strategy=request.strategy,
            interval=request.interval,
            start_date=request.start_date,
            end_date=request.end_date,
            total_combinations=len(results),
            top_results=optimization_results
        )
