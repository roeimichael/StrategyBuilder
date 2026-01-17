from typing import Dict, Optional, Any, Union
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.config import BacktestConfig
from src.core.run_strategy import Run_strategy
from src.services.strategy_service import StrategyService
from src.data.run_repository import RunRepository


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

    def market_scan(self, strategy_name: str, start_date: Optional[str] = None,
                    end_date: Optional[str] = None, interval: str = BacktestConfig.DEFAULT_INTERVAL,
                    cash: float = BacktestConfig.DEFAULT_CASH,
                    parameters: Optional[Dict[str, Union[int, float]]] = None) -> Dict[str, Any]:
        from src.utils.sp500_tickers import get_sp500_tickers
        from src.utils.api_logger import logger

        tickers = get_sp500_tickers()
        total_pnl = 0.0
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        stocks_with_trades = 0
        all_returns = []
        first_start_date = None
        last_end_date = None
        initial_cash_per_stock = cash

        logger.info(f"Starting market scan with strategy '{strategy_name}' across {len(tickers)} stocks")

        for ticker in tickers:
            try:
                request = BacktestRequest(
                    ticker=ticker,
                    strategy=strategy_name,
                    start_date=start_date,
                    end_date=end_date,
                    interval=interval,
                    cash=initial_cash_per_stock,
                    parameters=parameters
                )

                response = self.run_backtest(request, save_run=False)

                total_pnl += response.pnl
                total_trades += response.total_trades

                if response.total_trades > 0:
                    stocks_with_trades += 1

                if response.advanced_metrics:
                    winning_trades += response.advanced_metrics.get('winning_trades', 0)
                    losing_trades += response.advanced_metrics.get('losing_trades', 0)

                all_returns.append(response.return_pct)

                if first_start_date is None:
                    first_start_date = response.start_date
                if last_end_date is None or response.end_date > last_end_date:
                    last_end_date = response.end_date

            except Exception as e:
                logger.warning(f"Failed to run backtest for {ticker}: {str(e)}")
                continue

        total_start_value = initial_cash_per_stock * len(tickers)
        total_end_value = total_start_value + total_pnl
        avg_return_pct = (total_pnl / total_start_value * 100) if total_start_value > 0 else 0.0

        sharpe_ratio = None
        if len(all_returns) > 0:
            import numpy as np
            returns_array = np.array(all_returns)
            if returns_array.std() > 0:
                sharpe_ratio = (returns_array.mean() / returns_array.std()) * np.sqrt(252)

        max_drawdown = None
        if len(all_returns) > 0:
            cumulative = np.cumprod(1 + np.array(all_returns) / 100)
            running_max = np.maximum.accumulate(cumulative)
            drawdowns = (cumulative - running_max) / running_max
            max_drawdown = drawdowns.min() * 100 if len(drawdowns) > 0 else None

        logger.info(f"Market scan completed: {stocks_with_trades}/{len(tickers)} stocks had trades, Total PnL: ${total_pnl:.2f}")

        return {
            'success': True,
            'strategy': strategy_name,
            'start_value': total_start_value,
            'end_value': total_end_value,
            'pnl': total_pnl,
            'return_pct': round(avg_return_pct, 2),
            'sharpe_ratio': round(sharpe_ratio, 2) if sharpe_ratio else None,
            'max_drawdown': round(max_drawdown, 2) if max_drawdown else None,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'interval': interval,
            'start_date': first_start_date,
            'end_date': last_end_date,
            'stocks_scanned': len(tickers),
            'stocks_with_trades': stocks_with_trades,
            'advanced_metrics': {
                'avg_return_per_stock': round(sum(all_returns) / len(all_returns), 2) if all_returns else 0.0,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round((winning_trades / total_trades * 100), 2) if total_trades > 0 else 0.0
            }
        }

    def get_snapshot(self, ticker: str, strategy_name: str, interval: str = "1d",
                     lookback_bars: int = 200, parameters: Optional[Dict[str, Union[int, float]]] = None,
                     cash: float = BacktestConfig.DEFAULT_CASH) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        from src.core.data_manager import DataManager

        strategy_class = StrategyService.load_strategy_class(strategy_name)
        if not strategy_class:
            raise ValueError(f"Strategy '{strategy_name}' not found")

        days_needed = lookback_bars * 2 if interval == "1d" else 30
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_needed)

        params = StrategyService.get_default_parameters(parameters)
        params['cash'] = cash

        runner = Run_strategy(params, strategy_class)
        results = runner.runstrat(ticker, start_date, interval, end_date)

        chart_data = results.get('chart_data', [])
        trades = results.get('trades', [])

        last_bar = {}
        if chart_data and len(chart_data) > 0:
            last_entry = chart_data[-1]
            last_bar = {
                'date': last_entry.get('date'),
                'open': last_entry.get('open'),
                'high': last_entry.get('high'),
                'low': last_entry.get('low'),
                'close': last_entry.get('close'),
                'volume': last_entry.get('volume', 0)
            }

        indicators = {}
        if chart_data and len(chart_data) > 0:
            last_entry = chart_data[-1]
            for key, value in last_entry.items():
                if key not in ['date', 'open', 'high', 'low', 'close', 'volume', 'signals']:
                    indicators[key] = value

        position_state = {
            'in_position': False,
            'position_type': None,
            'entry_price': None,
            'current_price': last_bar.get('close'),
            'size': None,
            'unrealized_pnl': None
        }

        if trades and len(trades) > 0:
            last_trade = trades[-1]
            if last_trade.get('exit_date') is None or last_trade.get('exit_price') is None:
                position_state['in_position'] = True
                position_state['position_type'] = 'long' if last_trade.get('size', 0) > 0 else 'short'
                position_state['entry_price'] = last_trade.get('entry_price')
                position_state['size'] = abs(last_trade.get('size', 0))

                if position_state['current_price'] and position_state['entry_price']:
                    if position_state['position_type'] == 'long':
                        position_state['unrealized_pnl'] = (position_state['current_price'] - position_state['entry_price']) * position_state['size']
                    else:
                        position_state['unrealized_pnl'] = (position_state['entry_price'] - position_state['current_price']) * position_state['size']

        recent_trades = trades[-10:] if len(trades) > 10 else trades

        return {
            'ticker': ticker,
            'strategy': strategy_name,
            'interval': interval,
            'lookback_bars': lookback_bars,
            'last_bar': last_bar,
            'indicators': indicators,
            'position_state': position_state,
            'recent_trades': recent_trades,
            'portfolio_value': results['end_value'],
            'cash': results['end_value'] - sum(t.get('pnl', 0) for t in trades),
            'timestamp': datetime.now().isoformat()
        }
