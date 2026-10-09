from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models import Watchlist, Stock, StockPrice
from backend.ml.stock_predictor import stock_predictor

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

class WatchlistAddRequest(BaseModel):
    symbol: str
    notes: Optional[str] = None

@router.get("")
def get_watchlist(db: Session = Depends(get_db)):
    items = db.query(Watchlist).all()
    results = []
    for item in items:
        stock = db.query(Stock).filter(Stock.symbol == item.symbol).first()
        pred_snippet = None
        if stock:
            prices = db.query(StockPrice).filter(StockPrice.symbol == stock.symbol).order_by(StockPrice.timestamp.asc()).all()
            try:
                if len(prices) >= 40:
                    candles = [{"timestamp": p.timestamp.strftime("%Y-%m-%d"), "open": p.open, "high": p.high, "low": p.low, "close": p.close, "volume": p.volume} for p in prices]
                    p_res = stock_predictor.train_and_predict(candles)
                    if isinstance(p_res, dict) and "error" not in p_res:
                        pred_snippet = {
                            "positive_prob": p_res.get("positive_prob"),
                            "confidence": p_res.get("confidence"),
                            "range": f"{p_res.get('expected_return_min')}% to {p_res.get('expected_return_max')}%"
                        }
            except Exception:
                pred_snippet = None

            results.append({
                "id": item.id,
                "symbol": item.symbol,
                "name": stock.name,
                "sector": stock.sector,
                "current_price": stock.current_price,
                "change": stock.change,
                "change_percent": stock.change_percent,
                "volume": stock.volume,
                "pe_ratio": stock.pe_ratio,
                "high_52w": stock.high_52w,
                "low_52w": stock.low_52w,
                "notes": item.notes,
                "prediction": pred_snippet
            })
    return {"watchlist": results}

@router.post("")
def add_to_watchlist(req: WatchlistAddRequest, db: Session = Depends(get_db)):
    sym = req.symbol.upper().strip()
    stock = db.query(Stock).filter(Stock.symbol == sym).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {sym} not found.")

    existing = db.query(Watchlist).filter(Watchlist.symbol == sym).first()
    if existing:
        return {"message": f"{sym} is already in your watchlist.", "item_id": existing.id}

    item = Watchlist(symbol=sym, notes=req.notes)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": f"Added {sym} to watchlist", "item_id": item.id}

@router.delete("/{item_id}")
def remove_from_watchlist(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Watchlist).filter(Watchlist.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")
    db.delete(item)
    db.commit()
    return {"message": "Removed from watchlist"}
