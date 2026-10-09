import logging
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal
from backend.data_providers.ipo.ipo_provider_manager import ipo_provider_manager
from backend.data_providers.ipo.gmp_provider import gmp_provider

logger = logging.getLogger("GMPCollector")

def collect_gmp() -> dict:
    """
    Fetches latest unofficial GMP rates from public trackers,
    updates database records, and outputs Section 27 compliance health report.
    """
    db = SessionLocal()
    try:
        report = ipo_provider_manager.refresh_ipo_database(db)
        print(f"[GMPCollector] Synchronized unofficial GMP rates: valid={report.get('records_valid', 0)}")
        return report
    except Exception as e:
        logger.error(f"[GMPCollector Error] {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    collect_gmp()
