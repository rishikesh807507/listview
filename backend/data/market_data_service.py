"""
Central Market Data Service (Single Source of Truth).
Serves all market requests, coordinates index providers and equity quotes,
dynamically computes Top Gainers and Top Losers from a common market session snapshot,
and strictly enforces that no fake or fabricated data reaches the UI.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

from backend.data.provider_manager import provider_manager, diagnostics
from backend.data.symbol_mapper import symbol_mapper, INDEX_REGISTRY
from backend.data.market_session import get_market_session, get_ist_now, evaluate_freshness
from backend.models import Stock

logger = logging.getLogger("MarketDataService")

class MarketDataService:
    """
    Central single source of truth for all market operations.
    """
    def __init__(self):
        self.provider_mgr = provider_manager
        self.provider_manager = provider_manager

    def get_market_overview(self, db: Session) -> Dict[str, Any]:
        """
        Builds live market overview with verified benchmark indices,
        session-coherent movers, and calculated breadth.
        """
        session_info = get_market_session()

        # 1. Fetch live index quotes concurrently across bounded thread pool
        target_indices = ["NIFTY 50", "SENSEX", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO"]
        live_index_quotes = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_idx = {executor.submit(self.provider_mgr.index_provider.get_index_quote, name): name for name in target_indices}
            for future in future_to_idx:
                name = future_to_idx[future]
                try:
                    live_index_quotes[name] = future.result(timeout=4.0)
                except Exception as e:
                    logger.debug(f"Live index fetch timeout/error for {name}: {e}")
                    live_index_quotes[name] = None

        # Process indices sequentially on the caller's db session
        indices_list = []
        for name in target_indices:
            q = live_index_quotes.get(name)
            if q:
                self.provider_mgr.cache_manager.save_index_quote(db, q)
                diagnostics.record_success()
                freshness = evaluate_freshness(q["timestamp"])
                indices_list.append({
                    "index_name": q["index_name"],
                    "value": q["price"],
                    "price": q["price"],
                    "previous_close": q["previous_close"],
                    "change": q["change"],
                    "change_percent": q["change_percent"],
                    "timestamp": freshness["formatted_time"],
                    "source": q["source"],
                    "status": freshness["freshness"],
                    "freshness": freshness["freshness"],
                    "warning": freshness["warning"]
                })
            else:
                diagnostics.record_failure(f"Failed live fetch for {name}")
                cached = self.provider_mgr.cache_manager.get_last_verified_index(db, name)
                if cached:
                    indices_list.append({
                        "index_name": cached["index_name"],
                        "value": cached["value"],
                        "price": cached.get("price", cached["value"]),
                        "previous_close": cached["previous_close"],
                        "change": cached["change"],
                        "change_percent": cached["change_percent"],
                        "timestamp": cached["last_verified"],
                        "source": cached["source"],
                        "status": cached.get("status", "Cached"),
                        "freshness": cached.get("freshness", "Cached"),
                        "warning": cached.get("warning")
                    })
                else:
                    indices_list.append({
                        "index_name": name,
                        "value": None,
                        "price": None,
                        "previous_close": None,
                        "change": None,
                        "change_percent": None,
                        "timestamp": get_ist_now().strftime("%d %b %Y, %I:%M %p IST"),
                        "source": "None",
                        "status": "Unavailable",
                        "freshness": "Unavailable",
                        "warning": f"Live data temporarily unavailable — no verified cache found for {name}"
                    })

        # 2. Retrieve verified universe for Top Gainers / Losers
        equity_symbols = symbol_mapper.get_all_equity_symbols()
        live_equity_quotes = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_sym = {executor.submit(self.provider_mgr.stock_provider.get_quote, sym): sym for sym in equity_symbols}
            for future in future_to_sym:
                sym = future_to_sym[future]
                try:
                    live_equity_quotes[sym] = future.result(timeout=3.0)
                except Exception as e:
                    logger.debug(f"Live equity fetch timeout/error for {sym}: {e}")
                    live_equity_quotes[sym] = None

        session_quotes = []
        common_session_timestamp = get_ist_now().strftime("%d %b %Y, %I:%M %p IST")
        advances = 0
        declines = 0
        unchanged = 0

        for sym in equity_symbols:
            meta = symbol_mapper.get_equity_meta(sym)
            quote = live_equity_quotes.get(sym)
            if quote:
                self.provider_mgr.cache_manager.save_market_quote(db, quote)
                diagnostics.record_success()
                freshness = evaluate_freshness(quote["timestamp"])
                eq_data = {
                    "symbol": quote["symbol"],
                    "price": quote["price"],
                    "previous_close": quote["previous_close"],
                    "change": quote["change"],
                    "change_percent": quote["change_percent"],
                    "volume": quote.get("volume", 0),
                    "timestamp": freshness["formatted_time"]
                }
            else:
                diagnostics.record_failure(f"Failed live fetch for {sym}")
                cached = self.provider_mgr.cache_manager.get_last_verified_quote(db, sym)
                if cached:
                    eq_data = {
                        "symbol": cached["symbol"],
                        "price": cached.get("price"),
                        "previous_close": cached.get("previous_close"),
                        "change": cached.get("change"),
                        "change_percent": cached.get("change_percent"),
                        "volume": cached.get("volume", 0),
                        "timestamp": cached.get("last_verified")
                    }
                else:
                    eq_data = None

            if eq_data and eq_data.get("price") is not None and eq_data.get("change_percent") is not None:
                session_quotes.append({
                    "symbol": sym,
                    "name": meta["company_name"] if meta else sym,
                    "price": eq_data["price"],
                    "change": eq_data["change"],
                    "change_percent": eq_data["change_percent"],
                    "volume": eq_data.get("volume", 0),
                    "as_of": eq_data.get("timestamp") or common_session_timestamp
                })
                chg = eq_data.get("change")
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

        # Dynamically supplement Top Gainers from Stock table if insufficient from live feeds
        if len(top_gainers) < 5:
            existing_symbols = {g["symbol"] for g in top_gainers}
            db_gainers = db.query(Stock).filter(
                Stock.is_active == True,
                Stock.current_price.isnot(None),
                Stock.current_price > 0,
                Stock.change_percent.isnot(None),
                Stock.change_percent > 0,
                ~Stock.symbol.in_(existing_symbols)
            ).order_by(Stock.change_percent.desc()).limit(5 - len(top_gainers)).all()
            for s in db_gainers:
                ts_str = s.updated_at.strftime("%d %b %Y, %I:%M %p IST") if s.updated_at else common_session_timestamp
                top_gainers.append({
                    "symbol": s.symbol,
                    "name": s.name,
                    "price": s.current_price,
                    "change": s.change or 0.0,
                    "change_percent": s.change_percent,
                    "volume": s.volume or 0.0,
                    "as_of": ts_str
                })

        # Dynamically supplement Top Losers from Stock table if insufficient from live feeds
        if len(top_losers) < 5:
            existing_symbols = {l["symbol"] for l in top_losers}
            db_losers = db.query(Stock).filter(
                Stock.is_active == True,
                Stock.current_price.isnot(None),
                Stock.current_price > 0,
                Stock.change_percent.isnot(None),
                Stock.change_percent < 0,
                ~Stock.symbol.in_(existing_symbols)
            ).order_by(Stock.change_percent.asc()).limit(5 - len(top_losers)).all()
            for s in db_losers:
                ts_str = s.updated_at.strftime("%d %b %Y, %I:%M %p IST") if s.updated_at else common_session_timestamp
                top_losers.append({
                    "symbol": s.symbol,
                    "name": s.name,
                    "price": s.current_price,
                    "change": s.change or 0.0,
                    "change_percent": s.change_percent,
                    "volume": s.volume or 0.0,
                    "as_of": ts_str
                })

        # Dynamically supplement Most Active from Stock table if insufficient
        if len(most_active) < 5:
            existing_symbols = {a["symbol"] for a in most_active}
            db_active = db.query(Stock).filter(
                Stock.is_active == True,
                Stock.current_price.isnot(None),
                Stock.current_price > 0,
                ~Stock.symbol.in_(existing_symbols)
            ).order_by(Stock.volume.desc().nullslast()).limit(5 - len(most_active)).all()
            for s in db_active:
                ts_str = s.updated_at.strftime("%d %b %Y, %I:%M %p IST") if s.updated_at else common_session_timestamp
                most_active.append({
                    "symbol": s.symbol,
                    "name": s.name,
                    "price": s.current_price,
                    "change": s.change or 0.0,
                    "change_percent": s.change_percent or 0.0,
                    "volume": s.volume or 0.0,
                    "as_of": ts_str
                })

        # Calculate comprehensive market stats from database if live quotes are unavailable
        if advances == 0 and declines == 0:
            advances = db.query(Stock).filter(Stock.is_active == True, Stock.current_price > 0, Stock.change_percent > 0).count()
            declines = db.query(Stock).filter(Stock.is_active == True, Stock.current_price > 0, Stock.change_percent < 0).count()
            unchanged = db.query(Stock).filter(Stock.is_active == True, Stock.current_price > 0, Stock.change_percent == 0).count()

        highs_52w = db.query(Stock).filter(
            Stock.is_active == True,
            Stock.current_price.isnot(None),
            Stock.high_52w.isnot(None),
            Stock.high_52w > 0,
            Stock.current_price >= Stock.high_52w * 0.99
        ).count()

        lows_52w = db.query(Stock).filter(
            Stock.is_active == True,
            Stock.current_price.isnot(None),
            Stock.low_52w.isnot(None),
            Stock.low_52w > 0,
            Stock.current_price <= Stock.low_52w * 1.01
        ).count()

        total_tracked = advances + declines + unchanged if (advances or declines) else len(session_quotes)
        ad_ratio = round(advances / max(1, declines), 2) if declines > 0 else (round(float(advances), 2) if advances > 0 else 1.0)

        # Overall status based on session and data availability
        overall_status = "Live" if session_info.get("is_open") else "Market Closed"

        return {
            "indices": indices_list,
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "most_active": most_active,
            "market_stats": {
                "advances": advances,
                "declines": declines,
                "unchanged": unchanged,
                "total_tracked": total_tracked,
                "advance_decline_ratio": ad_ratio,
                "highs_52w": highs_52w,
                "lows_52w": lows_52w
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
