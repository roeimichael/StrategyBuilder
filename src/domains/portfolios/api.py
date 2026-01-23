from fastapi import APIRouter, HTTPException
from src.domains.portfolios.models import (
    CreatePortfolioRequest,
    UpdatePortfolioRequest,
    PortfolioResponse,
    PortfolioListResponse,
    PortfolioBacktestRequest,
    PortfolioBacktestResponse,
    PortfolioBacktestResult
)
from src.domains.portfolios.repository import PortfolioRepository
from src.domains.presets.repository import PresetRepository
from src.domains.backtests.service import BacktestService, BacktestRequest
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/portfolios", tags=["portfolios"])
portfolio_repository = PortfolioRepository()
preset_repository = PresetRepository()
backtest_service = BacktestService()


@router.post("", response_model=PortfolioResponse, status_code=201)
@log_errors
def create_portfolio(request: CreatePortfolioRequest) -> PortfolioResponse:
    """
    Create a new portfolio with stock holdings.

    - **name**: Unique name for the portfolio
    - **description**: Optional description
    - **holdings**: List of holdings with ticker, shares, and optional weight
    """
    try:
        portfolio_id = portfolio_repository.create_portfolio({
            'name': request.name,
            'description': request.description,
            'holdings': request.holdings
        })

        portfolio = portfolio_repository.get_portfolio_by_id(portfolio_id)
        return PortfolioResponse(**portfolio)
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail=f"Portfolio with name '{request.name}' already exists")
        raise HTTPException(status_code=500, detail=f"Failed to create portfolio: {str(e)}")


@router.get("", response_model=PortfolioListResponse)
@log_errors
def list_portfolios() -> PortfolioListResponse:
    """List all portfolios."""
    try:
        portfolios = portfolio_repository.list_portfolios()
        portfolio_responses = [PortfolioResponse(**p) for p in portfolios]

        return PortfolioListResponse(
            success=True,
            count=len(portfolio_responses),
            portfolios=portfolio_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolios: {str(e)}")


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
@log_errors
def get_portfolio(portfolio_id: int) -> PortfolioResponse:
    """
    Get a specific portfolio by ID.

    - **portfolio_id**: The ID of the portfolio
    """
    try:
        portfolio = portfolio_repository.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail=f"Portfolio with ID {portfolio_id} not found")

        return PortfolioResponse(**portfolio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio: {str(e)}")


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
@log_errors
def update_portfolio(portfolio_id: int, request: UpdatePortfolioRequest) -> PortfolioResponse:
    """
    Update a portfolio.

    - **portfolio_id**: The ID of the portfolio to update
    - **request**: Fields to update (all optional)
    """
    try:
        existing = portfolio_repository.get_portfolio_by_id(portfolio_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Portfolio with ID {portfolio_id} not found")

        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.holdings is not None:
            updates['holdings'] = request.holdings

        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")

        success = portfolio_repository.update_portfolio(portfolio_id, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update portfolio")

        portfolio = portfolio_repository.get_portfolio_by_id(portfolio_id)
        return PortfolioResponse(**portfolio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update portfolio: {str(e)}")


@router.delete("/{portfolio_id}", status_code=204)
@log_errors
def delete_portfolio(portfolio_id: int):
    """
    Delete a portfolio.

    - **portfolio_id**: The ID of the portfolio to delete
    """
    try:
        success = portfolio_repository.delete_portfolio(portfolio_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Portfolio with ID {portfolio_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete portfolio: {str(e)}")


@router.post("/{portfolio_id}/backtest", response_model=PortfolioBacktestResponse)
@log_errors
def backtest_portfolio(portfolio_id: int, request: PortfolioBacktestRequest) -> PortfolioBacktestResponse:
    """
    Run a backtest on all stocks in a portfolio using a preset strategy.

    - **portfolio_id**: The ID of the portfolio
    - **preset_id**: The preset strategy configuration to use
    - **start_date**: Backtest start date (YYYY-MM-DD)
    - **end_date**: Backtest end date (YYYY-MM-DD)
    - **use_weights**: Use portfolio weights for aggregated results
    """
    try:
        # Get portfolio
        portfolio = portfolio_repository.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail=f"Portfolio with ID {portfolio_id} not found")

        # Get preset
        preset = preset_repository.get_preset_by_id(request.preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset with ID {request.preset_id} not found")

        # Run backtest for each holding
        results = []
        for holding in portfolio['holdings']:
            try:
                backtest_req = BacktestRequest(
                    ticker=holding['ticker'],
                    strategy=preset['strategy'],
                    start_date=request.start_date,
                    end_date=request.end_date,
                    interval=preset['interval'],
                    cash=preset['cash'],
                    parameters=preset['parameters']
                )

                backtest_response = backtest_service.run_backtest(backtest_req, save_run=False)

                results.append(PortfolioBacktestResult(
                    ticker=holding['ticker'],
                    weight=holding.get('weight'),
                    pnl=backtest_response.pnl,
                    return_pct=backtest_response.return_pct,
                    sharpe_ratio=backtest_response.sharpe_ratio
                ))
            except Exception as e:
                # Continue with other tickers if one fails
                print(f"Failed to backtest {holding['ticker']}: {str(e)}")
                continue

        # Calculate weighted results if requested
        weighted_pnl = None
        weighted_return_pct = None
        if request.use_weights and all(r.weight is not None for r in results):
            weighted_pnl = sum(r.pnl * r.weight for r in results)
            weighted_return_pct = sum(r.return_pct * r.weight for r in results)

        return PortfolioBacktestResponse(
            success=True,
            portfolio_name=portfolio['name'],
            strategy=preset['strategy'],
            weighted_pnl=weighted_pnl,
            weighted_return_pct=weighted_return_pct,
            results=results
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to backtest portfolio: {str(e)}")
