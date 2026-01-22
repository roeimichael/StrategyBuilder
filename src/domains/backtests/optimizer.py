from typing import Dict, List, Any, Type, Union
from itertools import product
from datetime import date
import backtrader as bt
from src.domains.market_data.manager import DataManager

class StrategyOptimizer:
    def __init__(self, strategy_cls: Type[bt.Strategy], data_manager: DataManager):
        self.strategy_cls = strategy_cls
        self.data_manager = data_manager
        self.max_combinations = 1000
    def run_optimization(self, ticker: str, start_date: date, end_date: date,
                        interval: str, cash: float, param_ranges: Dict[str, List[Union[int, float]]]) -> List[Dict[str, Any]]:
        total_combinations = 1
        for param_values in param_ranges.values():
            total_combinations *= len(param_values)
        if total_combinations > self.max_combinations:
            raise ValueError(f"Too many parameter combinations: {total_combinations}. Maximum allowed: {self.max_combinations}")
        data = self.data_manager.get_data(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval)
        if data.empty:
            raise ValueError(f"No data available for {ticker}")
        bt_data = bt.feeds.PandasData(dataname=data)
        param_names = list(param_ranges.keys())
        param_values_list = [param_ranges[name] for name in param_names]
        results = []
        for param_combination in product(*param_values_list):
            params_dict = dict(zip(param_names, param_combination))
            cerebro = bt.Cerebro()
            cerebro.adddata(bt_data)
            cerebro.broker.setcash(cash)
            cerebro.broker.setcommission(commission=0.001)
            cerebro.addstrategy(self.strategy_cls, args=params_dict, **params_dict)
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days, riskfreerate=0.0)
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            strategies = cerebro.run()
            strategy = strategies[0]
            start_value = cash
            end_value = strategy.broker.getvalue()
            pnl = end_value - start_value
            return_pct = (pnl / start_value) * 100
            sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio', None)
            results.append({
                'parameters': params_dict,
                'pnl': pnl,
                'return_pct': return_pct,
                'sharpe_ratio': sharpe,
                'start_value': start_value,
                'end_value': end_value
            })
        results.sort(key=lambda x: x['pnl'], reverse=True)
        return results[:5]
