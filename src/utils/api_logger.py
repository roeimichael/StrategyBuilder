import logging
import traceback
import functools
from datetime import datetime
from typing import Callable, Any
from pathlib import Path

log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "api_errors.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("StrategyBuilder.API")

def log_errors(func: Callable) -> Callable:
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_time = datetime.now().isoformat()
            error_msg = f"""
{'='*80}
ERROR TIMESTAMP: {error_time}
FUNCTION: {func.__name__}
MODULE: {func.__module__}
ERROR TYPE: {type(e).__name__}
ERROR MESSAGE: {str(e)}

ARGUMENTS:
{args}

KEYWORD ARGUMENTS:
{kwargs}

FULL TRACEBACK:
{traceback.format_exc()}
{'='*80}
"""
            logger.error(error_msg)
            raise

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_time = datetime.now().isoformat()
            error_msg = f"""
{'='*80}
ERROR TIMESTAMP: {error_time}
FUNCTION: {func.__name__}
MODULE: {func.__module__}
ERROR TYPE: {type(e).__name__}
ERROR MESSAGE: {str(e)}

ARGUMENTS:
{args}

KEYWORD ARGUMENTS:
{kwargs}

FULL TRACEBACK:
{traceback.format_exc()}
{'='*80}
"""
            logger.error(error_msg)
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

import asyncio
