from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from backend.database import get_db
from backend.models import Stock, StockFundamentals

router = APIRouter(prefix="/screener", tags=["Screener"])

# In-memory / session store for saved screens (self-hosted, zero cost)
SAVED_SCREENS: List[Dict[str, Any]] = [
    {
        "id": "high_growth_low_debt",
        "name": "High ROE & Low Debt Compounders",
        "description": "ROE > 15%, Debt/Equity < 0.5, Revenue Growth > 8%",
        "filters": {"min_roe": 15.0, "max_debt_to_equity": 0.5, "min_rev_growth": 8.0}
    },
    {
        "id": "value_dividend",
        "name": "Value & High Dividend Yield",
        "description": "P/E < 25, Dividend Yield > 1.0%",
        "filters": {"max_pe": 25.0, "min_dividend_yield": 1.0}
    },
    {
        "id": "bluechip_giants",
        "name": "Mega Cap Quality Titans",
        "description": "Market Cap > ₹5,00,000 Cr, ROCE > 15%",
        "filters": {"min_market_cap": 500000.0, "min_roce": 15.0}
    }
]

@router.get("/saved")
def get_saved_screens():
    return SAVED_SCREENS

@router.get("/run")
def run_screen(
    min_market_cap: Optional[float] = None,
    max_market_cap: Optional[float] = None,
    min_pe: Optional[float] = None,
    max_pe: Optional[float] = None,
    min_pb: Optional[float] = None,
    max_pb: Optional[float] = None,
    min_roe: Optional[float] = None,
    min_roce: Optional[float] = None,
    min_rev_growth: Optional[float] = None,
    min_profit_growth: Optional[float] = None,
    max_debt_to_equity: Optional[float] = None,
    min_dividend_yield: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_volume: Optional[float] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Stock, StockFundamentals).outerjoin(StockFundamentals, Stock.symbol == StockFundamentals.symbol)

    if sector and sector.lower() != "all":
        query = query.filter(Stock.sector.ilike(f"%{sector}%"))
    if min_price is not None:
        query = query.filter(Stock.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Stock.current_price <= max_price)
    if min_volume is not None:
        query = query.filter(Stock.volume >= min_volume)

    results = []
    for stock, fund in query.all():
        m_cap = stock.market_cap
        pe = stock.pe_ratio
        pb = stock.pb_ratio
        roe = stock.roe
        roce = stock.roce
        de = stock.debt_to_equity
        div_y = stock.dividend_yield
        rev_g = fund.revenue_growth if fund else 0.0
        prof_g = fund.profit_growth if fund else 0.0

        if min_market_cap is not None and (m_cap is None or m_cap < min_market_cap):
            continue
        if max_market_cap is not None and (m_cap is None or m_cap > max_market_cap):
            continue
        if min_pe is not None and (pe is None or pe < min_pe):
            continue
        if max_pe is not None and (pe is None or pe <= 0 or pe > max_pe):
            continue
        if min_pb is not None and (pb is None or pb < min_pb):
            continue
        if max_pb is not None and (pb is None or pb > max_pb):
            continue
        if min_roe is not None and (roe is None or roe < min_roe):
            continue
        if min_roce is not None and (roce is None or roce < min_roce):
            continue
        if min_rev_growth is not None and (rev_g is None or rev_g < min_rev_growth):
            continue
        if min_profit_growth is not None and (prof_g is None or prof_g < min_profit_growth):
            continue
        if max_debt_to_equity is not None and (de is None or de > max_debt_to_equity):
            continue
        if min_dividend_yield is not None and (div_y is None or div_y < min_dividend_yield):
            continue

        results.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "sector": stock.sector,
            "current_price": stock.current_price,
            "change_percent": stock.change_percent,
            "market_cap": stock.market_cap,
            "pe_ratio": stock.pe_ratio,
            "pb_ratio": stock.pb_ratio,
            "roe": stock.roe,
            "roce": stock.roce,
            "debt_to_equity": stock.debt_to_equity,
            "dividend_yield": stock.dividend_yield,
            "revenue_growth": rev_g,
            "profit_growth": prof_g
        })

    return {
        "count": len(results),
        "results": results
    }
