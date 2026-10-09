"""
Automated Synchronization Engine for Listview Platform.
Handles background scheduled refresh of:
1. Official NSE/BSE securities universe (daily)
2. IPO announcements, timelines, subscriptions, and verified listing prices
3. Unofficial GMP updates with timestamps and source labeling
4. Historical OHLCV synchronization
Never fabricates data.
"""
import asyncio
import logging
from datetime import datetime
from backend.database import SessionLocal
from backend.data.securities_master import refresh_securities_master
from backend.data_providers.ipo.ipo_provider_manager import ipo_provider_manager

logger = logging.getLogger("ListviewSyncEngine")

_scheduler_running = False
_last_sync_info = {
    "last_stock_sync": None,
    "last_ipo_sync": None,
    "status": "Idle",
    "details": {}
}

async def run_sync_cycle():
    """Executes a single unified sync cycle."""
    global _last_sync_info
    _last_sync_info["status"] = "Syncing"
    logger.info("[SyncEngine] Starting automated synchronization cycle...")

    db = SessionLocal()
    try:
        # 1. Sync official securities universe
        sec_report = refresh_securities_master(db)
        _last_sync_info["last_stock_sync"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.info(f"[SyncEngine] Securities master updated: {sec_report.get('inserted', 0)} new, {sec_report.get('updated', 0)} refreshed.")

        # 2. Sync official IPO disclosures, timelines, GMP, and listing data
        ipo_report = ipo_provider_manager.refresh_ipo_database(db)
        _last_sync_info["last_ipo_sync"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.info(f"[SyncEngine] IPO database updated: {ipo_report.get('records_valid', 0)} records processed.")

        _last_sync_info["status"] = "Healthy"
        _last_sync_info["details"] = {
            "securities": sec_report,
            "ipos": ipo_report
        }
    except Exception as e:
        logger.error(f"[SyncEngine] Error during sync cycle: {e}")
        _last_sync_info["status"] = "Degraded"
        _last_sync_info["last_error"] = str(e)
    finally:
        db.close()

async def background_sync_worker(interval_seconds: int = 86400):
    """Periodic worker running daily (or on configured interval)."""
    global _scheduler_running
    _scheduler_running = True
    logger.info(f"[SyncEngine] Background sync worker started (interval: {interval_seconds}s).")

    # Initial cycle after short startup delay (5 seconds)
    await asyncio.sleep(5)
    await run_sync_cycle()

    while _scheduler_running:
        try:
            await asyncio.sleep(interval_seconds)
            await run_sync_cycle()
        except asyncio.CancelledError:
            logger.info("[SyncEngine] Background sync worker received cancellation.")
            break
        except Exception as e:
            logger.error(f"[SyncEngine] Unexpected worker loop error: {e}")
            await asyncio.sleep(60)

def get_sync_status():
    return _last_sync_info
