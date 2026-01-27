import uvicorn
from src.shared.config import Config

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )
