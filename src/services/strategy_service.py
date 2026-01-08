import os
import importlib
import inspect
from typing import Type, List, Dict, Optional, Any, Union
import backtrader as bt
from src.core.strategy_skeleton import Strategy_skeleton
from src.config import BacktestConfig
from src.exceptions import StrategyNotFoundError, StrategyLoadError

class StrategyInfo:
    def __init__(self, module: str, class_name: str, description: str):
        self.module = module
        self.class_name = class_name
        self.description = description
    def dict(self) -> Dict[str, str]:
        return {
            'module': self.module,
            'class_name': self.class_name,
            'description': self.description
        }

class StrategyService:
    @staticmethod
    def load_strategy_class(strategy_name: str) -> Type[bt.Strategy]:
        try:
            if strategy_name.endswith('.py'):
                strategy_name = strategy_name[:-3]
            module = importlib.import_module(f'src.strategies.{strategy_name}')
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, bt.Strategy) and obj not in [bt.Strategy, Strategy_skeleton]:
                    return obj
            raise StrategyNotFoundError(f"No valid strategy class found in {strategy_name}")
        except ImportError as e:
            raise StrategyNotFoundError(f"Strategy module '{strategy_name}' not found: {str(e)}")
        except Exception as e:
            raise StrategyLoadError(f"Error loading strategy: {str(e)}")
    @staticmethod
    def list_strategies() -> List[StrategyInfo]:
        strategies_dir = os.path.join(os.path.dirname(__file__), '..', 'strategies')
        strategies = []
        for filename in os.listdir(strategies_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'src.strategies.{module_name}')
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, bt.Strategy) and obj not in [bt.Strategy, Strategy_skeleton]:
                            strategies.append(StrategyInfo(
                                module=module_name,
                                class_name=name,
                                description=obj.__doc__ or ""
                            ))
                except Exception:
                    pass
        return strategies
    @staticmethod
    def get_strategy_info(strategy_name: str) -> Dict[str, Any]:
        strategy_class = StrategyService.load_strategy_class(strategy_name)
        params = {}
        if hasattr(strategy_class, 'params'):
            try:
                for param_name in dir(strategy_class.params):
                    if not param_name.startswith('_'):
                        param_value = getattr(strategy_class.params, param_name, None)
                        if param_value is not None and not callable(param_value):
                            params[param_name] = param_value
            except Exception:
                pass
        return {
            "module": strategy_name,
            "class_name": strategy_class.__name__,
            "description": strategy_class.__doc__ or "",
            "parameters": params
        }
    @staticmethod
    def get_default_parameters(strategy_params: Optional[Dict[str, Union[int, float]]] = None) -> Dict[str, Union[int, float]]:
        params = BacktestConfig.get_default_parameters()
        if strategy_params:
            params.update(strategy_params)
        return params
