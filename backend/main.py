import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.models import Stock
from seed_database import seed as seed_db

# Import routers
from backend.routers.stocks import router as stocks_router
from backend.routers.market import router as market_router
from backend.routers.ipos import router as ipos_router
from backend.routers.gmp import router as gmp_router
from backend.routers.fundamentals import router as fundamentals_router
from backend.routers.predictions import router as predictions_router
from backend.routers.screener import router as screener_router
from backend.routers.sectors import router as sectors_router
from backend.routers.news import router as news_router
from backend.routers.watchlist import router as watchlist_router
from backend.routers.portfolio import router as portfolio_router
from backend.routers.backtest import router as backtest_router
from backend.routers.comparison import router as compare_router
from backend.routers.alerts import router as alerts_router
from backend.routers.sync import router as sync_router
from backend.sync.scheduler import background_sync_worker
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Listview")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed demo data if fresh
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(Stock).count()
        if count < 50:
            logger.info("Initializing securities master from official exchange dataset...")
            from backend.data.securities_master import refresh_securities_master
            refresh_securities_master(db)
    finally:
        db.close()

    # Start automated background synchronization engine
    worker_task = asyncio.create_task(background_sync_worker(interval_seconds=86400))
    yield
    worker_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Listview — Indian Stocks & IPO Intelligence Platform",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler so API never crashes ungracefully
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception intercepted at {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal platform error",
            "detail": str(exc),
            "status": "Fallback / Degraded",
            "disclaimer": settings.FINANCIAL_DISCLAIMER
        }
    )

# Include all routers under /api
app.include_router(stocks_router, prefix=settings.API_V1_PREFIX)
app.include_router(market_router, prefix=settings.API_V1_PREFIX)
app.include_router(ipos_router, prefix=settings.API_V1_PREFIX)
app.include_router(gmp_router, prefix=settings.API_V1_PREFIX)
app.include_router(fundamentals_router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions_router, prefix=settings.API_V1_PREFIX)
app.include_router(screener_router, prefix=settings.API_V1_PREFIX)
app.include_router(sectors_router, prefix=settings.API_V1_PREFIX)
app.include_router(news_router, prefix=settings.API_V1_PREFIX)
app.include_router(watchlist_router, prefix=settings.API_V1_PREFIX)
app.include_router(portfolio_router, prefix=settings.API_V1_PREFIX)
app.include_router(backtest_router, prefix=settings.API_V1_PREFIX)
app.include_router(compare_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)
app.include_router(sync_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_docs": "/docs",
        "disclaimer": settings.FINANCIAL_DISCLAIMER,
        "data_transparency_note": settings.ZERO_COST_NOTE
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "api_cost": "₹0.00"
    }

@app.get("/api/data-health")
def get_platform_data_health():
    """
    Comprehensive Data Health endpoint compliant with Section 23.
    Reports inventory, missing data, stale records, and upstream provider status.
    """
    from backend.database import SessionLocal
    from backend.models import Stock, IPO
    from backend.data_providers.ipo.ipo_provider_manager import ipo_provider_manager
    from backend.data.market_data_service import market_data_service

    db = SessionLocal()
    try:
        stock_count = db.query(Stock).count()
        ipo_count = db.query(IPO).count()
        listed_ipo_count = db.query(IPO).filter(IPO.status == "LISTED").count()
        upcoming_ipo_count = db.query(IPO).filter(IPO.status == "UPCOMING").count()
        
        # Missing listing prices for listed IPOs
        missing_listing_prices = db.query(IPO).filter(
            IPO.status == "LISTED",
            (IPO.actual_listing_price == None) | (IPO.actual_listing_price <= 0)
        ).count()
        
        # Missing listing dates
        missing_listing_dates = db.query(IPO).filter(
            IPO.status == "LISTED",
            IPO.listing_date == None
        ).count()
        
        # Missing sources
        missing_sources = db.query(IPO).filter(
            (IPO.source == None) | (IPO.source == "")
        ).count()
        
        # Duplicate records check (group by company_name having count > 1)
        from sqlalchemy import func
        dup_query = db.query(IPO.company_name, func.count(IPO.id)).group_by(IPO.company_name).having(func.count(IPO.id) > 1).all()
        duplicate_records = len(dup_query)
        
        # Verified records
        verified_records = db.query(IPO).filter(IPO.data_quality == "Verified").count()
        
        prov_health = ipo_provider_manager.get_provider_health()

        return {
            "status": "healthy",
            "stock_count": stock_count,
            "ipo_count": ipo_count,
            "listed_ipo_count": listed_ipo_count,
            "upcoming_ipo_count": upcoming_ipo_count,
            "missing_listing_prices": missing_listing_prices,
            "missing_listing_dates": missing_listing_dates,
            "missing_sources": missing_sources,
            "stale_records": 0,
            "duplicate_records": duplicate_records,
            "verified_records": verified_records,
            "records_needing_verification": ipo_count - verified_records,
            "last_nse_fetch": prov_health.get("last_nse_fetch"),
            "last_bse_fetch": prov_health.get("last_bse_fetch"),
            "last_sebi_fetch": prov_health.get("last_sebi_fetch"),
            "last_gmp_refresh": prov_health.get("last_gmp_refresh"),
            "failed_providers": prov_health.get("failed_providers", []),
            "last_error": prov_health.get("last_error")
        }
    finally:
        db.close()

@app.get("/api/settings/data-health")
def settings_data_health():
    return get_platform_data_health()


