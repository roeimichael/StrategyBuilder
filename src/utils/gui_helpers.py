"""Utility functions for StrategyBuilder GUI"""

import importlib.util
import inspect
import os
import re
import sys
from typing import List, Dict, Any

import pandas as pd
import requests


def get_sp500_tickers() -> List[str]:
    """Fetch S&P 500 ticker symbols from Wikipedia"""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url)[0]
        tickers = table['Symbol'].tolist()
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        return sorted(tickers)
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT']


def discover_strategies(strategies_path: str = None) -> Dict[str, Any]:
    """Auto-discover trading strategies from the strategies folder"""
    if strategies_path is None:
        strategies_path = os.path.join(os.path.dirname(__file__), 'strategies')

    strategies = {}

    try:
        strategy_files = [f for f in os.listdir(strategies_path)
                         if f.endswith('.py') and f != '__init__.py']

        for filename in strategy_files:
            filepath = os.path.join(strategies_path, filename)
            module_name = filename[:-3]

            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, '__init__') and name != 'Strategy_skeleton':
                        description = obj.__doc__.strip() if obj.__doc__ else f"Strategy from {filename}"
                        description = description.split('\n')[0]
                        sig = inspect.signature(obj.__init__)
                        params = {}

                        strategies[name] = {
                            'class': obj,
                            'file': filename,
                            'description': description,
                            'module': module_name,
                            'parameters': params
                        }

            except Exception as e:
                print(f"Error loading strategy from {filename}: {e}")
                continue

    except Exception as e:
        print(f"Error discovering strategies: {e}")

    return strategies


def get_strategy_parameters(strategy_class) -> Dict[str, Dict[str, Any]]:
    """Extract configurable parameters for a strategy"""
    parameters = {}

    if hasattr(strategy_class, 'params'):
        params_tuple = strategy_class.params
        for param in params_tuple:
            if isinstance(param, tuple) and len(param) >= 2:
                param_name = param[0]
                param_default = param[1]
                param_type = type(param_default).__name__

                parameters[param_name] = {
                    'default': param_default,
                    'type': param_type,
                    'description': f'{param_name} parameter'
                }

    return parameters


def format_strategy_name(class_name: str) -> str:
    """Convert class name to human-readable format"""
    name = re.sub(r'([A-Z])', r' \1', class_name).strip()
    name = name.replace('_', ' ')
    name = ' '.join(name.split())
    return name


def get_popular_tickers() -> Dict[str, List[str]]:
    """Return categorized lists of popular tickers"""
    return {
        'Tech Giants': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
        'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
        'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK'],
        'Consumer': ['WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'MPC'],
    }
