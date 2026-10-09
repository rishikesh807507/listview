from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.data.market_data_service import market_data_service

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/overview")
def get_market_overview(db: Session = Depends(get_db)):
    """
    Returns verified market overview with live/cached benchmark indices,
    dynamically computed top gainers and top losers from the same session snapshot,
    and market breadth. Never returns hard-coded or fabricated numbers.
    """
    return market_data_service.get_market_overview(db)

@router.get("/data-health")
def get_data_health():
    """
    Returns automated data quality diagnostics, provider status,
    and rejection audit logs.
    """
    return market_data_service.get_data_health()
