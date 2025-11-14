"""FastAPI REST API for StrategyBuilder automation

This module provides REST API endpoints for programmatic backtesting
and strategy management.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.config_loader import ConfigLoader
from src.core.vectorized_backtest import (
    run_vectorized_backtest,
    VectorizedBollingerBands,
    VectorizedSMA,
    VectorizedRSI
)
from src.core.run_strategy import Run_strategy

# Initialize FastAPI
app = FastAPI(
    title="StrategyBuilder API",
    description="REST API for automated strategy backtesting",
    version="1.0.0"
)

# Load configuration
config = ConfigLoader(os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml'))
api_config = config.get_api_config()

# Configure CORS
if api_config.get('cors', {}).get('enabled', True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config.get('cors', {}).get('allowed_origins', ["*"]),
        allow_credentials=True,
        allow_methods=api_config.get('cors', {}).get('allowed_methods', ["*"]),
        allow_headers=api_config.get('cors', {}).get('allowed_headers', ["*"]),
    )


# Pydantic models for request/response validation
class BacktestRequest(BaseModel):
    """Request model for backtest endpoint"""
    ticker: str = Field(..., description="Stock ticker symbol", example="AAPL")
    strategy: str = Field(..., description="Strategy name", example="bollinger_bands")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)", example="2023-01-01")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)", example="2024-01-01")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Strategy parameters")
    use_vectorized: bool = Field(True, description="Use vectorized backtesting")
    interval: str = Field("1d", description="Data interval")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "strategy": "bollinger_bands",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "parameters": {
                    "period": 20,
                    "devfactor": 2.0
                },
                "use_vectorized": True,
                "interval": "1d"
            }
        }


class BacktestResponse(BaseModel):
    """Response model for backtest endpoint"""
    success: bool
    ticker: str
    strategy: str
    start_date: str
    end_date: str
    results: Dict[str, Any]
    execution_time_ms: float


class StrategyInfo(BaseModel):
    """Strategy information model"""
    name: str
    description: str
    default_parameters: Dict[str, Any]
    optimization_ranges: Dict[str, List]
    constraints: Dict[str, Dict[str, float]]


class StrategyListResponse(BaseModel):
    """Response model for strategies endpoint"""
    strategies: List[StrategyInfo]
    total_count: int


# Strategy registry
AVAILABLE_STRATEGIES = {
    'bollinger_bands': {
        'class': VectorizedBollingerBands,
        'description': 'Bollinger Bands mean reversion strategy',
        'vectorized': True
    },
    'sma_crossover': {
        'class': VectorizedSMA,
        'description': 'Simple Moving Average crossover strategy',
        'vectorized': True
    },
    'rsi': {
        'class': VectorizedRSI,
        'description': 'RSI overbought/oversold strategy',
        'vectorized': True
    }
}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "StrategyBuilder API",
        "version": "1.0.0",
        "endpoints": {
            "POST /backtest": "Run a backtest with specified parameters",
            "GET /strategies": "List available strategies",
            "GET /docs": "API documentation (Swagger UI)",
            "GET /redoc": "API documentation (ReDoc)"
        }
    }


@app.get("/strategies", response_model=StrategyListResponse)
async def list_strategies():
    """
    List all available trading strategies

    Returns:
        List of available strategies with their configurations
    """
    strategies = []

    for strategy_name, strategy_info in AVAILABLE_STRATEGIES.items():
        # Get strategy config from config file
        defaults = config.get_strategy_defaults(strategy_name)
        optimization = config.get_strategy_optimization_ranges(strategy_name)
        constraints = config.get_strategy_constraints(strategy_name)

        strategies.append(StrategyInfo(
            name=strategy_name,
            description=strategy_info['description'],
            default_parameters=defaults,
            optimization_ranges=optimization,
            constraints=constraints
        ))

    return StrategyListResponse(
        strategies=strategies,
        total_count=len(strategies)
    )


@app.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run a backtest with specified parameters

    Args:
        request: BacktestRequest with ticker, strategy, dates, and parameters

    Returns:
        BacktestResponse with results

    Raises:
        HTTPException: If strategy not found or backtest fails
    """
    import time
    start_time = time.time()

    # Validate strategy
    if request.strategy not in AVAILABLE_STRATEGIES:
        raise HTTPException(
            status_code=400,
            detail=f"Strategy '{request.strategy}' not found. Available strategies: {list(AVAILABLE_STRATEGIES.keys())}"
        )

    strategy_info = AVAILABLE_STRATEGIES[request.strategy]

    # Get parameters
    if request.parameters:
        params = request.parameters
    else:
        params = config.get_strategy_defaults(request.strategy)

    # Validate parameters
    if not config.validate_parameters(request.strategy, params):
        raise HTTPException(
            status_code=400,
            detail="Parameters violate strategy constraints"
        )

    # Parse dates
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
        )

    # Run backtest
    try:
        if request.use_vectorized and strategy_info.get('vectorized'):
            # Use vectorized backtest
            results = run_vectorized_backtest(
                ticker=request.ticker,
                start_date=start_date,
                end_date=end_date,
                strategy_class=strategy_info['class'],
                params=params
            )
        else:
            # Use traditional backtest
            runner = Run_strategy(params, strategy_info['class'])
            results = runner.runstrat(
                request.ticker,
                start_date,
                request.interval,
                end_date
            )

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Convert equity curve to list if it's a pandas Series
        if 'equity_curve' in results:
            equity_curve = results['equity_curve']
            if hasattr(equity_curve, 'tolist'):
                results['equity_curve'] = equity_curve.tolist()

        # Convert trades dates to strings
        if 'trades' in results:
            for trade in results['trades']:
                if 'entry_date' in trade and hasattr(trade['entry_date'], 'strftime'):
                    trade['entry_date'] = trade['entry_date'].strftime('%Y-%m-%d')
                if 'exit_date' in trade and hasattr(trade['exit_date'], 'strftime'):
                    trade['exit_date'] = trade['exit_date'].strftime('%Y-%m-%d')

        return BacktestResponse(
            success=True,
            ticker=request.ticker,
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            results=results,
            execution_time_ms=execution_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/config")
async def get_config():
    """Get current API configuration"""
    return {
        "api": config.get_api_config(),
        "performance": config.get_performance_config(),
        "available_strategies": list(AVAILABLE_STRATEGIES.keys())
    }


if __name__ == "__main__":
    import uvicorn

    host = api_config.get('host', '0.0.0.0')
    port = api_config.get('port', 8000)

    print(f"Starting StrategyBuilder API on {host}:{port}")
    print(f"Documentation available at http://{host}:{port}/docs")

    uvicorn.run(app, host=host, port=port)
