"""
Utility functions for StrategyBuilder GUI
"""
import os
import sys
import pandas as pd
import requests
from typing import List, Dict, Any
import importlib.util
import inspect


def get_sp500_tickers() -> List[str]:
    """
    Fetch S&P 500 ticker symbols from Wikipedia
    Returns a list of ticker symbols
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url)[0]
        tickers = table['Symbol'].tolist()
        # Clean up tickers (some may have extra characters)
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        return sorted(tickers)
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        # Return a default list of popular tickers
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT']


def discover_strategies(strategies_path: str = None) -> Dict[str, Any]:
    """
    Auto-discover trading strategies from the strategies folder
    Returns a dictionary with strategy names and their classes
    """
    if strategies_path is None:
        strategies_path = os.path.join(os.path.dirname(__file__), 'strategies')

    strategies = {}

    try:
        # List all Python files in strategies directory
        strategy_files = [f for f in os.listdir(strategies_path)
                         if f.endswith('.py') and f != '__init__.py']

        for filename in strategy_files:
            filepath = os.path.join(strategies_path, filename)
            module_name = filename[:-3]  # Remove .py extension

            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Find strategy classes (subclasses of Strategy or similar)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, '__init__') and name != 'Strategy_skeleton':
                        # Get strategy description from docstring or filename
                        description = obj.__doc__.strip() if obj.__doc__ else f"Strategy from {filename}"
                        description = description.split('\n')[0]  # First line only

                        # Get parameters from __init__ signature
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
    """
    Extract configurable parameters for a strategy
    Returns a dictionary of parameter names and their default values/types
    """
    parameters = {}

    # Check if strategy has params attribute (Backtrader convention)
    if hasattr(strategy_class, 'params'):
        params_tuple = strategy_class.params
        for param in params_tuple:
            if isinstance(param, tuple) and len(param) >= 2:
                param_name = param[0]
                param_default = param[1]

                # Infer type from default value
                param_type = type(param_default).__name__

                parameters[param_name] = {
                    'default': param_default,
                    'type': param_type,
                    'description': f'{param_name} parameter'
                }

    return parameters


def format_strategy_name(class_name: str) -> str:
    """
    Convert class name to human-readable format
    Example: CMF_ATR_MACD_Strategy -> CMF ATR MACD Strategy
    """
    # Add spaces before capitals
    import re
    name = re.sub(r'([A-Z])', r' \1', class_name).strip()
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    # Clean up multiple spaces
    name = ' '.join(name.split())
    return name


def get_popular_tickers() -> Dict[str, List[str]]:
    """
    Return categorized lists of popular tickers
    """
    return {
        'Tech Giants': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
        'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
        'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK'],
        'Consumer': ['WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'MPC'],
    }
