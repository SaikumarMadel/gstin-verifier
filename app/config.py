import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5001"))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    API_KEY = os.getenv("API_KEY", "").strip()
    SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "300"))
    SESSION_CLEANUP_INTERVAL_SECONDS = int(os.getenv("SESSION_CLEANUP_INTERVAL_SECONDS", "60"))
    GST_PORTAL_TIMEOUT_SECONDS = int(os.getenv("GST_PORTAL_TIMEOUT_SECONDS", "12"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
