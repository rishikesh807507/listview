import logging
from datetime import datetime
from backend.database import SessionLocal
from backend.models import Stock, StockPrice

logger = logging.getLogger("HistoricalCollector")

def collect_historical():
    """
    Appends today's closing price to local historical stock_prices table,
    gradually expanding the self-hosted historical database.
    """
    db = SessionLocal()
    try:
        stocks = db.query(Stock).all()
        today = datetime.utcnow().date()
        today_dt = datetime(today.year, today.month, today.day)
        
        saved = 0
        for s in stocks:
            existing = db.query(StockPrice).filter(
                StockPrice.symbol == s.symbol,
                StockPrice.timestamp == today_dt
            ).first()
            
            if not existing and s.current_price > 0:
                p = StockPrice(
                    symbol=s.symbol,
                    exchange=s.exchange,
                    timestamp=today_dt,
                    open=s.current_price - s.change,
                    high=max(s.current_price, s.current_price - s.change),
                    low=min(s.current_price, s.current_price - s.change),
                    close=s.current_price,
                    volume=s.volume,
                    source="scheduled_collector",
                    created_at=datetime.utcnow()
                )
                db.add(p)
                saved += 1
        db.commit()
        print(f"[HistoricalCollector] Recorded {saved} daily snapshots.")
    except Exception as e:
        print(f"[HistoricalCollector Error] {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    collect_historical()
