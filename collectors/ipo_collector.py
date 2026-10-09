import logging
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal
from backend.data_providers.ipo.ipo_provider_manager import ipo_provider_manager

logger = logging.getLogger("IPOCollector")

def collect_ipos() -> dict:
    """
    Polls official exchange disclosures (NSE) and public tracking feeds,
    updates database records, and outputs Section 27 compliance health report.
    """
    db = SessionLocal()
    try:
        report = ipo_provider_manager.refresh_ipo_database(db)
        print("\n" + json.dumps({
            "provider": "nse_ipo_provider",
            "records_received": report.get("records_received", 0),
            "records_valid": report.get("records_valid", 0),
            "records_rejected": report.get("records_rejected", 0),
            "stale_records": report.get("stale_records", 0),
            "timestamp": report.get("timestamp")
        }, indent=2))
        return report
    except Exception as e:
        logger.error(f"[IPOCollector Error] {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    collect_ipos()
