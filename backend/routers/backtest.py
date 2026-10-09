from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models import StockPrice, Stock
from backend.backtest.engine import run_backtest

router = APIRouter(prefix="/backtest", tags=["Backtesting"])

class BacktestPayload(BaseModel):
    symbol: str
    strategy: str = "SMA"  # SMA, EMA, RSI, MACD, Momentum
    initial_capital: float = 100000.0
    parameters: Optional[Dict[str, Any]] = None

from backend.data.historical_candles_service import get_historical_candles_for_symbol

@router.post("")
def execute_backtest(payload: BacktestPayload, db: Session = Depends(get_db)):
    sym = payload.symbol.upper().strip()
    candle_dicts = get_historical_candles_for_symbol(sym, db, min_bars=30)

    if not candle_dicts or len(candle_dicts) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Historical data unavailable for {sym} (minimum 30 daily trading bars required)."
        )


    result = run_backtest(
        prices=candle_dicts,
        strategy=payload.strategy,
        initial_capital=payload.initial_capital,
        params=payload.parameters
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    result["symbol"] = sym
    return result
