from typing import Dict, Optional, Any, Union
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.config import BacktestConfig
from src.core.run_strategy import Run_strategy
from src.services.strategy_service import StrategyService


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
    @staticmethod
    def run_backtest(request: BacktestRequest) -> BacktestResponse:
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
        return BacktestResponse(
            success=True, ticker=results['ticker'], strategy=request.strategy,
            start_value=results['start_value'], end_value=results['end_value'], pnl=results['pnl'],
            return_pct=round(results['return_pct'], 2),
            sharpe_ratio=round(results['sharpe_ratio'], 2) if results['sharpe_ratio'] else None,
            max_drawdown=round(results['max_drawdown'], 2) if results['max_drawdown'] else None,
            total_trades=results['total_trades'], interval=results['interval'],
            start_date=str(results['start_date']), end_date=str(results['end_date']),
            advanced_metrics=results.get('advanced_metrics', {}), chart_data=results.get('chart_data')
        )
