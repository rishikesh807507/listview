from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.database import get_db
from backend.models import Stock

router = APIRouter(prefix="/sectors", tags=["Sectors"])

SECTOR_DEFINITIONS = [
    "IT", "Banking", "Finance", "Automobile", "Pharma", "FMCG",
    "Energy", "Infrastructure", "Metals", "Telecom", "Real Estate", "Chemicals"
]

@router.get("")
def get_sectors_overview(db: Session = Depends(get_db)):
    stocks = db.query(Stock).filter(Stock.is_active == True).all()

    sector_map: Dict[str, List[Stock]] = {}
    for sec in SECTOR_DEFINITIONS:
        sector_map[sec] = []

    for s in stocks:
        sec = s.sector or "Other"
        matched = False
        for target in SECTOR_DEFINITIONS:
            if target.lower() in sec.lower():
                sector_map[target].append(s)
                matched = True
                break
        if not matched and sec not in sector_map:
            sector_map[sec] = [s]

    results = []
    for name, s_list in sector_map.items():
        if not s_list:
            # Provide baseline representation
            results.append({
                "sector": name,
                "count": 0,
                "average_return": 0.0,
                "total_market_cap_cr": 0.0,
                "total_volume": 0,
                "gainers": 0,
                "losers": 0,
                "status": "Neutral"
            })
            continue

        gainers = sum(1 for s in s_list if s.change is not None and s.change > 0)
        losers = sum(1 for s in s_list if s.change is not None and s.change < 0)
        valid_ret = [s.change_percent for s in s_list if s.change_percent is not None]
        avg_ret = round(sum(valid_ret) / len(valid_ret), 2) if valid_ret else 0.0
        total_mcap = round(sum((s.market_cap or 0.0) for s in s_list), 2)
        total_vol = sum(int(s.volume or 0) for s in s_list)

        results.append({
            "sector": name,
            "count": len(s_list),
            "average_return": avg_ret,
            "total_market_cap_cr": total_mcap,
            "total_volume": total_vol,
            "gainers": gainers,
            "losers": losers,
            "status": "Positive" if avg_ret > 0 else ("Negative" if avg_ret < 0 else "Neutral")
        })

    # Sort by performance
    results = sorted(results, key=lambda x: x["average_return"], reverse=True)
    return {"sectors": results}
