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
from typing import Dict, Any

from backend.database import SessionLocal
from backend.data.securities_master import refresh_securities_master
from backend.data_providers.ipo.ipo_provider_manager import ipo_provider_manager
from backend.data.symbol_mapper import INDEX_REGISTRY
from backend.data.index_provider import index_provider
from backend.data.cache_manager import cache_manager

logger = logging.getLogger("ListviewSyncEngine")

_scheduler_running = False
_last_sync_info = {
    "last_stock_sync": None,
    "last_ipo_sync": None,
    "last_index_sync": None,
    "status": "Idle",
    "details": {}
}

def sync_indices(db) -> Dict[str, Any]:
    """
    Independently refreshes benchmark indices and persists verified quotes to the database.
    Does not block securities or IPO synchronization on failure.
    """
    logger.info("[SyncEngine] Starting benchmark indices refresh...")
    results = {"success": 0, "failed": 0, "indices": {}}
    try:
        for canonical_name in INDEX_REGISTRY.keys():
            try:
                quote = index_provider.get_index_quote(canonical_name)
                if quote and quote.get("price", 0) > 0:
                    cache_manager.save_index_quote(db, quote)
                    results["success"] += 1
                    results["indices"][canonical_name] = {
                        "status": "Updated",
                        "price": quote["price"],
                        "source": quote.get("source"),
                        "timestamp": str(quote.get("timestamp"))
                    }
                else:
                    results["failed"] += 1
                    results["indices"][canonical_name] = {
                        "status": "Unavailable",
                        "reason": "Provider returned no valid quote"
                    }
            except Exception as e:
                results["failed"] += 1
                results["indices"][canonical_name] = {
                    "status": "Error",
                    "error": str(e)
                }
                logger.warning(f"[SyncEngine] Failed to refresh index {canonical_name}: {e}")
    except Exception as e:
        logger.error(f"[SyncEngine] Fatal error in sync_indices: {e}")
        results["error"] = str(e)
    return results

async def run_sync_cycle():
    """Executes a single unified sync cycle with strict fault isolation across jobs."""
    global _last_sync_info
    _last_sync_info["status"] = "Syncing"
    logger.info("[SyncEngine] Starting automated synchronization cycle...")

    db = SessionLocal()
    cycle_details = {}
    try:
        # 1. Sync official securities universe (independent error boundary)
        try:
            sec_report = refresh_securities_master(db)
            _last_sync_info["last_stock_sync"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            cycle_details["securities"] = sec_report
            logger.info(f"[SyncEngine] Securities master updated: {sec_report.get('inserted', 0)} new, {sec_report.get('updated', 0)} refreshed.")
        except Exception as e:
            logger.error(f"[SyncEngine] Securities master sync failed: {e}")
            cycle_details["securities_error"] = str(e)

        # 2. Sync official IPO disclosures, timelines, GMP, and listing data (independent error boundary)
        try:
            ipo_report = ipo_provider_manager.refresh_ipo_database(db)
            _last_sync_info["last_ipo_sync"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            cycle_details["ipos"] = ipo_report
            logger.info(f"[SyncEngine] IPO database updated: {ipo_report.get('records_valid', 0)} records processed.")
        except Exception as e:
            logger.error(f"[SyncEngine] IPO database sync failed: {e}")
            cycle_details["ipo_error"] = str(e)

        # 3. Sync benchmark market indices (independent error boundary)
        try:
            idx_report = sync_indices(db)
            _last_sync_info["last_index_sync"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            cycle_details["indices"] = idx_report
            logger.info(f"[SyncEngine] Benchmark indices updated: {idx_report.get('success', 0)} succeeded, {idx_report.get('failed', 0)} failed.")
        except Exception as e:
            logger.error(f"[SyncEngine] Index sync failed: {e}")
            cycle_details["index_error"] = str(e)

        has_error = any("error" in k for k in cycle_details)
        _last_sync_info["status"] = "Degraded" if has_error else "Healthy"
        _last_sync_info["details"] = cycle_details
    except Exception as e:
        logger.error(f"[SyncEngine] Unexpected error during sync cycle: {e}")
        _last_sync_info["status"] = "Degraded"
        _last_sync_info["last_error"] = str(e)
    finally:
        db.close()

async def background_index_worker(interval_seconds: int = 900):
    """Periodically refreshes benchmark indices every 15 minutes to keep cache warm."""
    global _scheduler_running
    logger.info(f"[SyncEngine] Periodic index worker active (interval: {interval_seconds}s).")
    await asyncio.sleep(10)
    while _scheduler_running:
        db = SessionLocal()
        try:
            sync_indices(db)
            _last_sync_info["last_index_sync"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception as e:
            logger.warning(f"[SyncEngine] Periodic index worker iteration error: {e}")
        finally:
            db.close()
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            break

async def background_sync_worker(interval_seconds: int = 86400):
    """Periodic worker running daily (or on configured interval) with dedicated index refresher."""
    global _scheduler_running
    _scheduler_running = True
    logger.info(f"[SyncEngine] Background sync worker started (daily interval: {interval_seconds}s).")

    # Start independent periodic index refresher
    index_task = asyncio.create_task(background_index_worker(interval_seconds=900))

    # Initial full cycle after short startup delay (5 seconds)
    await asyncio.sleep(5)
    await run_sync_cycle()

    while _scheduler_running:
        try:
            await asyncio.sleep(interval_seconds)
            await run_sync_cycle()
        except asyncio.CancelledError:
            logger.info("[SyncEngine] Background sync worker received cancellation.")
            index_task.cancel()
            break
        except Exception as e:
            logger.error(f"[SyncEngine] Unexpected worker loop error: {e}")
            await asyncio.sleep(60)

def get_sync_status():
    return _last_sync_info
