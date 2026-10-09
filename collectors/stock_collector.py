import logging
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal
from backend.models import Stock
from backend.data.stock_provider import stock_data_provider
from backend.data.market_session import get_ist_now, evaluate_freshness

logger = logging.getLogger("StockCollector")

def collect_stocks() -> dict:
    """
    Polls verified stock data provider, validates mathematically,
    persists verified quotes, and produces Section 27 automatic health report.
    """
    db = SessionLocal()
    records_received = 0
    records_valid = 0
    records_rejected = 0
    stale_records = 0
    rejected_details = []

    try:
        stocks = db.query(Stock).all()
        records_received = len(stocks)

        for s in stocks:
            quote = stock_data_provider.get_quote(s.symbol)
            if quote:
                freshness = evaluate_freshness(quote["timestamp"])
                if freshness["freshness"] == "Stale":
                    stale_records += 1

                s.current_price = quote["price"]
                s.change = quote["change"]
                s.change_percent = quote["change_percent"]
                s.volume = quote["volume"]
                s.updated_at = datetime.utcnow()
                records_valid += 1
            else:
                records_rejected += 1
                rejected_details.append({
                    "symbol": s.symbol,
                    "reason": "Failed live query or failed mathematical validation"
                })

        db.commit()
    except Exception as e:
        logger.error(f"[StockCollector Error] {e}")
        db.rollback()
    finally:
        db.close()

    report = {
        "provider": "stock_provider",
        "records_received": records_received,
        "records_valid": records_valid,
        "records_rejected": records_rejected,
        "stale_records": stale_records,
        "timestamp": get_ist_now().strftime("%d %b %Y, %I:%M:%S %p IST")
    }

    print("\n" + json.dumps(report, indent=2))
    if rejected_details:
        print("[StockCollector] Rejected records:")
        for r in rejected_details:
            print(f"  - {r['symbol']}: {r['reason']}")

    return report

if __name__ == "__main__":
    collect_stocks()
