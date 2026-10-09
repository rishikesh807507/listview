"""
Unified Historical Candles Service for Listview Platform.
Acts as a single, shared provider for:
- Quantitative Backtesting
- AI Stock Predictor (Walk-Forward Machine Learning)
- Stock Detail Interactive Charts
- Watchlist Mini Sparklines

Fetches verified chronological OHLCV data from market feed, validates and deduplicates,
and caches daily bars into database StockPrice.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models import Stock, StockPrice
from backend.data.stock_provider import stock_data_provider
from backend.data.provider_manager import provider_manager

logger = logging.getLogger("HistoricalCandlesService")

TIMEFRAME_CONFIG = {
    "1D": {"period": "1d", "interval": "5m", "limit": 100},
    "1W": {"period": "5d", "interval": "15m", "limit": 150},
    "1M": {"period": "1mo", "interval": "1d", "limit": 25},
    "3M": {"period": "3mo", "interval": "1d", "limit": 70},
    "6M": {"period": "6mo", "interval": "1d", "limit": 135},
    "1Y": {"period": "1y", "interval": "1d", "limit": 260},
    "3Y": {"period": "5y", "interval": "1d", "limit": 750},
    "5Y": {"period": "5y", "interval": "1d", "limit": 1300},
    "MAX": {"period": "max", "interval": "1d", "limit": 5000},
}


def sanitize_and_sort_candles(raw_candles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validates timestamps, OHLC values, deduplicates, and sorts chronologically.
    Never mixes symbols, never allows NaN/null or inverted candles.
    """
    if not raw_candles:
        return []

    seen_times = set()
    sanitized = []

    for c in raw_candles:
        t = c.get("time") or c.get("timestamp")
        o = c.get("open")
        h = c.get("high")
        l = c.get("low")
        cl = c.get("close")
        v = c.get("volume", 0.0)

        if t is None or o is None or h is None or l is None or cl is None:
            continue

        try:
            o_f = float(o)
            h_f = float(h)
            l_f = float(l)
            cl_f = float(cl)
            v_f = float(v) if v is not None else 0.0
        except (ValueError, TypeError):
            continue

        # Strictly positive price check
        if o_f <= 0.0 or h_f <= 0.0 or l_f <= 0.0 or cl_f <= 0.0:
            continue

        # Mathematical sanity: high must be >= open, close; low must be <= open, close
        h_f = max(h_f, o_f, cl_f)
        l_f = min(l_f, o_f, cl_f)

        if t in seen_times:
            continue
        seen_times.add(t)

        sanitized.append({
            "timestamp": str(c.get("timestamp", t)),
            "time": t,
            "open": round(o_f, 2),
            "high": round(h_f, 2),
            "low": round(l_f, 2),
            "close": round(cl_f, 2),
            "volume": round(v_f, 2)
        })

    # Sort strictly ascending by time
    sanitized.sort(key=lambda x: str(x["time"]))
    return sanitized


def get_historical_candles_for_symbol(
    symbol: str,
    db: Session,
    timeframe: str = "1Y",
    min_bars: int = 1
) -> List[Dict[str, Any]]:
    """
    Retrieves chronological OHLCV candles for any stock.
    Supports 1D, 1W, 1M, 3M, 6M, 1Y, 3Y, 5Y, MAX.
    """
    clean_sym = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
    tf_clean = (timeframe or "1Y").upper()
    cfg = TIMEFRAME_CONFIG.get(tf_clean, TIMEFRAME_CONFIG["1Y"])

    # 1. In live mode, attempt to fetch real data for the requested timeframe
    if provider_manager.data_mode == "live":
        try:
            live_candles = stock_data_provider.get_historical(
                clean_sym,
                period=cfg["period"],
                interval=cfg["interval"]
            )
            clean_live = sanitize_and_sort_candles(live_candles)

            if len(clean_live) >= min_bars:
                # Slice if requested (e.g. 3Y from 5Y query)
                limit = cfg.get("limit")
                result_candles = clean_live[-limit:] if (limit and len(clean_live) > limit) else clean_live

                # If daily data was fetched for 1Y, sync cache and 52W metrics to database
                if cfg["interval"] == "1d" and tf_clean in ["1Y", "MAX"]:
                    _persist_daily_candles_and_bounds(clean_sym, clean_live, db)

                return result_candles
        except Exception as e:
            logger.warning(f"Live candle fetch failed for {clean_sym} ({tf_clean}): {e}")

    # 2. Fallback to stored database candles (daily candles)
    prices = (
        db.query(StockPrice)
        .filter(StockPrice.symbol == clean_sym)
        .order_by(StockPrice.timestamp.asc())
        .all()
    )

    if prices:
        db_candles = [
            {
                "timestamp": p.timestamp.strftime("%Y-%m-%d"),
                "time": p.timestamp.strftime("%Y-%m-%d"),
                "open": float(p.open),
                "high": float(p.high),
                "low": float(p.low),
                "close": float(p.close),
                "volume": float(p.volume or 0.0)
            }
            for p in prices
        ]
        clean_db = sanitize_and_sort_candles(db_candles)

        limit_map = {
            "1D": 5, "1W": 5, "1M": 22, "3M": 66, "6M": 125,
            "1Y": 250, "3Y": 750, "5Y": 1250, "MAX": len(clean_db)
        }
        take = limit_map.get(tf_clean, 250)
        return clean_db[-take:] if len(clean_db) > take else clean_db

    # 3. If live fetch failed and DB is empty, try fetching 1Y daily as backup
    if provider_manager.data_mode != "demo":
        try:
            backup_candles = stock_data_provider.get_historical(clean_sym, period="1y", interval="1d")
            clean_backup = sanitize_and_sort_candles(backup_candles)
            if clean_backup:
                _persist_daily_candles_and_bounds(clean_sym, clean_backup, db)
                return clean_backup
        except Exception as e:
            logger.warning(f"Backup daily candle fetch failed for {clean_sym}: {e}")

    return []


def _persist_daily_candles_and_bounds(symbol: str, candles: List[Dict[str, Any]], db: Session):
    """
    Persists verified daily candles to SQLite StockPrice and updates 52W range on Stock.
    """
    try:
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        exchange = stock.exchange if stock and stock.exchange else "NSE"

        # Replace existing prices for this symbol with verified live prices
        db.query(StockPrice).filter(StockPrice.symbol == symbol).delete()

        new_objs = []
        for c in candles:
            try:
                dt_str = str(c["time"])
                dt = datetime.strptime(dt_str, "%Y-%m-%d")
                new_objs.append(StockPrice(
                    symbol=symbol,
                    exchange=exchange,
                    timestamp=dt,
                    open=c["open"],
                    high=c["high"],
                    low=c["low"],
                    close=c["close"],
                    volume=float(c.get("volume", 0.0)),
                    source="yahoo_finance_live",
                    created_at=datetime.utcnow()
                ))
            except Exception:
                continue

        if new_objs:
            db.bulk_save_objects(new_objs)

        # Update 52-week high and low from strictly 1-year (365 days) price history
        if stock and candles:
            cutoff_date = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")
            candles_1y = [c for c in candles if str(c["time"]) >= cutoff_date]
            if not candles_1y:
                candles_1y = candles[-260:]
            highs = [c["high"] for c in candles_1y if c.get("high") is not None]
            lows = [c["low"] for c in candles_1y if c.get("low") is not None]
            if highs and lows:
                stock.high_52w = round(max(highs), 2)
                stock.low_52w = round(min(lows), 2)

        db.commit()
    except Exception as e:
        logger.warning(f"Failed to persist verified candles for {symbol}: {e}")
        try:
            db.rollback()
        except Exception:
            pass
