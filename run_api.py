import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    from api.main import app
    from config import Config

    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )
