"""
Official Securities Master service for Listview.
Maintains the authoritative database of NSE/BSE equities from the official exchange master list.
"""
import os
import csv
import logging
import urllib.request
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import Stock

logger = logging.getLogger("Listview")

NSE_SECURITIES_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
LOCAL_CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "demo-data", "EQUITY_L.csv")

def refresh_securities_master(db: Session) -> dict:
    """
    Downloads or reads the official NSE equity master and synchronizes it into the stocks table.
    Ensures zero dependency on per-keystroke scraping.
    """
    csv_text = None
    source = "NSE Official Archive"

    try:
        req = urllib.request.Request(
            NSE_SECURITIES_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            csv_text = resp.read().decode("utf-8")
            # Cache locally
            os.makedirs(os.path.dirname(LOCAL_CACHE_PATH), exist_ok=True)
            with open(LOCAL_CACHE_PATH, "w", encoding="utf-8") as f:
                f.write(csv_text)
            logger.info("Successfully refreshed NSE securities master from online archive.")
    except Exception as e:
        logger.warning(f"Could not reach NSE archive directly ({e}); falling back to local cached master.")
        if os.path.exists(LOCAL_CACHE_PATH):
            with open(LOCAL_CACHE_PATH, "r", encoding="utf-8") as f:
                csv_text = f.read()
            source = "Local Cached NSE Master"
        else:
            return {"status": "failed", "error": str(e), "source": source}

    if not csv_text:
        return {"status": "failed", "error": "Empty securities master text", "source": source}

    reader = csv.reader(csv_text.strip().splitlines())
    header = next(reader, None)
    if not header:
        return {"status": "failed", "error": "Invalid CSV header", "source": source}

    inserted = 0
    updated = 0

    all_existing = {s.symbol: s for s in db.query(Stock).all()}

    for row in reader:
        if not row or len(row) < 7:
            continue
        symbol = row[0].strip().upper()
        company_name = row[1].strip()
        series = row[2].strip()
        isin = row[6].strip()

        if series not in ("EQ", "BE", "BZ", "SM"):
            continue

        existing = all_existing.get(symbol)
        if existing:
            existing.name = company_name
            existing.isin = isin
            existing.exchange = "NSE"
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            updated += 1
        else:
            new_stock = Stock(
                symbol=symbol,
                name=company_name,
                isin=isin,
                exchange="NSE",
                instrument_type="EQUITY",
                is_active=True,
                updated_at=datetime.utcnow()
            )
            db.add(new_stock)
            inserted += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing securities master: {e}")
        return {"status": "error", "error": str(e)}

    return {
        "status": "success",
        "inserted": inserted,
        "updated": updated,
        "total_equities": db.query(Stock).count(),
        "source": source,
        "last_refreshed": datetime.utcnow().isoformat()
    }
