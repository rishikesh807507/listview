"""
Cache Management and Database Persistence Layer for Market Data.
Stores verified quotes and indices into SQLite/PostgreSQL.
Retrieves last-verified snapshots when live providers are unreachable.
Strictly returns 'Data unavailable' if no verified cache exists (NO FAKE DATA).
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models import MarketQuote, IndexQuote, Stock
from backend.data.market_session import evaluate_freshness, IST

logger = logging.getLogger("CacheManager")

class CacheManager:
    def __init__(self):
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

    def save_index_quote(self, db: Session, quote: Dict[str, Any]):
        """Persists validated index quote to DB and in-memory cache."""
        index_name = quote["index_name"]
        self._memory_cache[f"INDEX:{index_name}"] = quote

        try:
            record = IndexQuote(
                index_name=index_name,
                value=quote["price"],
                previous_close=quote["previous_close"],
                change=quote["change"],
                change_percent=quote["change_percent"],
                timestamp=quote["timestamp"],
                source=quote["source"],
                status=quote.get("status", "Verified"),
                created_at=datetime.utcnow()
            )
            db.add(record)
            db.commit()
        except Exception as e:
            logger.warning(f"Error persisting index {index_name} to DB: {e}")
            db.rollback()

    def get_last_verified_index(self, db: Session, index_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves last verified index record from in-memory cache or DB with original timestamps and provenance."""
        mem_key = f"INDEX:{index_name}"
        if mem_key in self._memory_cache:
            item = self._memory_cache[mem_key]
            if item.get("value") or item.get("price"):
                freshness = evaluate_freshness(item["timestamp"])
                fallback_status = "Stale Cached" if freshness["freshness"] == "Stale" else ("Market Closed" if freshness["freshness"] == "Market Closed" else "Cached")
                return {
                    **item,
                    "status": fallback_status,
                    "freshness": freshness["freshness"],
                    "last_verified": freshness["formatted_time"],
                    "warning": freshness["warning"] or "Showing last verified cached data"
                }

        record = db.query(IndexQuote).filter(
            IndexQuote.index_name == index_name
        ).order_by(IndexQuote.timestamp.desc()).first()

        if record and record.value and record.value > 0:
            freshness = evaluate_freshness(record.timestamp)
            fallback_status = "Stale Cached" if freshness["freshness"] == "Stale" else ("Market Closed" if freshness["freshness"] == "Market Closed" else "Cached")
            return {
                "index_name": record.index_name,
                "price": record.value,
                "value": record.value,
                "previous_close": record.previous_close,
                "change": record.change,
                "change_percent": record.change_percent,
                "timestamp": record.timestamp.strftime("%d %b %Y, %I:%M %p IST") if hasattr(record.timestamp, "strftime") else str(record.timestamp),
                "source": f"{record.source} (Persisted DB Cache)",
                "status": fallback_status,
                "freshness": freshness["freshness"],
                "last_verified": freshness["formatted_time"],
                "warning": freshness["warning"] or "Showing last verified cached data"
            }

        return None

    def save_market_quote(self, db: Session, quote: Dict[str, Any]):
        """Persists validated equity quote to DB and in-memory cache, and updates Stock row."""
        symbol = quote["symbol"]
        self._memory_cache[f"EQUITY:{symbol}"] = quote

        try:
            record = MarketQuote(
                symbol=symbol,
                instrument_type=quote.get("instrument_type", "EQUITY"),
                exchange=quote.get("exchange", "NSE"),
                price=quote["price"],
                previous_close=quote["previous_close"],
                change=quote["change"],
                change_percent=quote["change_percent"],
                volume=quote.get("volume", 0.0),
                timestamp=quote["timestamp"],
                source=quote["source"],
                status=quote.get("status", "Verified"),
                created_at=datetime.utcnow()
            )
            db.add(record)

            # Keep active Stock table in sync so lists and search show verified price immediately
            stk = db.query(Stock).filter(Stock.symbol == symbol).first()
            if stk:
                if quote.get("price") is not None and quote["price"] > 0:
                    stk.current_price = quote["price"]
                    stk.change = quote.get("change", stk.change)
                    stk.change_percent = quote.get("change_percent", stk.change_percent)
                if quote.get("volume") is not None and quote["volume"] > 0:
                    stk.volume = quote["volume"]
                stk.updated_at = datetime.utcnow()

            db.commit()
        except Exception as e:
            logger.warning(f"Error persisting quote {symbol} to DB: {e}")
            db.rollback()

    def get_last_verified_quote(self, db: Session, symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieves last verified equity record from in-memory cache, DB MarketQuote, or DB Stock."""
        clean_sym = symbol.strip().upper()
        mem_key = f"EQUITY:{clean_sym}"
        if mem_key in self._memory_cache:
            item = self._memory_cache[mem_key]
            if item.get("current_price") or item.get("price"):
                freshness = evaluate_freshness(item["timestamp"])
                return {
                    **item,
                    "status": item.get("status", "Cached"),
                    "freshness": freshness["freshness"],
                    "last_verified": freshness["formatted_time"],
                    "warning": freshness["warning"] or "Showing last verified cached data"
                }

        record = db.query(MarketQuote).filter(
            MarketQuote.symbol == clean_sym
        ).order_by(MarketQuote.timestamp.desc()).first()

        if record and record.price and record.price > 0:
            freshness = evaluate_freshness(record.timestamp)
            return {
                "symbol": record.symbol,
                "exchange": record.exchange,
                "instrument_type": record.instrument_type,
                "price": record.price,
                "current_price": record.price,
                "previous_close": record.previous_close,
                "change": record.change,
                "change_percent": record.change_percent,
                "volume": record.volume,
                "timestamp": record.timestamp,
                "source": f"{record.source} (Local DB Cache)",
                "status": record.status or "Cached",
                "freshness": freshness["freshness"],
                "last_verified": freshness["formatted_time"],
                "warning": freshness["warning"] or "Showing last verified cached data"
            }

        # Fallback to Stock table in the database
        stk = db.query(Stock).filter(Stock.symbol == clean_sym).first()
        if stk and stk.current_price and stk.current_price > 0:
            ts = stk.updated_at or datetime.utcnow()
            ts_str = ts.strftime("%d %b %Y, %I:%M %p IST")
            freshness = evaluate_freshness(ts)
            prev_close = round(stk.current_price - (stk.change or 0.0), 2)
            return {
                "symbol": stk.symbol,
                "exchange": stk.exchange or "NSE",
                "instrument_type": "EQUITY",
                "price": stk.current_price,
                "current_price": stk.current_price,
                "previous_close": prev_close,
                "change": stk.change or 0.0,
                "change_percent": stk.change_percent or 0.0,
                "volume": stk.volume or 0.0,
                "timestamp": ts,
                "source": "NSE Securities Master (DB Cache)",
                "status": "Cached",
                "freshness": freshness["freshness"],
                "last_verified": ts_str,
                "warning": "Showing last verified session data"
            }

        return None

cache_manager = CacheManager()

