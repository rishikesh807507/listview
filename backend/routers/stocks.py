from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import case, or_, and_
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models import Stock, StockPrice, StockFundamentals
from backend.schemas import StockResponse, StockFundamentalsResponse, HealthScoreResponse
from backend.data.market_data_service import market_data_service
from backend.config import settings
from backend.ml.health_score import compute_health_score

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("", response_model=List[StockResponse])
def get_stocks(
    sector: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Stock).filter(Stock.is_active == True)

    # Sector filter: ignore "all", "All Sectors", "all_sectors", empty, etc.
    if sector:
        sec_clean = sector.strip()
        if sec_clean.lower() not in ("all", "all sectors", "all_sectors", "", "none"):
            query = query.filter(Stock.sector.ilike(f"%{sec_clean}%"))

    # Search filter: partial matching across symbol and company name
    if search and search.strip():
        s = f"%{search.strip()}%"
        query = query.filter((Stock.symbol.ilike(s)) | (Stock.name.ilike(s)))

    # Order by active price first, then market_cap desc, volume desc, symbol asc
    has_price = case((Stock.current_price.isnot(None) & (Stock.current_price > 0), 1), else_=0)
    query = query.order_by(
        has_price.desc(),
        Stock.market_cap.desc().nullslast(),
        Stock.volume.desc().nullslast(),
        Stock.symbol.asc()
    )

    stocks = query.offset(skip).limit(limit).all()
    for s in stocks:
        if s.current_price is not None and s.current_price <= 0:
            s.current_price = None
            s.change = None
            s.change_percent = None
    return stocks

# Common market aliases for Indian equities
COMPANY_ALIASES = {
    "RIL": "RELIANCE",
    "RELIANCE": "RELIANCE",
    "INFOSYS": "INFY",
    "INFY": "INFY",
    "TCS": "TCS",
    "TATA CONSULTANCY": "TCS",
    "SBI": "SBIN",
    "STATE BANK": "SBIN",
    "STATE BANK OF INDIA": "SBIN",
    "HDFC": "HDFCBANK",
    "HDFC BANK": "HDFCBANK",
    "ICICI": "ICICIBANK",
    "ICICI BANK": "ICICIBANK",
    "AIRTEL": "BHARTIARTL",
    "BHARTI": "BHARTIARTL",
    "BHARTI AIRTEL": "BHARTIARTL",
    "LT": "LT",
    "L&T": "LT",
    "LARSEN": "LT",
    "LARSEN & TOUBRO": "LT",
    "M&M": "M&M",
    "MAHINDRA": "M&M",
    "MARUTI": "MARUTI",
    "MARUTI SUZUKI": "MARUTI",
    "KOTAK": "KOTAKBANK",
    "KOTAK BANK": "KOTAKBANK",
    "WIPRO": "WIPRO",
    "BAJAJ AUTO": "BAJAJ-AUTO",
    "BAJAJ FINANCE": "BAJFINANCE",
    "BAJAJ FINSERV": "BAJAJFINSV",
    "ITC": "ITC"
}

@router.get("/search")
def search_stocks(q: str = Query("", min_length=0), limit: int = 25, db: Session = Depends(get_db)):
    """
    Search active stocks by symbol, company name, ISIN, or alias for autocomplete selectors.
    Case-insensitive, ranked by relevance (exact/prefix matches first).
    If query is empty, returns top active securities from database.
    """
    clean_q = (q or "").strip().upper()
    if not clean_q:
        has_price = case((Stock.current_price.isnot(None) & (Stock.current_price > 0), 1), else_=0)
        stocks = (
            db.query(Stock)
            .filter(Stock.is_active == True)
            .order_by(has_price.desc(), Stock.market_cap.desc().nullslast(), Stock.volume.desc().nullslast(), Stock.symbol.asc())
            .limit(limit)
            .all()
        )
        return [
            {
                "symbol": s.symbol,
                "company_name": s.name,
                "exchange": s.exchange,
                "isin": s.isin,
                "sector": s.sector,
                "instrument_type": "EQUITY",
                "current_price": s.current_price if (s.current_price is not None and s.current_price > 0) else None,
                "change": s.change if (s.current_price is not None and s.current_price > 0) else None,
                "change_percent": s.change_percent if (s.current_price is not None and s.current_price > 0) else None,
            }
            for s in stocks
        ]

    tokens = [t for t in clean_q.split() if t]
    
    # 1. Check alias mapping
    target_alias_symbol = COMPANY_ALIASES.get(clean_q)

    # 2. Query database master
    query = db.query(Stock).filter(Stock.is_active == True)
    
    s_like = f"%{clean_q}%"
    conditions = [
        Stock.symbol.ilike(s_like),
        Stock.name.ilike(s_like),
        Stock.isin.ilike(s_like)
    ]
    if target_alias_symbol:
        conditions.append(Stock.symbol == target_alias_symbol)

    # Multi-token matching if query has multiple words (e.g. 'HDFC Bank')
    if len(tokens) > 1:
        token_conds = [
            (Stock.symbol.ilike(f"%{t}%") | Stock.name.ilike(f"%{t}%"))
            for t in tokens
        ]
        conditions.append(and_(*token_conds))

    matches = query.filter(or_(*conditions)).all()

    # Relevance scoring: exact symbol (0), alias match (1), exact name (2), prefix symbol (3), prefix name (4), contains (5)
    # Secondary sort by has_price (0=has price, 1=no price) so active stocks appear first
    def relevance_key(stock: Stock):
        sym = (stock.symbol or "").upper()
        nm = (stock.name or "").upper()
        p_rank = 0 if (stock.current_price is not None and stock.current_price > 0) else 1
        mcap_rank = -(stock.market_cap or 0)
        if sym == clean_q:
            return (0, p_rank, mcap_rank, sym)
        if target_alias_symbol and sym == target_alias_symbol:
            return (1, p_rank, mcap_rank, sym)
        if nm == clean_q or nm.replace(" LIMITED", "").replace(" LTD", "") == clean_q:
            return (2, p_rank, mcap_rank, sym)
        if sym.startswith(clean_q):
            return (3, p_rank, mcap_rank, sym)
        if nm.startswith(clean_q):
            return (4, p_rank, mcap_rank, sym)
        if clean_q in sym:
            return (5, p_rank, mcap_rank, sym)
        return (6, p_rank, mcap_rank, sym)

    matches.sort(key=relevance_key)
    top_matches = matches[:limit]

    return [
        {
            "id": st.id,
            "symbol": st.symbol,
            "name": st.name,
            "company_name": st.name,
            "exchange": st.exchange or "NSE",
            "isin": getattr(st, "isin", None) or "Not available",
            "sector": st.sector or "General",
            "instrument_type": getattr(st, "instrument_type", "EQUITY") or "EQUITY",
            "current_price": st.current_price if (st.current_price is not None and st.current_price > 0) else None,
            "change": st.change if (st.current_price is not None and st.current_price > 0) else None,
            "change_percent": st.change_percent if (st.current_price is not None and st.current_price > 0) else None
        }
        for st in top_matches
    ]

@router.post("/refresh-master")
def trigger_refresh_securities_master(db: Session = Depends(get_db)):
    """Triggers background sync with the official NSE securities master."""
    from backend.data.securities_master import refresh_securities_master
    return refresh_securities_master(db)

@router.get("/{symbol}")
def get_stock_detail(symbol: str, db: Session = Depends(get_db)):
    from backend.data.historical_candles_service import get_historical_candles_for_symbol
    clean_sym = symbol.upper().strip()
    db_stock = db.query(Stock).filter(Stock.symbol == clean_sym).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail=f"Stock {clean_sym} not found.")

    verified_quote = market_data_service.get_stock_quote(db, clean_sym)

    # If verified quote has price, update stock instance
    if verified_quote.get("current_price") is not None:
        db_stock.current_price = verified_quote["current_price"]
        db_stock.change = verified_quote.get("change", db_stock.change)
        db_stock.change_percent = verified_quote.get("change_percent", db_stock.change_percent)
        db_stock.volume = verified_quote.get("volume", db_stock.volume)

    # Sync fundamentals from StockFundamentals if present
    fund = db.query(StockFundamentals).filter(StockFundamentals.symbol == clean_sym).first()

    # Verify and correct 52-week bounds if inconsistent or missing
    cur_p = db_stock.current_price
    needs_52w_refresh = (
        not db_stock.high_52w
        or not db_stock.low_52w
        or db_stock.high_52w <= 0
        or db_stock.low_52w <= 0
        or (cur_p is not None and cur_p > 0 and (db_stock.low_52w > cur_p or db_stock.high_52w < cur_p))
    )
    if needs_52w_refresh:
        candles_1y = get_historical_candles_for_symbol(clean_sym, db, timeframe="1Y")
        if candles_1y:
            highs = [c["high"] for c in candles_1y if c.get("high") is not None]
            lows = [c["low"] for c in candles_1y if c.get("low") is not None]
            if highs and lows:
                db_stock.high_52w = round(max(highs), 2)
                db_stock.low_52w = round(min(lows), 2)

    db_stock.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_stock)

    # Helper to resolve valid positive numeric metric or None (no fake 0s)
    def clean_positive(v, fallback=None):
        if v is not None and isinstance(v, (int, float)) and v > 0:
            return round(float(v), 2)
        if fallback is not None and isinstance(fallback, (int, float)) and fallback > 0:
            return round(float(fallback), 2)
        return None

    def clean_numeric(v, fallback=None):
        if v is not None and isinstance(v, (int, float)):
            return round(float(v), 2)
        if fallback is not None and isinstance(fallback, (int, float)):
            return round(float(fallback), 2)
        return None

    pe_val = clean_positive(db_stock.pe_ratio, getattr(fund, "pe", None))
    pb_val = clean_positive(db_stock.pb_ratio, getattr(fund, "pb", None))
    roe_val = clean_numeric(db_stock.roe, getattr(fund, "roe", None))
    roce_val = clean_numeric(db_stock.roce, getattr(fund, "roce", None))
    de_val = clean_numeric(db_stock.debt_to_equity, getattr(fund, "debt_to_equity", None))
    div_val = clean_numeric(db_stock.dividend_yield, getattr(fund, "dividend_yield", None))
    mcap_val = clean_positive(db_stock.market_cap, getattr(fund, "market_cap", None))

    stock_data = {
        "id": db_stock.id,
        "symbol": db_stock.symbol,
        "name": db_stock.name,
        "exchange": db_stock.exchange or "NSE",
        "isin": db_stock.isin or "Not available",
        "instrument_type": getattr(db_stock, "instrument_type", "EQUITY") or "EQUITY",
        "sector": db_stock.sector or "General",
        "industry": db_stock.industry,
        "current_price": db_stock.current_price,
        "change": db_stock.change,
        "change_percent": db_stock.change_percent,
        "market_cap": mcap_val,
        "pe_ratio": pe_val,
        "pb_ratio": pb_val,
        "roe": roe_val,
        "roce": roce_val,
        "dividend_yield": div_val,
        "debt_to_equity": de_val,
        "high_52w": clean_positive(db_stock.high_52w),
        "low_52w": clean_positive(db_stock.low_52w),
        "volume": db_stock.volume,
        "is_active": db_stock.is_active,
        "updated_at": db_stock.updated_at.isoformat() if db_stock.updated_at else None
    }

    return {
        "stock": stock_data,
        "status": verified_quote.get("status", "Verified"),
        "source": verified_quote.get("source", "NSE/BSE Public Feed"),
        "last_updated": verified_quote.get("timestamp"),
        "notice": verified_quote.get("warning"),
        "disclaimer": settings.FINANCIAL_DISCLAIMER
    }

@router.get("/{symbol}/history")
def get_stock_history(
    symbol: str,
    timeframe: str = "1Y",  # 1D, 1W, 1M, 3M, 6M, 1Y, 3Y, 5Y, MAX
    db: Session = Depends(get_db)
):
    from backend.data.historical_candles_service import get_historical_candles_for_symbol
    clean_sym = symbol.upper().strip()
    candles = get_historical_candles_for_symbol(clean_sym, db, timeframe=timeframe, min_bars=1)

    if not candles:
        return {"symbol": clean_sym, "candles": [], "status": "Empty"}

    return {
        "symbol": clean_sym,
        "count": len(candles),
        "candles": candles,
        "source": "Local Historical Database / Exchange Historical Feed",
        "attribution": "TradingView Lightweight Charts (Apache-2.0 License)"
    }

@router.get("/{symbol}/health", response_model=HealthScoreResponse)
def get_stock_health(symbol: str, db: Session = Depends(get_db)):
    clean_sym = symbol.upper().strip()
    fund = db.query(StockFundamentals).filter(StockFundamentals.symbol == clean_sym).first()
    if not fund:
        raise HTTPException(status_code=404, detail="Fundamentals not available for symbol.")
    
    fund_dict = {c.name: getattr(fund, c.name) for c in fund.__table__.columns}
    res = compute_health_score(fund_dict)
    return {
        "symbol": clean_sym,
        "overall_health": res["overall_health"],
        "score_out_of_100": res["score_out_of_100"],
        "components": res["components"],
        "disclaimer": res["disclaimer"]
    }
