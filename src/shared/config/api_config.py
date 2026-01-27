import os


class ApiConfig:
    API_TITLE = "StrategyBuilder API"
    API_VERSION = "2.0.0"
    API_HOST = os.getenv("API_HOST", "localhost")
    API_PORT = int(os.getenv("API_PORT", "8086"))

    # CORS Configuration - Restrict origins for security
    # Set CORS_ORIGINS environment variable for production (comma-separated list)
    # Example: CORS_ORIGINS="https://app.example.com,https://admin.example.com"
    _cors_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8086")
    # CORS_ORIGINS = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]
    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = True
    # CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    # CORS_HEADERS = ["Content-Type", "Authorization"]
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]