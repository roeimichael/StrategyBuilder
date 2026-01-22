from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.shared.config import Config

# Import domain routers
from src.domains.system.api import router as system_router
from src.domains.strategies.api import router as strategies_router
from src.domains.backtests.api import router as backtests_router
from src.domains.market_data.api import router as market_data_router
from src.domains.saved_runs.api import router as saved_runs_router

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
app.include_router(market_data_router)
app.include_router(saved_runs_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT, reload=True)
