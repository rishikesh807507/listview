from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.database import get_db
from backend.models import PortfolioItem, Stock

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

class TradeRequest(BaseModel):
    symbol: str
    quantity: int
    buy_price: float
    notes: Optional[str] = None

@router.get("")
def get_portfolio(db: Session = Depends(get_db)):
    items = db.query(PortfolioItem).all()
    
    holdings = []
    total_invested = 0.0
    total_current_value = 0.0
    sector_alloc = {}

    for it in items:
        stock = db.query(Stock).filter(Stock.symbol == it.symbol).first()
        curr_price = (stock.current_price if (stock and stock.current_price is not None) else it.buy_price)
        sector = (stock.sector if (stock and stock.sector) else "General")
        
        invested = round(it.quantity * it.buy_price, 2)
        curr_val = round(it.quantity * curr_price, 2)
        pnl = round(curr_val - invested, 2)
        pnl_pct = round((pnl / invested) * 100, 2) if invested > 0 else 0.0

        total_invested += invested
        total_current_value += curr_val

        sector_alloc[sector] = sector_alloc.get(sector, 0.0) + curr_val

        holdings.append({
            "id": it.id,
            "symbol": it.symbol,
            "name": stock.name if stock else it.symbol,
            "sector": sector,
            "quantity": it.quantity,
            "buy_price": it.buy_price,
            "current_price": curr_price,
            "invested_value": invested,
            "current_value": curr_val,
            "profit_loss": pnl,
            "return_percent": pnl_pct,
            "buy_date": it.buy_date.strftime("%Y-%m-%d"),
            "notes": it.notes
        })

    # Portfolio allocation %
    for h in holdings:
        h["allocation_percent"] = round((h["current_value"] / total_current_value * 100), 2) if total_current_value > 0 else 0.0

    sector_distribution = []
    for sec, val in sector_alloc.items():
        pct = round((val / total_current_value * 100), 2) if total_current_value > 0 else 0.0
        sector_distribution.append({"sector": sec, "value": val, "percent": pct})

    total_pnl = round(total_current_value - total_invested, 2)
    total_pnl_pct = round((total_pnl / total_invested * 100), 2) if total_invested > 0 else 0.0

    return {
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current_value, 2),
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_pct,
            "total_holdings_count": len(holdings)
        },
        "holdings": holdings,
        "sector_allocation": sector_distribution,
        "disclaimer": "Virtual Portfolio Simulator for educational & research purposes only. No real capital or transactions involved."
    }

@router.post("/buy")
def buy_stock(req: TradeRequest, db: Session = Depends(get_db)):
    sym = req.symbol.upper().strip()
    if req.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
    if req.buy_price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive.")

    # Check existing holding
    existing = db.query(PortfolioItem).filter(PortfolioItem.symbol == sym).first()
    if existing:
        # Weighted average buy price
        total_qty = existing.quantity + req.quantity
        avg_price = round(((existing.quantity * existing.buy_price) + (req.quantity * req.buy_price)) / total_qty, 2)
        existing.quantity = total_qty
        existing.buy_price = avg_price
        existing.notes = req.notes or existing.notes
        db.commit()
        return {"message": f"Updated position for {sym}", "item_id": existing.id}
    else:
        new_item = PortfolioItem(
            symbol=sym,
            quantity=req.quantity,
            buy_price=req.buy_price,
            notes=req.notes
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {"message": f"Bought {req.quantity} shares of {sym}", "item_id": new_item.id}

@router.post("/sell/{item_id}")
def sell_stock(item_id: int, quantity: int, db: Session = Depends(get_db)):
    item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Holding not found.")
    
    if quantity >= item.quantity:
        db.delete(item)
        db.commit()
        return {"message": f"Fully sold position in {item.symbol}"}
    else:
        item.quantity -= quantity
        db.commit()
        return {"message": f"Sold {quantity} shares of {item.symbol}, {item.quantity} remaining."}
