from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models import IPOGMP, IPO
from backend.data_providers.provider_manager import provider_manager
from backend.config import settings

router = APIRouter(prefix="/gmp", tags=["GMP"])

@router.get("")
def get_gmp_list(refresh: bool = False, db: Session = Depends(get_db)):
    """
    Returns latest Grey Market Premium for IPOs.
    Clearly marks GMP as unofficial and unregulated.
    """
    if refresh:
        provider_manager.sync_gmp_data(db)

    records = db.query(IPOGMP).order_by(IPOGMP.gmp_percent.desc()).all()
    results = []

    for r in records:
        results.append({
            "id": r.id,
            "ipo_id": r.ipo_id,
            "company_name": r.company_name,
            "gmp": r.gmp,
            "gmp_percent": r.gmp_percent,
            "min_gmp": r.min_gmp,
            "max_gmp": r.max_gmp,
            "estimated_listing_price": r.estimated_listing_price,
            "estimated_listing_gain": r.estimated_listing_gain,
            "source": r.source,
            "timestamp": r.updated_at.strftime("%d %b %Y, %I:%M %p UTC") if r.updated_at else "Recently",
            "disclaimer": r.disclaimer
        })

    return {
        "count": len(results),
        "data": results,
        "disclaimer": "GMP is unofficial and unregulated. It is not an NSE/BSE price and should not be treated as a guaranteed listing price.",
        "formula": "Estimated Listing Price = Upper Price Band + GMP",
        "attribution": "Dataset provided via open-source repository (Spectrumz00/india-ipo-gmp-data, CC BY 4.0)"
    }
