import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DATA_DIR = BASE_DIR / "demo-data"

class Settings:
    PROJECT_NAME: str = "Listview - Indian Stocks & IPO Intelligence"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'market.db'}")
    
    # Free Data Provider Config
    INDIAN_STOCK_API_BASE: str = os.getenv("INDIAN_STOCK_API_BASE", "https://indian-stock-market-api.fly.dev")
    GMP_GITHUB_RAW_URL: str = os.getenv("GMP_GITHUB_RAW_URL", "https://raw.githubusercontent.com/Spectrumz00/india-ipo-gmp-data/main/data.json")
    
    # Cache settings
    CACHE_EXPIRY_SECONDS: int = 300  # 5 minutes
    
    # Financial Disclaimer
    FINANCIAL_DISCLAIMER: str = (
        "This platform is for educational and informational purposes only. "
        "Market data may be delayed, incomplete, inaccurate, or unavailable. "
        "AI predictions are statistical estimates and are not guaranteed. "
        "IPO GMP is unofficial and unregulated. "
        "Nothing on this platform constitutes financial, investment, or trading advice."
    )
    
    # Legal note
    ZERO_COST_NOTE: str = (
        "Core application is self-hosted and uses open-source/free data sources where available. "
        "External data providers may change availability or terms. Graceful fallback to local cache & demo data."
    )

settings = Settings()
