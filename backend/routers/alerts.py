from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models import Alert, Stock

router = APIRouter(prefix="/alerts", tags=["Alerts"])

class AlertCreate(BaseModel):
    identifier: str
    alert_type: str  # price_above, price_below, pct_change, 52w_high, ipo_open, gmp_change
    condition: str
    threshold: float

@router.get("")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).all()
    results = []
    for a in alerts:
        # Check if triggered
        stock = db.query(Stock).filter(Stock.symbol == a.identifier.upper()).first()
        is_triggered = False
        current_val = 0.0
        if stock:
            current_val = stock.current_price
            if a.alert_type == "price_above" and stock.current_price >= a.threshold:
                is_triggered = True
            elif a.alert_type == "price_below" and stock.current_price <= a.threshold:
                is_triggered = True
            elif a.alert_type == "pct_change" and abs(stock.change_percent) >= a.threshold:
                is_triggered = True

        results.append({
            "id": a.id,
            "identifier": a.identifier,
            "alert_type": a.alert_type,
            "condition": a.condition,
            "threshold": a.threshold,
            "current_value": current_val,
            "is_triggered": is_triggered,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return {"alerts": results}

@router.post("")
def create_alert(req: AlertCreate, db: Session = Depends(get_db)):
    new_alert = Alert(
        identifier=req.identifier.upper().strip(),
        alert_type=req.alert_type,
        condition=req.condition,
        threshold=req.threshold
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return {"message": "Alert created successfully", "alert_id": new_alert.id}

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found.")
    db.delete(a)
    db.commit()
    return {"message": "Alert deleted"}
