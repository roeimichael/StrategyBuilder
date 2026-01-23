from typing import Dict, Optional, Any, Union
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.shared.config import BacktestConfig
from src.domains.backtests.engine import Run_strategy
from src.domains.strategies.service import StrategyService
from src.domains.run_history.repository import RunRepository


class BacktestRequest:
    def __init__(self, ticker: str, strategy: str, start_date: Optional[str] = None,
                 end_date: Optional[str] = None, interval: str = BacktestConfig.DEFAULT_INTERVAL,
                 cash: float = BacktestConfig.DEFAULT_CASH, parameters: Optional[Dict[str, Union[int, float]]] = None):
        self.ticker = ticker
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.cash = cash
        self.parameters = parameters or {}


class BacktestResponse:
    def __init__(self, success: bool, ticker: str, strategy: str, start_value: float, end_value: float,
                 pnl: float, return_pct: float, sharpe_ratio: Optional[float], max_drawdown: Optional[float],
                 total_trades: int, interval: str, start_date: str, end_date: str,
                 advanced_metrics: Optional[Dict[str, Any]] = None, chart_data: Optional[list] = None):
        self.success = success
        self.ticker = ticker
        self.strategy = strategy
        self.start_value = start_value
        self.end_value = end_value
        self.pnl = pnl
        self.return_pct = return_pct
        self.sharpe_ratio = sharpe_ratio
        self.max_drawdown = max_drawdown
        self.total_trades = total_trades
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.advanced_metrics = advanced_metrics
        self.chart_data = chart_data

    def dict(self) -> Dict[str, Any]:
        return {
            'success': self.success, 'ticker': self.ticker, 'strategy': self.strategy,
            'start_value': self.start_value, 'end_value': self.end_value, 'pnl': self.pnl,
            'return_pct': self.return_pct, 'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown, 'total_trades': self.total_trades,
            'interval': self.interval, 'start_date': self.start_date, 'end_date': self.end_date,
            'advanced_metrics': self.advanced_metrics, 'chart_data': self.chart_data
        }


class BacktestService:
    def __init__(self):
        self.run_repository = RunRepository()

    def run_backtest(self, request: BacktestRequest, save_run: bool = True) -> BacktestResponse:
        strategy_class = StrategyService.load_strategy_class(request.strategy)
        params = StrategyService.get_default_parameters(request.parameters)
        params['cash'] = request.cash
        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        else:
            start_date = datetime.now().date() - relativedelta(years=BacktestConfig.DEFAULT_BACKTEST_PERIOD_YEARS)
        end_date = None
        if request.end_date:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
        runner = Run_strategy(params, strategy_class)
        results = runner.runstrat(request.ticker, start_date, request.interval, end_date)

        response = BacktestResponse(
            success=True, ticker=results['ticker'], strategy=request.strategy,
            start_value=results['start_value'], end_value=results['end_value'], pnl=results['pnl'],
            return_pct=round(results['return_pct'], 2),
            sharpe_ratio=round(results['sharpe_ratio'], 2) if results['sharpe_ratio'] else None,
            max_drawdown=round(results['max_drawdown'], 2) if results['max_drawdown'] else None,
            total_trades=results['total_trades'], interval=results['interval'],
            start_date=str(results['start_date']), end_date=str(results['end_date']),
            advanced_metrics=results.get('advanced_metrics', {}), chart_data=results.get('chart_data')
        )

        if save_run:
            self._save_run(request, response)

        return response

    def _save_run(self, request: BacktestRequest, response: BacktestResponse):
        """Save the backtest run to the repository."""
        run_record = {
            'ticker': request.ticker,
            'strategy': request.strategy,
            'parameters': request.parameters,
            'start_date': response.start_date,
            'end_date': response.end_date,
            'interval': request.interval,
            'cash': request.cash,
            'pnl': response.pnl,
            'return_pct': response.return_pct,
            'sharpe_ratio': response.sharpe_ratio,
            'max_drawdown': response.max_drawdown,
            'total_trades': response.total_trades,
            'winning_trades': response.advanced_metrics.get('winning_trades') if response.advanced_metrics else None,
            'losing_trades': response.advanced_metrics.get('losing_trades') if response.advanced_metrics else None
        }
        self.run_repository.save_run(run_record)

    def run_backtest_from_saved_run(self, run_id: int, overrides: Optional[Dict[str, Any]] = None) -> BacktestResponse:
        """
        Replay a backtest from a saved run with optional parameter overrides.

        Args:
            run_id: The ID of the saved run to replay
            overrides: Optional dictionary of parameters to override (e.g., start_date, end_date, cash)

        Returns:
            BacktestResponse from the replayed backtest
        """
        saved_run = self.run_repository.get_run_by_id(run_id)
        if not saved_run:
            raise ValueError(f"Run with ID {run_id} not found")

        overrides = overrides or {}

        request = BacktestRequest(
            ticker=saved_run['ticker'],
            strategy=saved_run['strategy'],
            start_date=overrides.get('start_date', saved_run['start_date']),
            end_date=overrides.get('end_date', saved_run['end_date']),
            interval=overrides.get('interval', saved_run['interval']),
            cash=overrides.get('cash', saved_run['cash']),
            parameters=overrides.get('parameters', saved_run['parameters'])
        )

        return self.run_backtest(request, save_run=True)
