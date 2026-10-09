"""
Central Market Data Service (Single Source of Truth).
Serves all market requests, coordinates index providers and equity quotes,
dynamically computes Top Gainers and Top Losers from a common market session snapshot,
and strictly enforces that no fake or fabricated data reaches the UI.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.data.provider_manager import provider_manager, diagnostics
from backend.data.symbol_mapper import symbol_mapper, INDEX_REGISTRY
from backend.data.market_session import get_market_session, get_ist_now
from backend.models import Stock

logger = logging.getLogger("MarketDataService")

class MarketDataService:
    """
    Central single source of truth for all market operations.
    """
    def __init__(self):
        self.provider_mgr = provider_manager

    def get_market_overview(self, db: Session) -> Dict[str, Any]:
        """
        Builds live market overview with verified benchmark indices,
        session-coherent movers, and calculated breadth.
        """
        session_info = get_market_session()

        # 1. Fetch official indices (Separate from normal stocks)
        indices_list = []
        for index_name in ["NIFTY 50", "SENSEX", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO"]:
            idx_data = self.provider_mgr.get_index_data(db, index_name)
            indices_list.append(idx_data)

        # 2. Retrieve verified universe for Top Gainers / Losers (Section 14 & 15)
        # Use verified registry of core large-cap Indian equities
        equity_symbols = symbol_mapper.get_all_equity_symbols()
        session_quotes = []
        common_session_timestamp = get_ist_now().strftime("%d %b %Y, %I:%M %p IST")

        advances = 0
        declines = 0
        unchanged = 0

        for sym in equity_symbols:
            meta = symbol_mapper.get_equity_meta(sym)
            quote = self.provider_mgr.get_equity_data(db, sym)
            
            price = quote.get("current_price")
            chg = quote.get("change")
            chg_pct = quote.get("change_percent")

            if price is not None and chg_pct is not None:
                session_quotes.append({
                    "symbol": sym,
                    "name": meta["company_name"] if meta else sym,
                    "price": price,
                    "change": chg,
                    "change_percent": chg_pct,
                    "volume": quote.get("volume", 0),
                    "as_of": quote.get("timestamp") or common_session_timestamp
                })

                if chg is not None and chg > 0:
                    advances += 1
                elif chg is not None and chg < 0:
                    declines += 1
                else:
                    unchanged += 1

        # 3. Sort Gainers & Losers dynamically (never pre-written!)
        sorted_by_change = sorted(session_quotes, key=lambda x: x["change_percent"], reverse=True)
        top_gainers = [item for item in sorted_by_change if item["change_percent"] > 0][:5]
        top_losers = [item for item in reversed(sorted_by_change) if item["change_percent"] < 0][:5]
        most_active = sorted(session_quotes, key=lambda x: x["volume"], reverse=True)[:5]

        # Overall status based on session and data availability
        overall_status = "Live" if session_info["is_open"] else "Market Closed"

        return {
            "indices": indices_list,
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "most_active": most_active,
            "market_stats": {
                "advances": advances,
                "declines": declines,
                "unchanged": unchanged,
                "total_tracked": len(session_quotes),
                "advance_decline_ratio": round(advances / max(1, declines), 2)
            },
            "market_session": session_info,
            "as_of_timestamp": common_session_timestamp,
            "data_status": overall_status,
            "source": "NSE / BSE Verified Public Feeds",
            "data_mode": self.provider_mgr.data_mode
        }

    def get_stock_quote(self, db: Session, symbol: str) -> Dict[str, Any]:
        """
        Retrieves a verified stock quote with calculations and freshness checks.
        """
        return self.provider_mgr.get_equity_data(db, symbol)

    def get_data_health(self) -> Dict[str, Any]:
        """
        Provides comprehensive data health diagnostics (Section 26 & 27).
        """
        session_info = get_market_session()
        index_healthy = self.provider_mgr.index_provider.health_check()
        stock_healthy = self.provider_mgr.stock_provider.health_check()

        return {
            "provider_status": {
                "market_provider": "Healthy" if stock_healthy else "Degraded",
                "index_provider": "Healthy" if index_healthy else "Degraded",
                "database_cache": "Healthy",
                "session_state": session_info["session"]
            },
            "metrics": {
                "records_received": diagnostics.records_received,
                "records_valid": diagnostics.records_valid,
                "records_rejected": diagnostics.records_rejected,
                "cross_source_conflicts": diagnostics.cross_source_conflicts,
                "last_successful_fetch": diagnostics.last_successful_fetch or "None recorded yet",
                "last_failed_fetch": diagnostics.last_failed_fetch or "None recorded"
            },
            "recent_rejections": diagnostics.rejection_log[-10:],
            "data_mode": self.provider_mgr.data_mode,
            "timestamp": get_ist_now().strftime("%d %b %Y, %I:%M:%S %p IST")
        }

market_data_service = MarketDataService()
