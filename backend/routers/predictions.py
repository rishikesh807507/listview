from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Stock, StockPrice, IPO
from backend.ml.stock_predictor import stock_predictor
from backend.ml.ipo_predictor import ipo_predictor
from backend.config import settings

router = APIRouter(prefix="/predictions", tags=["AI Predictions"])

from backend.data.historical_candles_service import get_historical_candles_for_symbol

@router.get("/stock/{symbol}")
def get_stock_prediction(
    symbol: str,
    model: str = "RandomForest",  # RandomForest or XGBoost
    db: Session = Depends(get_db)
):
    clean_sym = symbol.upper().strip()
    records = get_historical_candles_for_symbol(clean_sym, db, min_bars=60)
    
    if not records or len(records) < 60:
        raise HTTPException(
            status_code=400,
            detail=f"Historical data unavailable for {clean_sym} (need at least 60 daily bars for ML model training)."
        )

    predictor = stock_predictor if model != "XGBoost" else stock_predictor.__class__(model_type="XGBoost")
    result = predictor.train_and_predict(records)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    result["target_symbol"] = clean_sym
    result["financial_disclaimer"] = settings.FINANCIAL_DISCLAIMER
    return result

@router.get("/ipo/{ipo_id}")
def get_ipo_prediction(ipo_id: int, db: Session = Depends(get_db)):
    ipo = db.query(IPO).filter(IPO.id == ipo_id).first()
    if not ipo:
        raise HTTPException(status_code=404, detail=f"IPO {ipo_id} not found.")

    gmp = ipo.gmp
    sub = ipo.subscription

    ipo_dict = {
        "price_band_high": ipo.price_band_high,
        "issue_size": ipo.issue_size,
        "roe": ipo.roe,
        "roce": ipo.roce,
        "debt": ipo.debt
    }
    gmp_dict = {
        "gmp": gmp.gmp if gmp else 0.0,
        "gmp_percent": gmp.gmp_percent if gmp else 0.0
    } if gmp else None
    
    sub_dict = {
        "qib": sub.qib if sub else 0.0,
        "nii": sub.nii if sub else 0.0,
        "retail": sub.retail if sub else 0.0,
        "total": sub.total if sub else 0.0
    } if sub else None

    pred = ipo_predictor.predict(ipo_dict, gmp_dict, sub_dict)
    pred["ipo_name"] = ipo.company_name
    pred["financial_disclaimer"] = settings.FINANCIAL_DISCLAIMER
    return pred

@router.get("/batch")
def get_predictions_batch(db: Session = Depends(get_db)):
    """Pre-runs lightweight predictions on key tracked stocks for the predictions dashboard."""
    stocks = db.query(Stock).limit(8).all()
    results = []
    for s in stocks:
        prices = db.query(StockPrice).filter(StockPrice.symbol == s.symbol).order_by(StockPrice.timestamp.asc()).all()
        if len(prices) >= 40:
            records = [{"timestamp": p.timestamp.strftime("%Y-%m-%d"), "open": p.open, "high": p.high, "low": p.low, "close": p.close, "volume": p.volume} for p in prices]
            res = stock_predictor.train_and_predict(records)
            if "error" not in res:
                results.append({
                    "symbol": s.symbol,
                    "name": s.name,
                    "current_price": s.current_price,
                    "positive_prob": res["positive_prob"],
                    "expected_return_range": f"{res['expected_return_min']}% to {res['expected_return_max']}%",
                    "confidence": res["confidence"],
                    "model_name": res["model_name"],
                    "walk_forward_accuracy": res["metrics"]["walk_forward_accuracy"],
                    "updated_at": res["prediction_timestamp"]
                })
    return {"predictions": results, "disclaimer": settings.FINANCIAL_DISCLAIMER}
