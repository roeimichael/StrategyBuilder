import os
import importlib
import inspect
from typing import Type, List, Dict, Optional, Any
import backtrader as bt

from src.core.strategy_skeleton import Strategy_skeleton
from src.config import Config


class StrategyInfo:
    """Data class for strategy information"""
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
    """
    Service for managing trading strategies.
    Handles strategy discovery, loading, and parameter management.
    """

    @staticmethod
    def load_strategy_class(strategy_name: str) -> Type[bt.Strategy]:
        """
        Load a strategy class by name.

        Args:
            strategy_name: Name of the strategy module (with or without .py extension)

        Returns:
            The strategy class

        Raises:
            ValueError: If strategy not found or invalid
        """
        try:
            if strategy_name.endswith('.py'):
                strategy_name = strategy_name[:-3]

            module = importlib.import_module(f'src.strategies.{strategy_name}')

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, bt.Strategy) and obj not in [bt.Strategy, Strategy_skeleton]:
                    return obj

            raise ValueError(f"No valid strategy class found in {strategy_name}")

        except ImportError as e:
            raise ValueError(f"Strategy module '{strategy_name}' not found: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading strategy: {str(e)}")

    @staticmethod
    def list_strategies() -> List[StrategyInfo]:
        """
        List all available strategies.

        Returns:
            List of StrategyInfo objects
        """
        strategies_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'strategies'
        )
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
        """
        Get detailed information about a specific strategy.

        Args:
            strategy_name: Name of the strategy

        Returns:
            Dictionary containing strategy details and parameters

        Raises:
            ValueError: If strategy not found
        """
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
    def get_default_parameters(strategy_params: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Get default backtest parameters, optionally merged with strategy-specific parameters.

        Args:
            strategy_params: Optional strategy-specific parameters to merge

        Returns:
            Merged parameter dictionary
        """
        params = Config.get_default_parameters()

        if strategy_params:
            params.update(strategy_params)

        return params
