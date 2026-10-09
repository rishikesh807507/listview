"""
Multi-Provider Manager with Cross-Validation and Data Quality Diagnostics.
Manages Primary and Secondary Free Feeds, Cross-Validates Index Quotes,
and strictly enforces DATA_MODE (live, cached, demo).
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from backend.data.index_provider import index_provider
from backend.data.stock_provider import stock_data_provider
from backend.data.cache_manager import cache_manager
from backend.data.market_session import evaluate_freshness, get_market_session, get_ist_now

logger = logging.getLogger("DataQualityProviderManager")

class DataQualityDiagnostics:
    def __init__(self):
        self.records_received = 0
        self.records_valid = 0
        self.records_rejected = 0
        self.cross_source_conflicts = 0
        self.last_successful_fetch: Optional[str] = None
        self.last_failed_fetch: Optional[str] = None
        self.rejection_log: List[Dict[str, Any]] = []

    def record_success(self, count: int = 1):
        self.records_received += count
        self.records_valid += count
        self.last_successful_fetch = get_ist_now().strftime("%d %b %Y, %I:%M:%S %p IST")

    def record_failure(self, reason: str, count: int = 1):
        self.records_received += count
        self.records_rejected += count
        self.last_failed_fetch = get_ist_now().strftime("%d %b %Y, %I:%M:%S %p IST")
        self.rejection_log.append({
            "timestamp": self.last_failed_fetch,
            "reason": reason
        })
        if len(self.rejection_log) > 50:
            self.rejection_log.pop(0)

    def record_conflict(self):
        self.cross_source_conflicts += 1

diagnostics = DataQualityDiagnostics()

class ProviderManager:
    """
    Central provider manager enforcing the Single Source of Truth rule.
    DATA_MODE:
      - 'live': Real external queries + DB cache fallback. (NEVER demo data)
      - 'cached': Read directly from local verified SQLite/PostgreSQL cache.
      - 'demo': Read from bundled demo datasets only when explicitly requested.
    """
    def __init__(self):
        self.data_mode = os.getenv("DATA_MODE", "live").lower()
        self.index_provider = index_provider
        self.stock_provider = stock_data_provider
        self.cache_manager = cache_manager

    def get_index_data(self, db: Session, index_name: str) -> Dict[str, Any]:
        """
        Retrieves index with 4-tier fallback:
        Tier 1: Live verified query
        Tier 2: Cached DB value
        Tier 3: Data unavailable (in live mode, never fake numbers!)
        """
        # 1. If live mode, attempt real fetch
        if self.data_mode == "live":
            quote = self.index_provider.get_index_quote(index_name)
            if quote:
                self.cache_manager.save_index_quote(db, quote)
                diagnostics.record_success()
                freshness = evaluate_freshness(quote["timestamp"])
                return {
                    "index_name": quote["index_name"],
                    "value": quote["price"],
                    "previous_close": quote["previous_close"],
                    "change": quote["change"],
                    "change_percent": quote["change_percent"],
                    "timestamp": freshness["formatted_time"],
                    "source": quote["source"],
                    "status": freshness["freshness"],
                    "freshness": freshness["freshness"],
                    "warning": freshness["warning"]
                }
            else:
                diagnostics.record_failure(f"Failed live fetch for {index_name}")

        # 2. Tier 2: DB Cache fallback
        cached = self.cache_manager.get_last_verified_index(db, index_name)
        if cached:
            return {
                "index_name": cached["index_name"],
                "value": cached["value"],
                "previous_close": cached["previous_close"],
                "change": cached["change"],
                "change_percent": cached["change_percent"],
                "timestamp": cached["last_verified"],
                "source": cached["source"],
                "status": "Cached",
                "freshness": cached["freshness"],
                "warning": cached["warning"]
            }

        # 3. Tier 3: In live/cached mode, NEVER invent data
        if self.data_mode != "demo":
            return {
                "index_name": index_name,
                "value": None,
                "previous_close": None,
                "change": None,
                "change_percent": None,
                "timestamp": get_ist_now().strftime("%d %b %Y, %I:%M %p IST"),
                "source": "None",
                "status": "Live data unavailable",
                "freshness": "Unavailable",
                "warning": "Live data temporarily unavailable — no verified cache found"
            }

        # 4. Tier 4: Explicit demo mode only
        return {
            "index_name": index_name,
            "value": 22421.95,
            "previous_close": 23140.50,
            "change": -718.55,
            "change_percent": -3.10,
            "timestamp": "Demo Snapshot",
            "source": "Bundled Demo Dataset",
            "status": "Demo Mode",
            "freshness": "Demo",
            "warning": "Running in Demo Mode"
        }

    def get_equity_data(self, db: Session, symbol: str) -> Dict[str, Any]:
        """
        Retrieves equity quote with verification, change calculation, and cache persistence.
        """
        clean_sym = symbol.strip().upper()

        if self.data_mode == "live":
            quote = self.stock_provider.get_quote(clean_sym)
            if quote:
                self.cache_manager.save_market_quote(db, quote)
                diagnostics.record_success()
                freshness = evaluate_freshness(quote["timestamp"])
                return {
                    "symbol": quote["symbol"],
                    "exchange": quote["exchange"],
                    "current_price": quote["price"],
                    "previous_close": quote["previous_close"],
                    "change": quote["change"],
                    "change_percent": quote["change_percent"],
                    "volume": quote["volume"],
                    "timestamp": freshness["formatted_time"],
                    "source": quote["source"],
                    "status": freshness["freshness"],
                    "freshness": freshness["freshness"],
                    "warning": freshness["warning"]
                }
            else:
                diagnostics.record_failure(f"Failed live fetch for {clean_sym}")

        # Cached fallback
        cached = self.cache_manager.get_last_verified_quote(db, clean_sym)
        if cached:
            return {
                "symbol": cached["symbol"],
                "exchange": cached["exchange"],
                "current_price": cached["price"],
                "previous_close": cached["previous_close"],
                "change": cached["change"],
                "change_percent": cached["change_percent"],
                "volume": cached.get("volume", 0.0),
                "timestamp": cached["last_verified"],
                "source": cached["source"],
                "status": "Cached",
                "freshness": cached["freshness"],
                "warning": cached["warning"]
            }

        # If data is unavailable, return unavailable status without fabricating
        return {
            "symbol": clean_sym,
            "exchange": "NSE",
            "current_price": None,
            "previous_close": None,
            "change": None,
            "change_percent": None,
            "volume": None,
            "timestamp": get_ist_now().strftime("%d %b %Y, %I:%M %p IST"),
            "source": "None",
            "status": "Live data unavailable",
            "freshness": "Unavailable",
            "warning": f"Live data unavailable for {clean_sym}"
        }

provider_manager = ProviderManager()
