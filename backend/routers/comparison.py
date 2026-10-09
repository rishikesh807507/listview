from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Stock, StockFundamentals, IPO, IPOGMP, IPOSubscription

router = APIRouter(prefix="/compare", tags=["Comparison"])

@router.get("/stocks")
def compare_stocks(symbols: str = Query("RELIANCE,TCS,HDFCBANK,INFY"), db: Session = Depends(get_db)):
    """
    Compares up to 5 stocks across valuation, growth, profitability, and balance sheet metrics.
    Neutral comparison without subjective 'best' or 'worst' badges.
    """
    sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()][:5]
    if not sym_list:
        raise HTTPException(status_code=400, detail="Please provide at least one stock symbol to compare.")

    results = []
    for sym in sym_list:
        stock = db.query(Stock).filter(Stock.symbol == sym).first()
        fund = db.query(StockFundamentals).filter(StockFundamentals.symbol == sym).first()
        
        if stock:
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
                "revenue": fund.revenue if fund else 0.0,
                "revenue_growth": fund.revenue_growth if fund else 0.0,
                "net_profit": fund.net_profit if fund else 0.0,
                "profit_growth": fund.profit_growth if fund else 0.0,
                "eps": fund.eps if fund else 0.0,
                "free_cash_flow": fund.free_cash_flow if fund else 0.0,
                "promoter_holding": fund.promoter_holding if fund else 0.0
            })
            
    return {"comparison": results}

@router.get("/ipos")
def compare_ipos(ids: str = Query(..., description="Comma separated IDs"), db: Session = Depends(get_db)):
    """
    Compares multiple IPOs side-by-side with factual differences.
    Missing values return None (N/A), never fake 0.0.
    """
    id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()][:5]
    results = []

    for ipo_id in id_list:
        ipo = db.query(IPO).filter(IPO.id == ipo_id).first()
        if ipo:
            gmp = ipo.gmp
            sub = ipo.subscription
            high_p = ipo.price_band_high or ipo.price_band_low
            gmp_val = gmp.gmp if (gmp and gmp.gmp is not None) else None
            indicative = round(high_p + gmp_val, 2) if (high_p is not None and gmp_val is not None) else None

            actual_listing = ipo.actual_listing_price
            day_close = getattr(ipo, 'listing_day_close', None)
            if (actual_listing is None or day_close is None) and ipo.status in ("LISTED", "LISTING_TODAY"):
                try:
                    from backend.data_providers.ipo.listing_data_provider import listing_data_provider
                    l_info = listing_data_provider.get_listing_data(
                        symbol=ipo.symbol,
                        company_name=ipo.company_name,
                        listing_date=ipo.listing_date,
                        db=db
                    )
                    if actual_listing is None and l_info.get("actual_listing_price"):
                        actual_listing = l_info["actual_listing_price"]
                    if day_close is None and l_info.get("listing_day_close"):
                        day_close = l_info["listing_day_close"]
                except Exception:
                    pass

            eff_issue = ipo.issue_price or ipo.price_band_high or ipo.price_band_low

            results.append({
                "id": ipo.id,
                "symbol": ipo.symbol,
                "company_name": ipo.company_name,
                "isin": ipo.isin,
                "board": ipo.board or ipo.ipo_type or "Mainboard",
                "ipo_type": ipo.board or ipo.ipo_type or "Mainboard",
                "exchange": ipo.exchange or "NSE, BSE",
                "issue_price": eff_issue,
                "price_band_low": ipo.price_band_low,
                "price_band_high": ipo.price_band_high,
                "price_band": f"₹{ipo.price_band_low} - ₹{ipo.price_band_high}" if (ipo.price_band_low is not None and ipo.price_band_high is not None) else "Not available",
                "lot_size": ipo.lot_size,
                "issue_size_crore": ipo.issue_size_crore or ipo.issue_size,
                "fresh_issue_crore": ipo.fresh_issue_crore,
                "offer_for_sale_crore": ipo.offer_for_sale_crore,
                "open_date": (ipo.issue_open_date or ipo.open_date).isoformat() if (ipo.issue_open_date or ipo.open_date) else None,
                "close_date": (ipo.issue_close_date or ipo.close_date).isoformat() if (ipo.issue_close_date or ipo.close_date) else None,
                "listing_date": ipo.listing_date.isoformat() if ipo.listing_date else None,
                "gmp": gmp_val,
                "historical_gmp": gmp_val,
                "gmp_percent": gmp.gmp_percent if gmp else None,
                "indicative_listing_price": indicative,
                "estimated_listing_price": indicative,
                "actual_listing_price": actual_listing,
                "listing_day_close": day_close,
                "qib_subscription": sub.qib if sub else None,
                "nii_subscription": sub.nii if sub else None,
                "retail_subscription": sub.retail if sub else None,
                "total_subscription": sub.total if sub else None,
                "revenue": ipo.revenue,
                "profit": ipo.profit,
                "eps": ipo.eps,
                "pe": getattr(ipo, 'pe_ratio', None),
                "pe_ratio": getattr(ipo, 'pe_ratio', None),
                "roe": ipo.roe,
                "roce": getattr(ipo, 'roce', None),
                "debt": ipo.debt,
                "market_cap": None,
                "status": ipo.status,
                "source": ipo.source or "Exchange Public Disclosure & Filings",
                "source_url": ipo.source_url,
                "last_verified_at": ipo.last_verified_at.strftime("%d %b %Y, %I:%M %p IST") if ipo.last_verified_at else None
            })

    return {"ipos": results}
