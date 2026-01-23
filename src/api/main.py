from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.shared.config import Config

# Import domain routers
from src.domains.system.api import router as system_router
from src.domains.strategies.api import router as strategies_router
from src.domains.backtests.api import router as backtests_router
from src.domains.optimizations.api import router as optimizations_router
from src.domains.market_scans.api import router as market_scans_router
from src.domains.run_history.api import router as run_history_router
from src.domains.presets.api import router as presets_router
from src.domains.watchlists.api import router as watchlists_router
from src.domains.portfolios.api import router as portfolios_router
from src.domains.live_monitor.api import router as live_monitor_router

app = FastAPI(
    title=Config.API_TITLE,
    description="Algorithmic Trading Backtesting Platform",
    version=Config.API_VERSION
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=Config.CORS_CREDENTIALS,
    allow_methods=Config.CORS_METHODS,
    allow_headers=Config.CORS_HEADERS
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include domain routers
app.include_router(system_router)
app.include_router(strategies_router)
app.include_router(backtests_router)
app.include_router(optimizations_router)
app.include_router(market_scans_router)
app.include_router(run_history_router)
app.include_router(presets_router)
app.include_router(watchlists_router)
app.include_router(portfolios_router)
app.include_router(live_monitor_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=True)
